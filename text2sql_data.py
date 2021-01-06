# coding=utf8
"""
Parsing data from https://github.com/jkkummerfeld/text2sql-data/tree/master/data
"""

import os
import json
import copy


def get_sql_data(basepath, raw_data_path):
    with open(raw_data_path, 'r') as f:
        data = json.load(f)
    question_based_train_dataset, question_based_dev_dataset, question_based_test_dataset = list(), list(), list()
    query_based_train_dataset, query_based_dev_dataset, query_based_test_dataset = list(), list(), list()
    for d in data:
        sql = d['sql'][0]
        sentences = d['sentences']
        for s_dict in sentences:
            s = s_dict['text']
            _sql = copy.copy(sql)

            for name in s_dict['variables']:
                value = s_dict['variables'][name]
                if len(value) == 0:
                    for variable in d['variables']:
                        if variable['name'] == name:
                            value = variable['example']
                s = value.join(s.split(name))
                _sql = value.join(_sql.split(name))

            if s_dict['question-split'] == 'test':
                question_based_test_dataset.append("%s\t%s" % (s, _sql))
            elif s_dict['question-split'] == 'dev':
                question_based_dev_dataset.append("%s\t%s" % (s, _sql))
            else:
                question_based_train_dataset.append("%s\t%s" % (s, _sql))

            if d['query-split'] == 'test':
                query_based_test_dataset.append("%s\t%s" % (s, _sql))
            elif d['query-split'] == 'dev':
                query_based_dev_dataset.append("%s\t%s" % (s, _sql))
            else:
                query_based_train_dataset.append("%s\t%s" % (s, _sql))

    save_train_path, save_dev_path, save_test_path = os.path.join(base_path, 'atis_sql_question_based_train_2018.tsv'), \
        os.path.join(basepath, 'atis_sql_question_based_dev_2018.tsv'), \
        os.path.join(base_path, 'atis_sql_question_based_test_2018.tsv')
    with open(save_train_path, 'w') as f:
        f.write('\n'.join(question_based_train_dataset))
    with open(save_dev_path, 'w') as f:
        f.write('\n'.join(question_based_dev_dataset))
    with open(save_test_path, 'w') as f:
        f.write('\n'.join(question_based_test_dataset))

    save_train_path, save_dev_path, save_test_path = os.path.join(base_path, 'atis_sql_query_based_train_2018.tsv'), \
        os.path.join(base_path, 'atis_sql_query_based_dev_2018.tsv'), \
        os.path.join(base_path, 'atis_sql_query_based_test_2018.tsv')
    with open(save_train_path, 'w') as f:
        f.write('\n'.join(query_based_train_dataset))
    with open(save_dev_path, 'w') as f:
        f.write('\n'.join(query_based_dev_dataset))
    with open(save_test_path, 'w') as f:
        f.write('\n'.join(query_based_test_dataset))


if __name__ == '__main__':
    base_path = os.path.join('data', 'atis')
    raw_data_path = os.path.join('data', 'atis', 'atis.json')
    get_sql_data(base_path, raw_data_path)
