# codint=uf8

import re


def read_logical_forms(path):
    ql_dict = dict()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            ql_dict[splits[0]] = splits[1]
    return ql_dict


def process_prolog_denotation(denotation):
    assert denotation[0] == '[' and denotation[-1] == ']'
    values = denotation[1:-1].split(',')
    processed_values = list()
    for v in values:
        if len(v) == 0:
            continue
        processed_values.append(v)
    return sorted(processed_values)


def process_funql_denotation(denotation):
    assert denotation[0] == '[' and denotation[-1] == ']'
    if '(' in denotation:
        values = denotation[1:-1].split('),')
    else:
        values = denotation[1:-1].split(',')
    processed_values = list()
    for v in values:
        if len(v) == 0:
            continue
        nv = re.sub(r'.*\((.*),\s*[a-z|\_]+\)', r'\1', v)
        nv = re.sub(r'.*\((.*),\s*[a-z|\_]+', r'\1', nv)
        nv = re.sub(r'.*\((.*)\)', r'\1', nv)
        nv = re.sub(r'.*\((.*)', r'\1', nv)
        processed_values.append(nv)
    return sorted(processed_values)


def read_denotations(path, denotation_process_func):
    questions, denotations = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            questions.append(splits[0])
            # print(splits[1])
            d = denotation_process_func(splits[1])
            denotations.append(d)
    return questions, denotations


def compare(prolog_data_path, prolog_path, funql_data_path, funql_path):
    prolog_dict, funql_dict = read_logical_forms(
        prolog_data_path), read_logical_forms(funql_data_path)
    prolog_questions, prolog_denotations = read_denotations(
        prolog_path, process_prolog_denotation)
    funql_questions, funql_denotations = read_denotations(
        funql_path, process_funql_denotation)
    total, same = 0, 0
    for pq, pd in zip(prolog_questions, prolog_denotations):
        pq_1 = pq[: -1].lower().strip()
        funql_idx = funql_questions.index(pq_1)
        fd = funql_denotations[funql_idx]
        if pd == fd:
            same += 1
        else:
            print(pq)
            print(prolog_dict[pq])
            print(pd)
            print(funql_dict[pq_1.strip()])
            print(fd)
            print("===\n\n")
        total += 1
    print(total, same)


if __name__ == '__main__':
    compare('../data/geo/geo_prolog_test_v2.tsv', './prolog_execution_results.tsv',
            '../data/geo/geo_funql_test.tsv', './funql_execution_results.tsv')
