# coding=utf8

import re


def read_data():
    questions, logical_forms = list(), list()
    paths = [
        "../../data/atis/atis_prolog_train.tsv",
        "../../data/atis/atis_prolog_dev.tsv",
        "../../data/atis/atis_prolog_test.tsv"]
    for p in paths:
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                splits = line.split('\t')
                questions.append(splits[0])
                logical_forms.append(splits[1])
    return questions, logical_forms


def get_const(logical_forms):
    pattern = re.compile("const\([A-Z],(.*?)\(([a-z|A-Z|\d|_|\.]+)\)\)")
    object_dict = dict()
    for lf in logical_forms:
        results = pattern.findall(lf)
        if len(results):
            for result in results:
                if result[0] not in object_dict:
                    object_dict[result[0]] = list()
                object_dict[result[0]].append(result[1])
    return object_dict


def get_unit_relations(logical_forms):
    pattern = re.compile("[,|\(]([a-z|\d|_]+d?)\([A-Z]\)[,|)]")
    unit_relations = set()
    for lf in logical_forms:
        results = pattern.findall(lf)
        if len(results):
            for result in results:
                unit_relations.add(result)
    return unit_relations


def get_binary_relations(logical_forms):
    pattern = re.compile("[,|\(]([a-z|\d|_]+d?)\([A-Z],[A-Z]\)[,|)]")
    binary_relations = set()
    for lf in logical_forms:
        results = pattern.findall(lf)
        if len(results):
            for result in results:
                binary_relations.add(result)
    return binary_relations


def get_triplet_relations(logical_forms):
    pattern = re.compile("[,|\(]([a-z|\d|_]+d?)\([A-Z],[A-Z],[A-Z]\)[,|)]")
    triplet_relations = set()
    for lf in logical_forms:
        results = pattern.findall(lf)
        if len(results):
            for result in results:
                triplet_relations.add(result)
    return triplet_relations


def get_arg_predicates(logical_forms):
    pattern = re.compile("((argmin|argmax)[a-z|\d|_]+?)\(")
    arg_relations = set()
    for lf in logical_forms:
        results = pattern.findall(lf)
        if len(results):
            for result in results:
                arg_relations.add(result[0])
    return arg_relations


if __name__ == '__main__':
    questions, logical_forms = read_data()

    # Const Objects
    print("Const Objects")
    const_object_dict = get_const(logical_forms)
    object_names = ["(%s)" % k for k in const_object_dict.keys()]
    print(object_names)
    for key, values in const_object_dict.items():
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" %s_value ")")']""" % (key, key, key))
        print("GRAMMAR_DICTIONARY['%s_value'] = %s" % (key, str(['"%s"' % v for v in set(values)])))
    print("==\n\n")

    # Unit Relations
    print("Unit Relations")
    unit_relations = get_unit_relations(logical_forms)
    print(unit_relations)
    print("""GRAMMAR_DICTIONARY['unit_relation'] = %s""" % (["(%s)" % r for r in unit_relations]))
    for r in unit_relations:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" var ")")']""" % (r, r))
    print("==\n\n")

    # Binary Relations
    binary_relations = get_binary_relations(logical_forms)
    print("Binary Relations")
    print(binary_relations)
    print("""GRAMMAR_DICTIONARY['binary_relation'] = %s""" % (["(%s)" % r for r in binary_relations]))
    for r in binary_relations:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" var "," var ")")']""" % (r, r))
    print("==\n\n")

    triplet_relations = get_triplet_relations(logical_forms)
    print("Triplet Relations")
    print(triplet_relations)
    print("""GRAMMAR_DICTIONARY['triplet_relation'] = %s""" % (["(%s)" % r for r in triplet_relations]))
    for r in triplet_relations:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" var "," var "," var ")")']""" % (r, r))
    print("==\n\n")

    # Arg Predicates
    print("Arg Relations")
    arg_predicates = get_arg_predicates(logical_forms)
    print(arg_predicates)
    for r in arg_predicates:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" var "," goal)']""" % (r, r))
