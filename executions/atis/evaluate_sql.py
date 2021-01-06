# coding=utf8

import os
import re
import json
import argparse
from sql.evaluator import compare_sqls


def evaluate(path, timeout=120):
    with open(path, 'r') as f:
        predictions = json.load(f)
    
    total = len(predictions)
    correct = 0
    for pidx, p in enumerate(predictions):
        truth = p['truth_logical_form']
        pred = p['predicted_logical_form']
        print(pidx)
        print(truth)
        print(pred)
        if truth == pred or compare_sqls(truth, pred):
            print(True)
            correct += 1
        else:
            print(False)
        print("===\n\n")
    print("Total: %d, Correct: %d, Accuracy: %f" %
            (total, correct, float(correct / total)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--predictions', help='file that stores the prediction results', required=True)
    args = parser.parse_args()
    evaluate(args.predictions)
