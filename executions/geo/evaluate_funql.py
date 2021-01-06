# coding=utf8

import os
import re
import json
import argparse
import subprocess

pattern = re.compile("(\d+)'\s+([yn])'")


script_template = """
:-compile('%s').
:-compile('%s').
:-compile('%s').
:-use_module(library(time)).
%s
:-halt.
"""


def evaluate(path, timeout=120):
    with open(path, 'r') as f:
        predictions = json.load(f)
    library_path = os.path.join(os.getcwd(), 'funql')
    code = list()
    for pidx, p in enumerate(predictions):
        truth = p['truth_logical_form']
        pred = p['predicted_logical_form']
        code.append(
            ":-catch((call_with_time_limit(%d, execute_funql_query(%s, U%d1)), call_with_time_limit(%d, execute_funql_query(%s, U%d2)), print(%d), (U%d1 == U%d2 -> print(' y') ; print(' n')), nl), time_limit_exceeded, (print(%d), print(' n'), nl))." %
            (timeout, pred, pidx, timeout, truth, pidx, pidx, pidx, pidx, pidx))
    code = "\n".join(code)
    script = script_template % (
        os.path.join(library_path, 'geobase.pl'),
        os.path.join(library_path, 'geoquery.pl'),
        os.path.join(library_path, 'eval.pl'),
        code
    )
    with open('eval_funql.pl', 'w') as f:
        f.write(script)

    command = 'swipl -l ' + 'eval_funql.pl > funql_result.log'
    subprocess.call(command, shell=True)

    # Parse Result
    count = 0
    correct = 0
    with open('funql_result.log', 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                match = pattern.match(line)
                if match:
                    count += 1
                    index, is_correct = int(
                        match.group(1)), match.group(2) == 'y'
                    predictions[index]['execution_correct'] = is_correct
                    if is_correct:
                        correct += 1
    print("Total: %d, Correct: %d, Accuracy: %f" %
          (len(predictions), correct, float(correct / len(predictions))))
    # assert count == len(predictions)
    with open(path, 'w') as f:
        f.write(json.dumps(predictions, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--predictions', help='file that stores the prediction results', required=True)
    args = parser.parse_args()
    evaluate(args.predictions)
