# coding=utf8

import os
import re
import json
import shutil
import argparse
import subprocess
from geo.lambda_calculus.transform_lambda_caculus import transform

pattern = re.compile('\((\d+),Just\s+(.*)\)')
failed_pattern = re.compile('\((\d+),Nothing\)')

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


def evaluate(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            q, l = splits[0], splits[1]
            questions.append(q)
            logical_forms.append(l)

    # timeout_limits = 5 * 60 * 1000000
    # code = list()
    # for pidx, p in enumerate(logical_forms):
    #     code.append("""    compare_result_%d <- (timeout %d (return $! (%s)))""" %
    #                 (pidx, timeout_limits, transform(p)))
    #     code.append("""    print (%d, compare_result_%d)""" % (pidx, pidx))
    # code = "\n".join(code)
    # code = script_template % code
    # with open('Main.hs', 'w') as f:
    #     f.write(code)

    # # copy file
    # shutil.copyfile('./Main.hs', './geo/lambda_calculus/evaluator/app/Main.hs')

    # # Change directory
    # os.chdir('./geo/lambda_calculus/evaluator')

    # # Compile & run
    # command = 'stack build'
    # subprocess.call(command, shell=True)

    # command = 'stack exec evaluator-exe > ./lambda_calculus_result.log'
    # subprocess.call(command, shell=True)

    # # move file
    # shutil.copyfile('./lambda_calculus_result.log',
    #                 '../../lambda_calculus_result.log')

    # Read result
    failed_count = 0
    with open('lambda_calculus_train_result.log', 'r') as f, open('lambda_calculus_train_execution_results.tsv', 'w') as wf:
        for lidx, line in enumerate(f):
            line = line.strip()
            if lidx == 0 or len(line) == 0:
                continue

            print(line)
            # Failed
            match = failed_pattern.match(line)
            if match:
                failed_count += 1
                idx = int(match.group(1))
                wf.write("%s\t%s\n" % (questions[idx], "Nothing"))
                continue

            match = pattern.match(line)
            assert match is not None
            idx = int(match.group(1))
            result = match.group(2)
            wf.write("%s\t%s\n" % (questions[idx], result))

    print("Failed Count: ", failed_count)


if __name__ == '__main__':
    evaluate('../data/geo/geo_lambda_calculus_train.tsv')
