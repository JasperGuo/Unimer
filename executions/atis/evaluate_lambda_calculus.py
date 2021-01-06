# coding=utf8


import json
import argparse
from lambda_calculus.lc_evaluator import compare_lambda_calculus


def evaluate(path, timeout=600):
    with open(path, 'r') as f:
        predictions = json.load(f)

    total = len(predictions)
    correct = 0
    for pidx, p in enumerate(predictions):
        print(pidx)
        print(p['question'])
        truth = p['truth_logical_form']
        pred = p['predicted_logical_form']
        is_correct = False
        if truth == pred:
            is_correct = True
        elif compare_lambda_calculus(truth, pred, time_limit=timeout):
            is_correct = True
        if is_correct:
            correct += 1
        print("is_correct: ", is_correct)
        print("===\n\n")
    print("Total: %d, Correct: %d, Accuracy: %f" %
          (total, correct, float(correct / total)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--predictions', help='file that stores the prediction results', required=True)
    args = parser.parse_args()
    evaluate(args.predictions)
