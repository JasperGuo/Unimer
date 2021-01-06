# coding=utf8

import re
import json

entity_pattern = re.compile('\s([a-z|_|.]+?:[a-z]+)[\s|)]')


def process_logic_expression(haskell_lf, is_and):
    if is_and:
        target, replace_target, replace_result = "(and:<t*,t>", "and:<t*,t>", "and ["
    else:
        target, replace_target, replace_result = "(or:<t*,t>", "or:<t*,t>", "or ["
    and_count = haskell_lf.count(target)
    # print(and_count)
    for and_idx in range(and_count):
        try:
            index = haskell_lf.rindex(target)
        except:
            pass
        else:
            prefix = haskell_lf[:index]
            suffix = haskell_lf[index:].replace(replace_target, replace_result)
            assert suffix[0] == '('
            idx = 1
            stack = [suffix[idx]]
            new_suffix = "("
            while idx < len(suffix):
                if len(stack) == 0:
                    break
                character = suffix[idx]
                new_suffix += character
                if character == ')':
                    stack.pop(len(stack) - 1)
                    if len(stack) == 1:
                        new_suffix += ','
                elif character == '(':
                    stack.append('(')
                idx += 1
            new_suffix = new_suffix[:-1] + '])' + suffix[idx:]
            if new_suffix.count('[') != new_suffix.count(']'):
                print("Not equals")
            # assert new_suffix.count('[') == new_suffix.count(']')
            haskell_lf = prefix + new_suffix
            # print(new_suffix)
    haskell_lf = haskell_lf.replace("[ (", "[(").replace(",]", "]")
    return haskell_lf


def transform(logical_form):
    # 1. Replace argument $0, $1, $2, $3, $4 -> x, y, z, m, n
    haskell_lf = logical_form.replace('$0', 'x')
    haskell_lf = haskell_lf.replace('$1', 'y')
    haskell_lf = haskell_lf.replace('$2', 'z')
    haskell_lf = haskell_lf.replace('$3', 'm')
    haskell_lf = haskell_lf.replace('$4', 'n')

    # 2. Replace Predicate
    haskell_lf = haskell_lf.replace('state:<s,t>', 'state')
    haskell_lf = haskell_lf.replace('capital:<c,t>', 'capital')
    haskell_lf = haskell_lf.replace('capital:<s,c>', 'capital2')
    haskell_lf = haskell_lf.replace('capital:<s,<c,t>>', 'is_state_capital')
    haskell_lf = haskell_lf.replace('capital2:<s,<c,t>>', 'is_state_capital')
    haskell_lf = haskell_lf.replace('place:<p,t>', 'place')
    haskell_lf = haskell_lf.replace('city:<c,t>', 'city')
    haskell_lf = haskell_lf.replace('town:<lo,t>', 'town')
    haskell_lf = haskell_lf.replace('river:<r,t>', 'river')
    haskell_lf = haskell_lf.replace('lake:<l,t>', 'lake')
    haskell_lf = haskell_lf.replace('mountain:<m,t>', 'mountain')
    haskell_lf = haskell_lf.replace('high_point:<e,<e,t>>', 'high_point')
    haskell_lf = haskell_lf.replace('elevation:<lo,i>', 'elevation')
    haskell_lf = haskell_lf.replace('area:<lo,i>', 'area')
    haskell_lf = haskell_lf.replace('population:<lo,i>', 'population')
    haskell_lf = haskell_lf.replace('population:<lo,<i,t>>', 'is_population')
    haskell_lf = haskell_lf.replace('area:<lo,i>', 'area')
    haskell_lf = haskell_lf.replace('len:<r,i>', 'len')
    haskell_lf = haskell_lf.replace('size:<lo,i>', 'size_')
    haskell_lf = haskell_lf.replace('next_to:<lo,<lo,t>>', 'next_to')
    haskell_lf = haskell_lf.replace('loc:<lo,<lo,t>>', 'loc')
    haskell_lf = haskell_lf.replace('major:<lo,t>', 'major')
    haskell_lf = haskell_lf.replace('density:<lo,i>', 'density')
    haskell_lf = haskell_lf.replace('density:<lo,<i,t>>', 'is_density')
    haskell_lf = haskell_lf.replace('elevation:<lo,<i,t>>', 'is_correct_elevation')
    haskell_lf = haskell_lf.replace('the:<<e,t>,e>', 'take_first')

    haskell_lf = haskell_lf.replace('argmax:<<e,t>,<<e,i>,e>>', 'argmax_')
    haskell_lf = haskell_lf.replace('argmin:<<e,t>,<<e,i>,e>>', 'argmin_')
    haskell_lf = haskell_lf.replace('sum:<<e,t>,<<e,i>,i>>', 'sum_')
    haskell_lf = haskell_lf.replace('forall:<<e,t>,t>', 'forall_')
    haskell_lf = haskell_lf.replace('exists:<<e,t>,t>', 'exists_')
    haskell_lf = haskell_lf.replace('count:<<e,t>,i>', 'count_')
    haskell_lf = haskell_lf.replace('equals:<e,<e,t>>', 'equals_')
    haskell_lf = haskell_lf.replace('in:<lo,<lo,t>>', 'equals_')
    haskell_lf = haskell_lf.replace('named:<e,<n,t>>', 'named')
    haskell_lf = haskell_lf.replace('not:<t,t>', 'not')
    haskell_lf = haskell_lf.replace('<:<i,<i,t>>', 'lower_than')
    haskell_lf = haskell_lf.replace('>:<i,<i,t>>', 'larger_than')
    haskell_lf = haskell_lf.replace('=:<i,<i,t>>', 'num_equals')

    # 3. Replace Lambda
    haskell_lf = haskell_lf.replace('lambda x:e', '\\x ->')
    haskell_lf = haskell_lf.replace('lambda x:i', '\\x ->')
    haskell_lf = haskell_lf.replace('lambda y:e', '\\y ->')
    haskell_lf = haskell_lf.replace('lambda z:e', '\\z ->')
    haskell_lf = haskell_lf.replace('lambda m:e', '\\m ->')
    haskell_lf = haskell_lf.replace('lambda n:e', '\\n ->')

    # 4. Replace and:<t*,t>
    haskell_lf = haskell_lf.replace("\s+", " ")
    haskell_lf = process_logic_expression(haskell_lf, is_and=True)
    haskell_lf = process_logic_expression(haskell_lf, is_and=False)

    # Replace Entity
    entities = set(entity_pattern.findall(haskell_lf))
    for e in entities:
        haskell_lf = haskell_lf.replace(e, '"%s"' % e)

    # Add runnning environment for Lambda expression
    if haskell_lf.startswith('(\\'):
        # Lambda
        lambda_variable_types = logical_form.split()[1]
        assert lambda_variable_types.endswith(
            ":e") or lambda_variable_types.endswith(":i")
        subjects = "all_entities" if lambda_variable_types.endswith(':e') else "all_numbers"
        haskell_lf = "[e | e <- %s, %s e]" % (subjects, haskell_lf)

    # Replace Constance Value
    haskell_lf = haskell_lf.replace('0:i', '0')

    return haskell_lf


if __name__ == '__main__':
    path = '../../../data/geo/geo_lambda_calculus_train.tsv'
    results = list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            question, logical_form = line.split('\t')
            haskell_lf = transform(logical_form)
            print(question)
            print(logical_form)
            print(haskell_lf)
            print("===\n\n")
            results.append({"question": question, "predicted_logical_form": haskell_lf, "truth_logical_form": haskell_lf})
    with open("test_predictions.json", 'w') as f:
        f.write(json.dumps(results))
