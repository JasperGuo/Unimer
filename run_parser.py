# coding=utf-8

import re
import os
import json
import copy
import random
import torch
import itertools
from typing import Dict, Any
from overrides import overrides
from absl import app
from absl import flags
import numpy as np
import torch
import torch.optim as optim
from torch.optim.lr_scheduler import MultiStepLR
from allennlp.data.iterators import BucketIterator
from allennlp.training.util import evaluate as model_evaluate
from allennlp.data.vocabulary import Vocabulary
from allennlp.training.learning_rate_schedulers import LearningRateScheduler, NoamLR
from allennlp.data.tokenizers import WordTokenizer
from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter
from grammars.grammar import get_grammar
from grammars.entity_matcher import get_entity_matcher, get_seq2seq_entity_matcher
from grammars.gnn_entity_matcher import get_gnn_entity_replacer, get_gnn_entity_matcher
from grammars.utils import get_logical_form_preprocessor, get_logical_form_postprocessor,\
    get_logical_form_tokenizer, get_utterance_preprocessor
from data_readers.grammar_based_reader import GrammarBasedDataReader
from data_readers.grammar_copy_based_reader import GrammarCopyBasedDataReader
from data_readers.seq2seq_data_reader import Seq2SeqDataReader
from data_readers.gnn_data_reader import GNNCopyTransformerDataReader
from model_builder import build_grammar_model, get_predictor, build_seq2seq_model, build_parsing_seq2seq_model, \
    build_grammar_copy_model, build_grammar_copy_model_2, build_parsing_recombination_seq2seq_model,\
    build_parsing_recombination_seq2seq_copy_model, build_gnn_parsing_model, build_gnn_parsing_model2
from custom_trainer import CustomTrainer
from lr_scheduler_wrapper import PyTorchMultiStepLearningRateSchedulerWrapper
import evaluations


flags.DEFINE_bool('do_train', False, 'whether to do training')
flags.DEFINE_integer('seed', 100, 'random seed')

# Model Type
flags.DEFINE_enum(
    'model', 'parsing',
    ['parsing', 'copy_parsing', 'copy_parsing_2',
     'seq_parsing', 'recombination_seq_parsing',
     'recombination_copy_seq_parsing',
     'translation', 'gnn_parsing', 'gnn_parsing2'],
    'Specifying parsing models and translation models'
)

# Data
flags.DEFINE_enum('task', 'geo', ['geo', 'atis', 'job'], 'task')
flags.DEFINE_string('train_data', os.path.join(
    'data', 'geo', 'geo_prolog_train.tsv'), 'training data path')
flags.DEFINE_string('test_data', os.path.join(
    'data', 'geo', 'geo_prolog_test.tsv'), 'training data path')
flags.DEFINE_enum('language', 'prolog', [
                  'funql', 'typed_funql', 'prolog', 'prolog2', 'lambda',
                  'lambda2', 'lambda3', 'lambda4', 'sql', 'sql2', 'sql3'], 'target language to generate')
flags.DEFINE_integer('min_count', 1, 'Minimum counts for vocabulary')

# Model Hyper-parameters
flags.DEFINE_integer('source_embedding_dim', 128, 'Embedding size of source')
flags.DEFINE_integer('encoder_hidden_dim', 128, 'Hidden size of lstm encoder')
flags.DEFINE_bool('encoder_bidirectional', True,
                  'Whether to use birdirectional lstm')
flags.DEFINE_float('encoder_output_dropout', 0.2,
                   'Input dropout rate of encoder')
flags.DEFINE_float('encoder_input_dropout', 0.2,
                   'Output dropout rate of encoder')

# Grammar Decoder
flags.DEFINE_integer('target_embedding_dim', 128, 'Hidden size of lstm decoder')
flags.DEFINE_integer('decoder_hidden_dim', 128, 'Hidden size of lstm decoder')
flags.DEFINE_integer('decoder_num_layers', 1, 'Number of layers in decoder')
flags.DEFINE_integer('rule_embedding_dim', 64, 'Embedding size of rule')
flags.DEFINE_integer('nonterminal_embedding_dim', 64,
                     'Embedding size of non-terminal')
flags.DEFINE_integer('max_decode_length', 100, 'Maximum decode steps')
flags.DEFINE_integer('attention_hidden_dim', 100, 'Attention hidden dim for Bilinear Attention')
flags.DEFINE_float('dropout', 0.2, 'Dropout rate')

# GNN Hyperparameters
flags.DEFINE_integer('transformer_encoder_hidden_dim', 128, 'hidden dimension of encoder of transformer')
flags.DEFINE_integer('transformer_decoder_hidden_dim', 128, 'hidden dimension of decoder of transformer')
flags.DEFINE_integer('transformer_encoder_nhead', 128, 'number of head in self attention')
flags.DEFINE_integer('transformer_decoder_nhead', 128, 'number of head in self attention')
flags.DEFINE_integer('transformer_num_encoder_layers', 3, 'number of encoder layer in transformer')
flags.DEFINE_integer('transformer_num_decoder_layers', 3, 'number of decoder layer in transformer')
flags.DEFINE_integer('transformer_encoder_feedforward_dim', 256, 'dimension of feed forward layer in transformer')
flags.DEFINE_integer('transformer_decoder_feedforward_dim', 256, 'dimension of feed forward layer in transformer')
flags.DEFINE_integer('gnn_transformer_num_edge_labels', 20, 'number of edge labels in gnn transformer')
flags.DEFINE_bool('gnn_encode_edge_label_with_matrix', True, 'whether to encode edge label with matrix')
flags.DEFINE_integer('gnn_relative_position_clipped_range', 8, 'clip distance of relative position representations')
flags.DEFINE_integer('gnn_max_decode_clip_range', 8, 'clip distance of decode sequence')

# Optimization
flags.DEFINE_bool('use_scheduler', False, 'whether to use learning rate scheduler')
flags.DEFINE_float('lr', 0.001, 'learning rate')
flags.DEFINE_enum('optimizer', 'adam', [
                  'adam', 'sgd', 'rmsprop', 'adadelta'], 'optimizer to use')
flags.DEFINE_integer('warmup_steps', 800, 'number of steps to increase learning rate')
flags.DEFINE_float('adam_beta_1', 0.9, 'hyper-parameter beta_1 of adam')
flags.DEFINE_float('adam_beta_2', 0.999, 'hyper-parameter beta_2 of adam')
flags.DEFINE_float('adam_eps', 1e-8, 'hyper-parameter epsilon of adam')
flags.DEFINE_enum('scheduler', 'noam', ['noam', 'bert', 'finetune_bert_noam'], 'scheduler for transformer based models')
flags.DEFINE_integer('batch_size', 32, 'batch size')
flags.DEFINE_integer(
    'patient', 10, 'Number of epochs to be patient before early stopping')
flags.DEFINE_integer('epoch', 1, 'Number of epoch to train')
flags.DEFINE_integer('model_save_interval', 1, 'Interval to save model')
flags.DEFINE_float('gradient_clip', 5.0, 'Clip gradient')
flags.DEFINE_string('validation_metric', '+accuracy', 'validation metric')

# Utils
flags.DEFINE_string('serialization_dir', os.path.join(
    'trained_models', 'geo'), 'Path to save trained models')

# Evaluation
flags.DEFINE_bool('save_prediction_result', False,
                  'Whether to save prediction result')
flags.DEFINE_string('checkpoint', 'best.th', 'Checkpoint to evaluate')
flags.DEFINE_integer('beam_size', 1, 'Beam Search Size')


FLAGS = flags.FLAGS


def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    # Seed all GPUs with the same seed if available.
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def save_flags(FLAGs):
    with open(os.path.join(FLAGS.serialization_dir, 'config.txt'), 'w') as f:
        f.write(FLAGS.flags_into_string())


def build_data_reader(FLAGS):
    splitter = SpacyWordSplitter(pos_tags=True)
    question_tokenizer = WordTokenizer(SpacyWordSplitter(pos_tags=True))
    reader = None
    if FLAGS.model == 'parsing':
        # Parsing
        grammar = get_grammar(FLAGS.task, FLAGS.language)
        assert grammar is not None
        logical_form_preprocessor = get_logical_form_preprocessor(
            FLAGS.task, FLAGS.language)
        if FLAGS.do_train:
            max_target_length = FLAGS.max_decode_length
        else:
            max_target_length = 0
        reader = GrammarBasedDataReader(
            question_tokenizer, grammar, logical_form_preprocessor=logical_form_preprocessor,
            maximum_target_length=max_target_length)
    elif FLAGS.model in ['copy_parsing', 'copy_parsing_2']:
        # Parsing
        grammar = get_grammar(FLAGS.task, FLAGS.language)
        assert grammar is not None
        logical_form_preprocessor = get_logical_form_preprocessor(
            FLAGS.task, FLAGS.language)
        if FLAGS.do_train:
            max_target_length = FLAGS.max_decode_length
        else:
            max_target_length = 0
        entity_matcher = get_entity_matcher(FLAGS.task, FLAGS.language)
        utterance_preprocessor = get_utterance_preprocessor(FLAGS.task, FLAGS.language)
        reader = GrammarCopyBasedDataReader(
            question_tokenizer, grammar, logical_form_preprocessor=logical_form_preprocessor,
            utterance_preprocessor=utterance_preprocessor,
            copy_link_finder=entity_matcher, maximum_target_length=max_target_length)
    elif FLAGS.model == 'translation':
        # Translation
        logical_form_tokenizer = get_logical_form_tokenizer(FLAGS.task, FLAGS.language)
        reader = Seq2SeqDataReader(
            question_tokenizer=question_tokenizer,
            logical_form_tokenizer=logical_form_tokenizer,
            is_parsing=False)
        return reader
    elif FLAGS.model == 'seq_parsing':
        # Parsing without grammar
        logical_form_tokenizer = get_logical_form_tokenizer(FLAGS.task, FLAGS.language)
        reader = Seq2SeqDataReader(
            question_tokenizer=question_tokenizer,
            logical_form_tokenizer=logical_form_tokenizer,
            is_parsing=True)
    elif FLAGS.model == 'recombination_seq_parsing':
        logical_form_preprocessor = get_logical_form_preprocessor(
            FLAGS.task, FLAGS.language, normalize_var_with_de_brujin_index=True)
        logical_form_tokenizer = get_logical_form_tokenizer(FLAGS.task, FLAGS.language)
        if FLAGS.do_train:
            max_target_length = FLAGS.max_decode_length
        else:
            max_target_length = 0
        reader = Seq2SeqDataReader(
            question_tokenizer=question_tokenizer,
            logical_form_tokenizer=logical_form_tokenizer,
            logical_form_preprocessor=logical_form_preprocessor,
            is_parsing=True,
            maximum_target_length=max_target_length
        )
        return reader
    elif FLAGS.model == 'recombination_copy_seq_parsing':
        logical_form_preprocessor = get_logical_form_preprocessor(
            FLAGS.task, FLAGS.language, normalize_var_with_de_brujin_index=True)
        logical_form_tokenizer = get_logical_form_tokenizer(FLAGS.task, FLAGS.language)
        if FLAGS.do_train:
            max_target_length = FLAGS.max_decode_length
        else:
            max_target_length = 0
        entity_matcher = get_seq2seq_entity_matcher(FLAGS.task, FLAGS.language)
        if FLAGS.language.startswith('sql'):
            exclude_target_words = ['select', 'from', 'and', 'in', 'where', 'group', 'order', 'having', 'limit', 'not']
        else:
            exclude_target_words = None
        reader = Seq2SeqDataReader(
            question_tokenizer=question_tokenizer,
            logical_form_tokenizer=logical_form_tokenizer,
            logical_form_preprocessor=logical_form_preprocessor,
            is_parsing=True,
            enable_copy=True,
            maximum_target_length=max_target_length,
            entity_matcher=entity_matcher,
            exclude_target_words=exclude_target_words
        )
        return reader
    elif FLAGS.model in ['gnn_parsing', 'gnn_parsing2']:
        logical_form_preprocessor = get_logical_form_preprocessor(
            FLAGS.task, FLAGS.language, normalize_var_with_de_brujin_index=True)
        logical_form_tokenizer = get_logical_form_tokenizer(FLAGS.task, FLAGS.language)
        if FLAGS.do_train:
            max_target_length = FLAGS.max_decode_length
            allow_drop = True
        else:
            max_target_length = 0
            allow_drop = False
        grammar = get_grammar(FLAGS.task, FLAGS.language)
        entity_matcher = get_gnn_entity_matcher(FLAGS.task, FLAGS.language)
        entity_replacer = get_gnn_entity_replacer(FLAGS.task, FLAGS.language)
        reader = GNNCopyTransformerDataReader(
            entity_matcher=entity_matcher,
            entity_replacer=entity_replacer,
            target_grammar=grammar,
            source_tokenizer=question_tokenizer,
            target_tokenizer=logical_form_tokenizer,
            logical_form_preprocessor=logical_form_preprocessor,
            relative_position_clipped_range=FLAGS.gnn_relative_position_clipped_range,
            nlabels=FLAGS.gnn_transformer_num_edge_labels,
            allow_drop=allow_drop
        )
        return reader

    return reader


def build_optimizer(FLAGS, parameters) -> optim.Optimizer:
    if FLAGS.optimizer == 'adam':
        optimizer = optim.Adam(parameters, lr=FLAGS.lr)
    elif FLAGS.optimizer == 'sgd':
        optimizer = optim.SGD(parameters, lr=FLAGS.lr, momentum=0,
                              dampening=0, weight_decay=0, nesterov=False)
    elif FLAGS.optimizer == 'rmsprop':
        optimizer = optim.RMSprop(parameters, lr=FLAGS.lr, alpha=0.95)
    elif FLAGS.optimizer == 'adadelta':
        optimizer = optim.Adadelta(parameters, lr=FLAGS.lr)
    else:
        optimizer = None
    return optimizer


def build_lr_scheduler(FLAGS, optimizer) -> LearningRateScheduler:
    if not FLAGS.use_scheduler:
        return None
    allen_scheduler = None
    if FLAGS.optimizer == 'rmsprop':
        scheduler = MultiStepLR(optimizer, milestones=[5] + list(range(6, 200)), gamma=0.98)
        allen_scheduler = PyTorchMultiStepLearningRateSchedulerWrapper(scheduler)
    elif FLAGS.optimizer == 'sgd':
        scheduler = MultiStepLR(optimizer, milestones=[15, 20, 25, 30], gamma=0.5)
        allen_scheduler = PyTorchMultiStepLearningRateSchedulerWrapper(scheduler)
    elif FLAGS.optimizer == 'adam':
        if FLAGS.scheduler == 'noam':
            print('Use Noam Scheduler')
            allen_scheduler = NoamLR(optimizer, model_size=FLAGS.transformer_encoder_hidden_dim,
                                     warmup_steps=FLAGS.warmup_steps)
    return allen_scheduler


def main(argv):
    set_random_seed(FLAGS.seed)
    print(FLAGS.flags_into_string())
    reader = build_data_reader(FLAGS)
    assert reader is not None

    if FLAGS.do_train:
        is_test = False
        save_flags(FLAGS)
        train_dataset, test_dataset = reader.read(
            FLAGS.train_data), reader.read(FLAGS.test_data)
        vocab = Vocabulary.from_instances(
            train_dataset, min_count={'source_tokens': FLAGS.min_count})
    else:
        is_test = True
        test_dataset = reader.read(FLAGS.test_data)
        vocab = Vocabulary.from_files(os.path.join(
            FLAGS.serialization_dir, 'vocabulary'))

    if FLAGS.model == 'parsing':
        model = build_grammar_model(FLAGS, reader, vocab, reader.grammar)
    elif FLAGS.model == 'copy_parsing':
        model = build_grammar_copy_model(FLAGS, reader, vocab, reader.grammar)
    elif FLAGS.model == 'copy_parsing_2':
        model = build_grammar_copy_model_2(FLAGS, reader, vocab, reader.grammar)
    elif FLAGS.model == 'translation':
        model = build_seq2seq_model(FLAGS, reader, vocab)
    elif FLAGS.model == 'recombination_seq_parsing':
        model = build_parsing_recombination_seq2seq_model(FLAGS, reader, vocab)
    elif FLAGS.model == 'recombination_copy_seq_parsing':
        model = build_parsing_recombination_seq2seq_copy_model(FLAGS, reader, vocab)
    elif FLAGS.model == 'gnn_parsing':
        model = build_gnn_parsing_model(FLAGS, reader, vocab, is_test=not FLAGS.do_train)
    elif FLAGS.model == 'gnn_parsing2':
        model = build_gnn_parsing_model2(FLAGS, reader, vocab, is_test=not FLAGS.do_train)
    else:
        model = build_parsing_seq2seq_model(FLAGS, reader, vocab)

    print(model)
    assert model is not None

    print("Cuda Available: ", torch.cuda.is_available())
    if torch.cuda.is_available():
        cuda_device = list(range(torch.cuda.device_count()))
        print("Cuda device: ", cuda_device)
        if len(cuda_device) > 1:
            print("Enable Multiple GPU: ", cuda_device)
            # Enable Multiple GPU
            model = model.cuda(cuda_device[0])
        else:
            cuda_device = cuda_device[0]
            model = model.cuda(cuda_device)
    else:
        cuda_device = -1

    if FLAGS.do_train:
        with torch.autograd.set_detect_anomaly(False):
            model.train()

            optimizer = build_optimizer(FLAGS, model.parameters())
            assert optimizer is not None

            allen_scheduler = build_lr_scheduler(FLAGS, optimizer)

            vocab.save_to_files(os.path.join(
                FLAGS.serialization_dir, 'vocabulary'))
            iterator = BucketIterator(batch_size=FLAGS.batch_size, sorting_keys=[
                                      ("source_tokens", "num_tokens")])
            iterator.index_with(vocab)
            trainer = CustomTrainer(model=model,
                                    optimizer=optimizer,
                                    iterator=iterator,
                                    train_dataset=train_dataset,
                                    validation_dataset=test_dataset,
                                    patience=FLAGS.patient,
                                    num_epochs=FLAGS.epoch,
                                    cuda_device=cuda_device,
                                    serialization_dir=FLAGS.serialization_dir,
                                    grad_clipping=FLAGS.gradient_clip,
                                    validation_metric=FLAGS.validation_metric,
                                    should_log_learning_rate=True,
                                    summary_interval=5,
                                    num_serialized_models_to_keep=5,
                                    learning_rate_scheduler=allen_scheduler,
                                    loss_fn=None)
            trainer.train()
    else:
        # Load Model
        with open(os.path.join(FLAGS.serialization_dir, FLAGS.checkpoint), 'rb') as f:
            model.load_state_dict(torch.load(f))
        model.eval()

        iterator = BucketIterator(batch_size=FLAGS.batch_size, sorting_keys=[
                                  ("source_tokens", "num_tokens")])
        iterator.index_with(vocab)

        metrics = model_evaluate(
            model, test_dataset, iterator, cuda_device, batch_weight_key='')
        for key, metric in metrics.items():
            print("%s: %s" % (key, str(metric)))

        if FLAGS.save_prediction_result:
            results = list()
            predictor = get_predictor(model, reader)

            total, correct = 0, 0
            preprocessor = get_logical_form_preprocessor(FLAGS.task, FLAGS.language)
            postprocessor = get_logical_form_postprocessor(
                FLAGS.task, FLAGS.language)
            for idx in itertools.islice(range(len(test_dataset)), 0, len(test_dataset), FLAGS.batch_size):
                instances = test_dataset[idx:idx + FLAGS.batch_size]
                total += len(instances)
                predictions = predictor.predict_batch_instance(instances)
                for inst, pred in zip(instances, predictions):
                    if FLAGS.model == 'parsing':
                        is_correct, result = evaluations.evaluate_grammar_based_prediction(
                            inst, pred, reader.grammar, preprocessor, postprocessor)
                    elif FLAGS.model in ['copy_parsing', 'copy_parsing_2']:
                        is_correct, result = evaluations.evaluate_grammar_copy_based_prediction(
                            inst, pred, reader.grammar, preprocessor, postprocessor)
                    elif FLAGS.model in ['seq_parsing', 'recombination_seq_parsing']:
                        is_correct, result = evaluations.evaluate_seq_parsing_prediction(
                            inst, pred, FLAGS.language)
                    elif FLAGS.model in ['recombination_copy_seq_parsing']:
                        is_correct, result = evaluations.evaluate_seq_copy_parsing_prediction(
                            inst, pred, FLAGS.language
                        )
                    elif FLAGS.model in ['gnn_parsing', 'gnn_parsing2']:
                        is_correct, result = evaluations.evaluate_gnn_parsing_prediction(
                            inst, pred, FLAGS.language
                        )
                    else:
                        # Translation
                        is_correct, result = evaluations.evaluate_translation_prediction(
                            inst, pred, FLAGS.language)
                    if is_correct:
                        correct += 1
                    results.append(result)

            assert total == len(test_dataset)
            print('Total: %d, Correct: %d, Accuracy: %f' %
                  (total, correct, correct / total))
            with open(os.path.join(FLAGS.serialization_dir, 'predictions.json'), 'w') as f:
                f.write(json.dumps(results, indent=4))


if __name__ == '__main__':
    app.run(main)
