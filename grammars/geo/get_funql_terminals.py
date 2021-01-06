# coding=utf8

import re

stateid_pattern = re.compile('stateid\((.*?)\)')
riverid_pattern = re.compile('riverid\((.*?)\)')
countryid_pattern = re.compile('countryid\((.*?)\)')
cityid_pattern = re.compile('cityid\((.*?),(.*?)\)')
placeid_pattern = re.compile('placeid\((.*?)\)')


if __name__ == '__main__':
    test_data = '../../data/geo/geo_funql_test.tsv'
    train_data = '../../data/geo/geo_funql_train.tsv'

    funqls = list()
    with open(test_data, 'r') as f:
        for line in f:
            line = line.strip()
            funqls.append(line.split('\t')[1].lower())
    with open(train_data, 'r') as f:
        for line in f:
            line = line.strip()
            funqls.append(line.split('\t')[1].lower())

    state_names = set()
    for p in funqls:
        matches = stateid_pattern.findall(p)
        for m in matches:
            state_names.add(m)
    print("State Names: ")
    print(['"%s"' % c for c in state_names])
    print("====\n\n")

    country_names = set()
    for p in funqls:
        matches = countryid_pattern.findall(p)
        for m in matches:
            country_names.add(m)
    print("Country Names: ")
    print(['"%s"' % c for c in country_names])
    print("====\n\n")

    river_names = set()
    for p in funqls:
        matches = riverid_pattern.findall(p)
        for m in matches:
            river_names.add(m)
    print("River Names: ")
    print(['"%s"' % c for c in river_names])
    print("====\n\n")

    place_names = set()
    for p in funqls:
        matches = placeid_pattern.findall(p)
        for m in matches:
            place_names.add(m)
    print("Place Names: ")
    print(['"%s"' % c for c in place_names])
    print("====\n\n")

    city_names = set()
    state_abbres = set()
    for p in funqls:
        matches = cityid_pattern.findall(p)
        for c, s in matches:
            city_names.add(c)
            state_abbres.add(s)
    print("City Names: ")
    print(['"%s"' % c for c in city_names])
    print("====\n\n")

    print("State Abbres: ")
    print(['"%s"' % c for c in state_abbres])
    print("====\n\n")
