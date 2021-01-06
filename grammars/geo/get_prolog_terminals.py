# coding=utf8

import re

stateid_pattern = re.compile('_stateid\((.*?)\)')
riverid_pattern = re.compile('_riverid\((.*?)\)')
countryid_pattern = re.compile('_countryid\((.*?)\)')
cityid_pattern = re.compile('_cityid\((.*?),(.*?)\)')
placeid_pattern = re.compile('_placeid\((.*?)\)')


if __name__ == '__main__':
    test_data = '../../data/geo/geo_prolog_test.tsv'
    train_data = '../../data/geo/geo_prolog_train.tsv'

    prologs = list()
    with open(test_data, 'r') as f:
        for line in f:
            line = line.strip()
            prologs.append(line.split('\t')[1].replace(' ', '').replace("'", "").lower())
    with open(train_data, 'r') as f:
        for line in f:
            line = line.strip()
            prologs.append(line.split('\t')[1].replace(' ', '').replace("'", "").lower())

    state_names = set()
    for p in prologs:
        matches = stateid_pattern.findall(p)
        for m in matches:
            state_names.add(m)
    print("State Names: ")
    print(['"%s"' % c for c in state_names])
    print("====\n\n")

    country_names = set()
    for p in prologs:
        matches = countryid_pattern.findall(p)
        for m in matches:
            country_names.add(m)
    print("Country Names: ")
    print(['"%s"' % c for c in country_names])
    print("====\n\n")

    river_names = set()
    for p in prologs:
        matches = riverid_pattern.findall(p)
        for m in matches:
            river_names.add(m)
    print("River Names: ")
    print(['"%s"' % c for c in river_names])
    print("====\n\n")

    place_names = set()
    for p in prologs:
        matches = placeid_pattern.findall(p)
        for m in matches:
            place_names.add(m)
    print("Place Names: ")
    print(['"%s"' % c for c in place_names])
    print("====\n\n")

    city_names = set()
    state_abbres = set()
    for p in prologs:
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