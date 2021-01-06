# coding=utf8


import re
import os
import json
import argparse
import subprocess

import sys
sys.path += ['..', '../../']


pattern = re.compile("(\d+)'\s+([yn])'")

script_template = """
:-compile('%s').
:-compile('%s').
:-compile('%s').
:-use_module(library(time)).
%s
:-halt.
"""


def tokenize(logical_form):
    normalized_lf = logical_form.replace(" ", "::")
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        (',', ' , '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    toks = [t if "::" not in t else t.replace(
        "::", " ") for t in normalized_lf.split()]
    return toks


def fix_variables(logical_form):
    # Tokenize Prolog
    toks = tokenize(logical_form)
    toks = [t.upper() if len(t) == 1 and re.match(
        '[a-z]', t) else t for t in toks]
    return "".join(toks)


def recover_variable_name(logical_form):
    """Undo the variable name standardization."""
    toks = tokenize(logical_form)
    cur_var = chr(ord('A') - 1)
    new_toks = []
    for w in toks:
        if w == 'NV' or w == 'nv':
            cur_var = chr(ord(cur_var) + 1)
            new_toks.append(cur_var)
        elif re.match('[V|v]\d+', w):
            ind = int(w[1:])
            new_toks.append(chr(ord(cur_var) - ind))
        else:
            new_toks.append(w)
    return ''.join(new_toks)


def is_valid(lf, grammar):
    try:
        grammar.parse(lf)
    except:
        return False
    return True


def evaluate(path, grammar, is_recover_variable, timeout=120):
    with open(path, 'r') as f:
        predictions = json.load(f)
    library_path = os.path.join(os.getcwd(), 'prolog')
    count = len(predictions)
    code = list()
    grammar_valid_count = 0
    for pidx, p in enumerate(predictions):
        if is_valid(p['predicted_logical_form'], grammar):
            if is_recover_variable:
                pred = recover_variable_name(p['predicted_logical_form'])
                truth = recover_variable_name(p['truth_logical_form'])
            else:
                pred = fix_variables(p['predicted_logical_form'])
                truth = fix_variables(p['truth_logical_form'])
            code.append(
                ":-catch((call_with_time_limit(%d, execute_query(%s, U%d1)), call_with_time_limit(%d, execute_query(%s, U%d2)), print(%d), (U%d1 == U%d2 -> print(' y') ; print(' n')), nl), time_limit_exceeded, (print(%d), print(' n'), nl))." %
                (timeout, pred, pidx, timeout, truth, pidx, pidx, pidx, pidx, pidx))
            grammar_valid_count += 1
    code = "\n".join(code)
    script = script_template % (
        os.path.join(library_path, 'geobase.pl'),
        os.path.join(library_path, 'geoquery.pl'),
        os.path.join(library_path, 'evalp.pl'),
        code
    )
    with open('eval_prolog.pl', 'w') as f:
        f.write(script)

    command = 'swipl -l ' + 'eval_prolog.pl > prolog_result.log'
    subprocess.call(command, shell=True)

    # Parse Result
    correct = 0
    valid_executions = 0
    with open('prolog_result.log', 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                match = pattern.match(line)
                if match:
                    valid_executions += 1
                    index, is_correct = int(
                        match.group(1)), match.group(2) == 'y'
                    predictions[index]['execution_correct'] = is_correct
                    if is_correct:
                        correct += 1
    print("Total: %d, Grammar Valid: %d, Valid Executions: %d, Correct: %d, Accuracy: %f" %
          (len(predictions), grammar_valid_count, valid_executions, correct, float(correct / len(predictions))))
    # with open(path, 'w') as f:
    #     f.write(json.dumps(predictions))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--predictions', help='file that stores the prediction results', required=True)
    parser.add_argument("--recover_variable",
                        action='store_true', default=False)
    parser.add_argument("--timeout",
                        help='timeout limit for expression', default=120, type=int)
    args = parser.parse_args()
    from grammars.grammar import get_grammar
    grammar = get_grammar('geo', 'prolog')
    evaluate(args.predictions, grammar, args.recover_variable, args.timeout)
