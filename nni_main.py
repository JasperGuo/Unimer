# coding=utf-8

import os
import re
import time
import json
import shutil
import subprocess
from absl import app
from absl import flags
from pprint import pprint
import nni

# Data
flags.DEFINE_integer('cuda_device', 0, 'cuda_device')
flags.DEFINE_string('train_data', os.path.join('data', 'geo', 'geo_funql_train.tsv'), 'training data path')
flags.DEFINE_string('test_data', os.path.join('data', 'geo', 'geo_funql_test.tsv'), 'testing data path')
flags.DEFINE_enum('language', 'funql', ['funql', 'prolog', 'lambda', 'sql'], 'target language to generate')
flags.DEFINE_string('basepath', 'model', 'basepath to store models')

FLAGS = flags.FLAGS

PATTERN = re.compile('metrics_epoch_(\d+).json')


def main(argv):
    # basepath
    base_path = FLAGS.basepath
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    # model path
    save_path = os.path.join(base_path, '%s_model' % str(time.time()))
    os.mkdir(save_path)

    params = nni.get_next_parameter()
    source_embedding_dim = params['encoder_hidden_dim'] * 2
    encoder_hidden_dim = params['encoder_hidden_dim']
    encoder_input_dropout = params['encoder_input_dropout']
    encoder_output_dropout = params['encoder_output_dropout']
    decoder_hidden_dim = params['encoder_hidden_dim'] * 2
    decoder_num_layers = params['decoder_num_layers']
    rule_embedding_dim = params['rule_embedding_dim']
    nonterminal_embedding_dim = params['nonterminal_embedding_dim']
    dropout = params['decoder_dropout']
    batch_size = params['batch_size']
    lr = params['lr']

    command = '''CUDA_VISIBLE_DEVICES=%d python run_parser.py --do_train=True \
        --source_embedding_dim=%d \
        --encoder_hidden_dim=%d \
        --encoder_bidirectional=True \
        --encoder_input_dropout=%f \
        --encoder_output_dropout=%f \
        --decoder_hidden_dim=%d \
        --decoder_num_layers=%d \
        --rule_embedding_dim=%d \
        --nonterminal_embedding_dim=%d \
        --max_decode_length=200 \
        --serialization_dir=%s \
        --seed=1 \
        --dropout=%f \
        --task=geo \
        --language=%s \
        --train_data=%s \
        --test_data=%s \
        --batch_size=%d \
        --lr=%f \
        --patient=30 \
        --optimizer=adam \
        --epoch=50 \
        --model_save_interval=1 \
        --gradient_clip=5 \ ''' % (FLAGS.cuda_device, source_embedding_dim, encoder_hidden_dim, encoder_input_dropout, encoder_output_dropout,
                                   decoder_hidden_dim, decoder_num_layers, rule_embedding_dim, nonterminal_embedding_dim, save_path,
                                   dropout, FLAGS.language, FLAGS.train_data, FLAGS.test_data, batch_size, lr)

    command = re.sub('\s+', ' ', command).strip()
    subprocess.call(command, shell=True)

    last_epoch = 0
    for f in os.listdir(save_path):
        if f.startswith('metrics_epoch_'):
            match = PATTERN.match(f)
            if match:
                epoch = int(match.group(1))
                if epoch > last_epoch:
                    last_epoch = epoch
    file_path = os.path.join(save_path, 'metrics_epoch_%d.json' % last_epoch)
    with open(file_path, 'r') as f:
        metrics = json.load(f)
        accuracy = metrics['best_validation_accuracy']
        nni.report_final_result(accuracy)


if __name__ == '__main__':
    app.run(main)
