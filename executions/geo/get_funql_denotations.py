# coding=utf8

import os
import re
import json
import argparse
import subprocess

pattern = re.compile('(\d+)(\[.*\])')

script_template = """
:-compile('%s').
:-compile('%s').
:-compile('%s').
%s
:-halt.
"""


def evaluate(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            q, l = splits[0], splits[1]
            questions.append(q)
            logical_forms.append(l)
    commands = list()
    for idx, lf in enumerate(logical_forms):
        command = ":-execute_funql_query(%s, U%d),print(%d),print(U%d),nl." % (
            lf, idx, idx, idx)
        commands.append(command)
    commands = '\n'.join(commands)
    library_path = os.path.join(os.getcwd(), 'funql')
    script = script_template % (
        os.path.join(library_path, 'geobase.pl'),
        os.path.join(library_path, 'geoquery.pl'),
        os.path.join(library_path, 'eval.pl'),
        commands
    )
    with open('test_funql.pl', 'w') as f:
        f.write(script)

    command = 'swipl -l ' + 'test_funql.pl > funql_result.log'
    subprocess.call(command, shell=True)

    # Read result
    with open('funql_result.log', 'r') as f, open('funql_execution_results.tsv', 'w') as wf:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            assert match is not None
            idx = int(match.group(1))
            result = match.group(2)
            wf.write("%s\t%s\n" % (questions[idx], result))


if __name__ == '__main__':
    evaluate('../../data/geo/geo_funql_train.tsv')
