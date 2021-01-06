# coding=utf8

import re
import os
import json
import shutil
import argparse
import subprocess
from lambda_calculus.transform_lambda_caculus import transform

import sys
sys.path += ['..', os.path.join('..', '..')]

pattern = re.compile('\(\"([p|t])\",(\d+),Just\s+(.*)\)')
failed_pattern = re.compile('\(\"([p|t])\",(\d+),(Nothing|\"Nothing\")\)')


script_template = r"""
module Main where

import Lib
import Geobase
import Geofunctions
import System.Environment
import System.Timeout

main :: IO ()
main = do
    putStrLn "Execute Lambda Calculus"
    -- let predicted_result = (count_ (\x -> (and [(river x), (loc x "texas:s")])))
    -- let truth_result = (count_ (\x -> (and [(river x), (loc x "texas:s")])))
    -- let compare_result = predicted_result == truth_result
%s
"""


def is_valid(lf, grammar):
    try:
        grammar.parse(lf)
    except:
        return False
    return True


def check_misuse_of_variable(lf, tokenizer):
    tokens = tokenizer.tokenize(lf)
    defined_variables = list()
    for token in tokens:
        if token.text.endswith(":e") or token.text.endswith(":i"):
            defined_variables.append(token.text)
        else:
            if token.text.startswith("$"):
                # Check if it is defined
                for dv in defined_variables:
                    if token.text == dv[:2]:
                        break
                else:
                    return False
    return True


def calculuate_result(path):
    with open(path, 'r') as f:
        predictions = json.load(f)

    predicted_query_results, truth_query_results = list(), list()
    with open('./lambda_calculus/evaluator/lambda_calculus_is_correct_result.log', 'r') as f:
        for lidx, line in enumerate(f):
            line = line.strip()
            if lidx == 0 or len(line) == 0:
                continue

            match = failed_pattern.match(line)
            if match:
                is_predict = match.group(1) == 'p'
                if is_predict:
                    predicted_query_results.append((int(match.group(2)), None))
                else:
                    truth_query_results.append((int(match.group(2)), None))
                continue

            print(line)
            match = pattern.match(line)
            assert match is not None
            is_predict = match.group(1) == 'p'
            idx = int(match.group(2))
            result = match.group(3)
            if is_predict:
                predicted_query_results.append((idx, result))
            else:
                truth_query_results.append((idx, result))

        correct_count = 0
        for idx, pq_result in predicted_query_results:
            if pq_result is None:
                continue

            # find truth result
            for tidx, tq_result in truth_query_results:
                if idx == tidx:
                    if pq_result == tq_result:
                        correct_count += 1
                        break

        print("Correct Count: %d, Total: %d, Accuracy: %f" %
              (correct_count, len(predictions), (correct_count/len(predictions))))


def evaluate(path, grammar, tokenizer, timeout=120):
    with open(path, 'r') as f:
        predictions = json.load(f)

    timeout_limits = 10 * 60 * 1000000
    code = list()
    result_code = """    let results = ["""
    predicted_queries, truth_queries = list(), list()
    for pidx, p in enumerate(predictions):
        if is_valid(p['predicted_logical_form'], grammar) and \
             check_misuse_of_variable(p['predicted_logical_form'], tokenizer):
            print(pidx)
            print(p['question'])
            print(p['truth_logical_form'])
            print(p['predicted_logical_form'])
            print("==\n\n")
            transformed_pred = transform(p['predicted_logical_form'])
            transform_truth = transform(p['truth_logical_form'])

            if transformed_pred.startswith("[e") and not transform_truth.startswith('[e'):
                transform_truth = "[%s]" % transform_truth
            if transform_truth.startswith('[e') and not transformed_pred.startswith("[e"):
                transformed_pred = "[%s]" % transformed_pred

            predicted_queries.append((pidx, transformed_pred))
            truth_queries.append((pidx, transform_truth))

    for (idx, pq) in predicted_queries:
        code.append("""    compare_result_p%d <- (timeout %d (return $! (%s)))""" %
                    (idx, timeout_limits, pq))
        code.append("""    print ("p", %d, compare_result_p%d)""" % (idx, idx))

    for (idx, tq) in truth_queries:
        code.append("""    compare_result_t%d <- (timeout %d (return $! (%s)))""" %
                    (idx, timeout_limits, tq))
        code.append("""    print ("t", %d, compare_result_t%d)""" % (idx, idx))

    code = "\n".join(code)
    code = script_template % (code)
    with open('Main.hs', 'w') as f:
        f.write(code)

    # copy file
    shutil.copyfile('./Main.hs', './lambda_calculus/evaluator/app/Main.hs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--predictions', help='file that stores the prediction results', required=True)
    parser.add_argument("--timeout",
                        help='timeout limit for expression', default=120, type=int)
    args = parser.parse_args()
    from grammars.grammar import get_grammar
    grammar = get_grammar('geo', 'lambda')
    from grammars.utils import get_logical_form_tokenizer
    tokenizer = get_logical_form_tokenizer('geo', 'lambda')
    evaluate(args.predictions, grammar, tokenizer, args.timeout)
    # calculuate_result(args.predictions)
