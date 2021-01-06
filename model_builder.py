# coding=utf8

import numpy
import torch
from typing import Dict, List, Callable
from overrides import overrides
from allennlp.modules.seq2seq_encoders import PytorchSeq2SeqWrapper
from allennlp.training.metrics import Metric
from allennlp.models.model import Model
from allennlp.data.vocabulary import Vocabulary
from allennlp.modules import Embedding
from allennlp.data.dataset_readers import DatasetReader
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder
from allennlp.models.encoder_decoders.simple_seq2seq import SimpleSeq2Seq
from allennlp.modules.attention import BilinearAttention, DotProductAttention
from allennlp.predictors import Seq2SeqPredictor
from allennlp.common import Params
from allennlp.nn import Activation, InitializerApplicator

from grammars.grammar import Grammar
from grammars.parse_ast import AST
from neural_models.seq2seq_model import Seq2SeqModel
from neural_models.recombination_seq2seq import RecombinationSeq2Seq
from neural_models.recombination_seq2seq_copy import RecombinationSeq2SeqWithCopy
from neural_models.grammar_based_models import GrammarModel
from neural_models.modules.grammar_decoder import LSTMGrammarDecoder
from neural_models.modules.grammar_copy_decoder import LSTMGrammarCopyDecoder
from neural_models.modules.grammar_copy_decoder_2 import LSTMGrammarCopyDecoder as LSTMGrammarCopyDecoder2
from neural_models.GNN import GNNCopyTransformer
from neural_models.GNN2 import GNNCopyTransformer2
from metrics.sequency_accuracy import SequenceAccuracy


def get_predictor(model, reader) -> Seq2SeqPredictor:
    return Seq2SeqPredictor(model=model, dataset_reader=reader)


def build_grammar_model(
        flags,
        data_reader: DatasetReader,
        vocab: Vocabulary,
        grammar: Grammar,
        source_namespace: str = 'source_tokens',
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    lstm_encoder = PytorchSeq2SeqWrapper(
        torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                      bidirectional=flags.encoder_bidirectional))
    decoder = LSTMGrammarDecoder(grammar, AST, lstm_hidden_dim=flags.decoder_hidden_dim,
                                 num_lstm_layers=flags.decoder_num_layers,
                                 rule_pad_index=data_reader.rule_pad_index, rule_embedding_dim=flags.rule_embedding_dim,
                                 nonterminal_pad_index=data_reader.nonterminal_pad_index,
                                 nonterminal_end_index=data_reader.nonterminal_end_index,
                                 nonterminal_embedding_dim=flags.nonterminal_embedding_dim,
                                 source_encoding_dim=flags.encoder_hidden_dim * 2,
                                 dropout=flags.dropout, max_target_length=flags.max_decode_length)
    metric = SequenceAccuracy()
    model = GrammarModel(vocab, source_embedder, lstm_encoder,
                         decoder, metric, flags, regularizer=None)
    return model


def build_grammar_copy_model(
        flags,
        data_reader: DatasetReader,
        vocab: Vocabulary,
        grammar: Grammar,
        source_namespace: str = 'source_tokens',
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    lstm_encoder = PytorchSeq2SeqWrapper(
        torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                      bidirectional=flags.encoder_bidirectional))
    decoder = LSTMGrammarCopyDecoder(grammar, AST, lstm_hidden_dim=flags.decoder_hidden_dim,
                                     num_lstm_layers=flags.decoder_num_layers,
                                     rule_pad_index=data_reader.rule_pad_index,
                                     rule_embedding_dim=flags.rule_embedding_dim,
                                     nonterminal_pad_index=data_reader.nonterminal_pad_index,
                                     nonterminal_end_index=data_reader.nonterminal_end_index,
                                     nonterminal_embedding_dim=flags.nonterminal_embedding_dim,
                                     source_encoding_dim=flags.encoder_hidden_dim * 2,
                                     dropout=flags.dropout, max_target_length=flags.max_decode_length)
    metric = SequenceAccuracy()
    model = GrammarModel(vocab, source_embedder, lstm_encoder,
                         decoder, metric, flags, regularizer=None)
    return model


def build_grammar_copy_model_2(
        flags,
        data_reader: DatasetReader,
        vocab: Vocabulary,
        grammar: Grammar,
        source_namespace: str = 'source_tokens',
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    lstm_encoder = PytorchSeq2SeqWrapper(
        torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                      bidirectional=flags.encoder_bidirectional))
    decoder = LSTMGrammarCopyDecoder2(grammar, AST, lstm_hidden_dim=flags.decoder_hidden_dim,
                                      num_lstm_layers=flags.decoder_num_layers,
                                      rule_pad_index=data_reader.rule_pad_index,
                                      rule_embedding_dim=flags.rule_embedding_dim,
                                      nonterminal_pad_index=data_reader.nonterminal_pad_index,
                                      nonterminal_end_index=data_reader.nonterminal_end_index,
                                      nonterminal_embedding_dim=flags.nonterminal_embedding_dim,
                                      source_encoding_dim=flags.encoder_hidden_dim * 2,
                                      dropout=flags.dropout, max_target_length=flags.max_decode_length)
    metric = SequenceAccuracy()
    model = GrammarModel(vocab, source_embedder, lstm_encoder,
                         decoder, metric, flags, regularizer=None)
    return model


def build_parsing_seq2seq_model(
        flags,
        data_reader,
        vocab: Vocabulary,
        source_namespace: str = 'source_tokens',
        target_namespace: str = 'target_tokens'
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    lstm_encoder = PytorchSeq2SeqWrapper(
        torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                      bidirectional=flags.encoder_bidirectional))
    attention = DotProductAttention()
    metric = SequenceAccuracy()
    model = Seq2SeqModel(vocab, source_embedder, lstm_encoder, flags.max_decode_length,
                         target_embedding_dim=flags.decoder_hidden_dim,
                         target_namespace=target_namespace,
                         attention=attention,
                         beam_size=flags.beam_size,
                         use_bleu=False,
                         seq_metrics=metric)
    return model


def build_parsing_recombination_seq2seq_model(
        flags,
        data_reader,
        vocab: Vocabulary,
        source_namespace: str = 'source_tokens',
        target_namespace: str = 'target_tokens'
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    lstm = PytorchSeq2SeqWrapper(torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                                               bidirectional=flags.encoder_bidirectional))
    attention = BilinearAttention(flags.attention_hidden_dim, flags.attention_hidden_dim)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    initializer = InitializerApplicator.from_params([(".*bias", Params({"type": "constant", "val": 0})),
                                                     ('.*', Params({"type": "uniform", "a": -0.1, "b": 0.1}))])
    metric = SequenceAccuracy()
    model = RecombinationSeq2Seq(vocab, source_embedder, lstm, flags.max_decode_length,
                                 seq_metrics=metric,
                                 target_embedding_dim=flags.target_embedding_dim,
                                 target_namespace=target_namespace,
                                 output_attention=attention,
                                 beam_size=flags.beam_size,
                                 use_bleu=False,
                                 encoder_input_dropout=flags.encoder_input_dropout,
                                 encoder_output_dropout=flags.encoder_output_dropout,
                                 dropout=flags.dropout,
                                 feed_output_attention_to_decoder=True,
                                 keep_decoder_output_dim_same_as_encoder=True,
                                 initializer=initializer)
    return model


def build_parsing_recombination_seq2seq_copy_model(
    flags,
    data_reader,
    vocab: Vocabulary,
    source_namespace: str = 'source_tokens',
    target_namespace: str = 'target_tokens'
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    lstm = PytorchSeq2SeqWrapper(torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                                               bidirectional=flags.encoder_bidirectional))
    attention = BilinearAttention(flags.attention_hidden_dim, flags.attention_hidden_dim, normalize=False)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    initializer = InitializerApplicator.from_params([(".*bias", Params({"type": "constant", "val": 0})),
                                                     ('.*', Params({"type": "uniform", "a": -0.1, "b": 0.1}))])
    metric = SequenceAccuracy()
    model = RecombinationSeq2SeqWithCopy(vocab, source_embedder, lstm, flags.max_decode_length,
                                         seq_metrics=metric,
                                         source_namespace=source_namespace,
                                         target_namespace=target_namespace,
                                         target_embedding_dim=flags.target_embedding_dim,
                                         attention=attention,
                                         beam_size=flags.beam_size,
                                         use_bleu = False,
                                         encoder_input_dropout=flags.encoder_input_dropout,
                                         encoder_output_dropout=flags.encoder_output_dropout,
                                         dropout=flags.dropout,
                                         feed_output_attention_to_decoder=True,
                                         keep_decoder_output_dim_same_as_encoder=True,
                                         initializer=initializer)
    return model


def build_gnn_parsing_model(
    flags,
    data_reader: DatasetReader,
    vocab: Vocabulary,
    is_test: bool = False,
    source_namespace: str = 'source_tokens',
    target_namespace: str = 'target_tokens',
    segment_namespace: str = 'segment_tokens',
) -> Model:
    metric = SequenceAccuracy()
    model = GNNCopyTransformer(
        vocab=vocab,
        source_namespace=source_namespace,
        target_namespace=target_namespace,
        segment_namespace=segment_namespace,
        max_decoding_step=flags.max_decode_length,
        token_based_metric=metric,
        source_embedding_dim=flags.source_embedding_dim,
        target_embedding_dim=flags.target_embedding_dim,
        encoder_d_model=flags.transformer_encoder_hidden_dim,
        decoder_d_model=flags.transformer_decoder_hidden_dim,
        encoder_nhead=flags.transformer_encoder_nhead,
        decoder_nhead=flags.transformer_decoder_nhead,
        num_decoder_layers=flags.transformer_num_decoder_layers,
        num_encoder_layers=flags.transformer_num_encoder_layers,
        encoder_dim_feedforward=flags.transformer_encoder_feedforward_dim,
        decoder_dim_feedforward=flags.transformer_decoder_feedforward_dim,
        dropout=flags.dropout,
        beam_size=1,
        nlabels=flags.gnn_transformer_num_edge_labels,
        max_decode_clip_range=flags.gnn_max_decode_clip_range,
        encode_edge_label_with_matrix=flags.gnn_encode_edge_label_with_matrix,
        is_test=is_test
    )
    return model


def build_gnn_parsing_model2(
    flags,
    data_reader: DatasetReader,
    vocab: Vocabulary,
    is_test: bool = False,
    source_namespace: str = 'source_tokens',
    target_namespace: str = 'target_tokens',
    segment_namespace: str = 'segment_tokens',
) -> Model:
    metric = SequenceAccuracy()
    model = GNNCopyTransformer2(
        vocab=vocab,
        source_namespace=source_namespace,
        target_namespace=target_namespace,
        segment_namespace=segment_namespace,
        max_decoding_step=flags.max_decode_length,
        token_based_metric=metric,
        source_embedding_dim=flags.source_embedding_dim,
        target_embedding_dim=flags.target_embedding_dim,
        encoder_d_model=flags.transformer_encoder_hidden_dim,
        decoder_d_model=flags.transformer_decoder_hidden_dim,
        encoder_nhead=flags.transformer_encoder_nhead,
        decoder_nhead=flags.transformer_decoder_nhead,
        num_decoder_layers=flags.transformer_num_decoder_layers,
        num_encoder_layers=flags.transformer_num_encoder_layers,
        encoder_dim_feedforward=flags.transformer_encoder_feedforward_dim,
        decoder_dim_feedforward=flags.transformer_decoder_feedforward_dim,
        dropout=flags.dropout,
        beam_size=1,
        nlabels=flags.gnn_transformer_num_edge_labels,
        max_decode_clip_range=flags.gnn_max_decode_clip_range,
        encode_edge_label_with_matrix=flags.gnn_encode_edge_label_with_matrix,
        is_test=is_test
    )
    return model


def build_seq2seq_model(
        flags,
        data_reader,
        vocab: Vocabulary,
        source_namespace: str = 'source_tokens',
        target_namespace: str = 'target_tokens'
) -> Model:
    source_embedding = Embedding(vocab.get_vocab_size(namespace=source_namespace),
                                 embedding_dim=flags.source_embedding_dim)
    source_embedder = BasicTextFieldEmbedder({'tokens': source_embedding})
    lstm_encoder = PytorchSeq2SeqWrapper(
        torch.nn.LSTM(flags.source_embedding_dim, flags.encoder_hidden_dim, batch_first=True,
                      bidirectional=flags.encoder_bidirectional))
    attention = DotProductAttention()
    model = SimpleSeq2Seq(vocab, source_embedder, lstm_encoder, flags.max_decode_length,
                          target_embedding_dim=flags.decoder_hidden_dim,
                          target_namespace=target_namespace,
                          attention=attention,
                          beam_size=flags.beam_size,
                          use_bleu=True)
    return model
