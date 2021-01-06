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
%s
:-halt.
"""


def evaluate(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            q, origin_lf = splits[0], splits[1]
            questions.append(q)
            # l = re.sub(r"\s*\(\s*", "(", origin_lf)
            # l = re.sub(r"\s*\)\s*", ")", l)
            # l = re.sub(r"\s*,\s*", ",", l)
            # l = re.sub(r"\s*'\s*", "'", l)
            # l = re.sub(r'_([a-z]+\()', r'\1', l)
            # l = l.replace("_nextto", "next_to")
            # l = l.replace("_highpoint", "high_point")
            # l = l.replace("_lowpoint", "low_point")
            # l = l.replace("\+", 'not')
            logical_forms.append(origin_lf)

    commands = list()
    for idx, lf in enumerate(logical_forms):
        if idx == 257:
            continue
        command = ":-execute_query(%s, U%d),print(%d),print(U%d),nl." % (
            lf, idx, idx, idx)
        commands.append(command)
    commands = '\n'.join(commands)
    library_path = os.path.join(os.getcwd(), 'geo', 'prolog')
    script = script_template % (
        os.path.join(library_path, 'geobase.pl'),
        os.path.join(library_path, 'geoquery.pl'),
        commands
    )
    with open('test_prolog.pl', 'w') as f:
        f.write(script)

    command = 'swipl -l ' + 'test_prolog.pl > prolog_result.log'
    subprocess.call(command, shell=True)

    # Read result
    with open('prolog_result.log', 'r') as f, open('prolog_execution_results.tsv', 'w') as wf:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            assert match is not None
            idx = int(match.group(1))
            result = match.group(2)
            wf.write("%s\t%s\n" % (questions[idx], result))


if __name__ == '__main__':
    evaluate('../data/geo/geo_prolog_test_fixed.tsv')
