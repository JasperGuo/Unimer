# coding=utf8

import re


def read_data():
    questions, logical_forms = list(), list()
    paths = [
        "../../data/job/job_prolog_train.tsv",
        "../../data/job/job_prolog_test.tsv"]
    for p in paths:
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                splits = line.split('\t')
                questions.append(splits[0])
                logical_forms.append(splits[1])
    return questions, logical_forms


def get_binary_predicates(logical_forms):
    binary_predicates = set()
    binary_pattern = re.compile('(([a-z|_|\d]+?)\(([A-Z]|[_|\d]+),([A-Z]|[_|\d]+)\))')
    for lf in logical_forms:
        matches = binary_pattern.findall(lf)
        for match in matches:
            binary_predicates.add(match[1])
    return binary_predicates


def get_unary_predicates(logical_forms):
    unary_predicates = set()
    unary_pattern = re.compile('(([a-z|_|\d]+?)\(([A-Z]|[_|\d]+)\))')
    for lf in logical_forms:
        matches = unary_pattern.findall(lf)
        for match in matches:
            unary_predicates.add(match[1])
    return unary_predicates


def get_terminals(logical_forms):
    terminals = set()
    terminal_pattern = re.compile("const\(([A-Z]|[_|\d]+),(.+?)\)")
    for lf in logical_forms:
        matches = terminal_pattern.findall(lf)
        for match in matches:
            terminals.add(match[1])
    return terminals


def get_all_salary_values(logical_forms):
    salary = set()
    salary_pattern = re.compile('salary_greater_than\(([A-Z]|[_|\d]+),(\d+),([a-z]+)\)')
    for lf in logical_forms:
        matches = salary_pattern.findall(lf)
        for match in matches:
            salary.add(match[1])
    return salary


if __name__ == '__main__':
    questions, logical_forms = read_data()
    binary_predicates = get_binary_predicates(logical_forms)

    print("Binary Relations")
    print(binary_predicates)
    print("""GRAMMAR_DICTIONARY['binary_relation'] = %s""" % (["(is_%s)" % r for r in binary_predicates]))
    for r in binary_predicates:
        print("""GRAMMAR_DICTIONARY['is_%s'] = ['("%s(" var "," var ")")']""" % (r, r))
    print("==\n\n")

    unary_predicates = get_unary_predicates(logical_forms)
    print("Unary Relations")
    print(unary_predicates)
    for r in unary_predicates:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" var ")")']""" % (r, r))
    print("===\n\n")


    terminals = get_terminals(logical_forms)
    print("Terminals")
    formatted_terminals = sorted(['"%s"' % t.replace("'", "\'") for t in terminals], key=lambda x: len(x), reverse=True)
    print(formatted_terminals)

    salary_values = get_all_salary_values(logical_forms)
    print("Salary Values:")
    print(['"%s"' % v for v in sorted(list(salary_values), key=lambda x: len(x), reverse=True)])
