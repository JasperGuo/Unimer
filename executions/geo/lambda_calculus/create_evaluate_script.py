# coding=utf8

import os
import json


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
    
    let total = length results
    let correct = length . filter (\x -> x == Just True) $ results

    putStrLn "Results: "
    print total
    print correct"""

def read_predictions(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def main(filepath):
    predictions = read_predictions(filepath)
    timeout_limits = 10 * 60 * 1000000
    code = list()
    result_code = """    let results = ["""
    for pidx, p in enumerate(predictions):
        print(pidx)
        print(p['question'])
        print(p['predicted_logical_form'])
        print("==\n\n")
        code.append("""    compare_result_%d <- (timeout %d (return $! ((%s) == (%s))))""" % (pidx, timeout_limits, p['predicted_logical_form'], p['truth_logical_form']))
        code.append("""    print (%d, compare_result_%d)""" % (pidx, pidx))
        result_code += "compare_result_%d," % pidx
    result_code = result_code[:-1] + "]"
    code.append(result_code)
    code = "\n".join(code)
    code = script_template % code
    with open('Main.hs', 'w') as f:
        f.write(code)


if __name__ == '__main__':
    main("test_predictions.json")