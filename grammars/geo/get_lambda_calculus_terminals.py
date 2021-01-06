# coding=utf8

import re

state_pattern = re.compile('\s([a-z|_|.]+?:s)[\s|)]')
city_pattern = re.compile('\s([a-z|_|.]+?:c)[\s|)]')
river_pattern = re.compile('\s([a-z|_|.]+?:r)[\s|)]')
place_pattern = re.compile('\s([a-z|_|.]+?:p)[\s|)]')
lake_pattern = re.compile('\s([a-z|_|.]+?:l)[\s|)]')
location_pattern = re.compile('\s([a-z|_|.]+?:lo)[\s|)]')
mountain_pattern = re.compile('\s([a-z|_|.]+?:m)[\s|)]')
name_pattern = re.compile('\s([a-z|_|.]+?:n)[\s|)]')


if __name__ == '__main__':
    test_data = '../../data/geo/geo_lambda_calculus_test.tsv'
    train_data = '../../data/geo/geo_lambda_calculus_train.tsv'

    logical_forms = list()
    with open(test_data, 'r') as f:
        for line in f:
            line = line.strip()
            logical_forms.append(line.split('\t')[1].lower())
    with open(train_data, 'r') as f:
        for line in f:
            line = line.strip()
            logical_forms.append(line.split('\t')[1].lower())

    state_names = set()
    for p in logical_forms:
        matches = state_pattern.findall(p)
        for m in matches:
            state_names.add(m)
    print("State Names: ")
    print(['"%s"' % c for c in state_names])
    print("====\n\n")

    city_names = set()
    for p in logical_forms:
        matches = city_pattern.findall(p)
        for m in matches:
            city_names.add(m)
    print("City Names: ")
    print(['"%s"' % c for c in city_names])
    print("====\n\n")

    river_names = set()
    for p in logical_forms:
        matches = river_pattern.findall(p)
        for m in matches:
            river_names.add(m)
    print("River Names: ")
    print(['"%s"' % c for c in river_names])
    print("====\n\n")

    lake_names = set()
    for p in logical_forms:
        matches = lake_pattern.findall(p)
        for m in matches:
            lake_names.add(m)
    print("Lake Names: ")
    print(['"%s"' % c for c in lake_names])
    print("====\n\n")

    location_names = set()
    for p in logical_forms:
        matches = location_pattern.findall(p)
        for m in matches:
            location_names.add(m)
    print("Location Names: ")
    print(['"%s"' % c for c in location_names])
    print("====\n\n")

    mountain_names = set()
    for p in logical_forms:
        matches = mountain_pattern.findall(p)
        for m in matches:
            mountain_names.add(m)
    print("Mountain Names: ")
    print(['"%s"' % c for c in mountain_names])
    print("====\n\n")

    names = set()
    for p in logical_forms:
        matches = name_pattern.findall(p)
        for m in matches:
            names.add(m)
    print("Names: ")
    print(['"%s"' % c for c in names])
    print("====\n\n")