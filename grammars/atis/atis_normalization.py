# coding=utf8


import re


def standardize_lambda_calculus_varnames(ans):
    toks = ans.split(' ')
    varnames = {}
    new_toks = []
    for t in toks:
        if t == 'x' or t.startswith('$'):
            if ':' in t:
                # var definition
                splits = t.split(':')
                name, var_type = splits[0], splits[1]
                assert name not in varnames
                new_name = '$v%d' % len(varnames)
                varnames[name] = new_name
                new_toks.append(new_name + ":" +  var_type)
            else:
                # t is a variable name
                if t in varnames:
                    new_toks.append(varnames[t])
                else:
                    new_varname = '$v%d' % len(varnames)
                    varnames[t] = new_varname
                    new_toks.append(new_varname)
        else:
            new_toks.append(t)
    lf = ' '.join(new_toks)
    return lf


def normalize_lambda_calculus(logical_form):
    s = standardize_lambda_calculus_varnames(logical_form)
    s = s.replace(' :', ":").replace(
        '\s+', ' ').replace("( ", "(").replace(" )", ")").replace(')\s)', '))').replace(" )", ")").strip().lower()
    variables = ["$v0", "$v1", "$v10", "$1", "$2", "$3", "$y",
                 "$0", "$v7", "$v3", "$f", "$x", "$v6", "$v14", "$airline", "$v2", "$v5", "x"]
    for var in variables:
        s = s.replace(var + " e ", "%s:e " % var)
        s = s.replace(var + " i ", "%s:i " % var)
    return s


def to_lisp_tree(logical_form):
    expr = logical_form.replace("(", " ( ").replace(")", " ) ").strip()
    expr = re.sub(' +', ' ', expr)
    toks = expr.split(' ')

    def recurse(i):
        if toks[i] == '(':
            subtrees = []
            j = i+1
            while True:
                subtree, j = recurse(j)
                subtrees.append(subtree)
                if toks[j] == ')':
                    return subtrees, j + 1
        else:
            return toks[i], i+1

    try:
        lisp_tree, final_ind = recurse(0)
        return lisp_tree
    except Exception as e:
        print('Failed to convert "%s" to lisp tree' % expr)
        print(e)
        return None


def postprocess_lambda_calculus(logical_form):
    lisp_tree = to_lisp_tree(logical_form)
    if lisp_tree is None: return logical_form

    # Post-order traversal, sorting as we go
    def recurse(node):
        if isinstance(node, str): return
        for child in node:
            recurse(child)
        if node[0] in ('_and', '_or'):
            node[1:] = sorted(node[1:], key=lambda x: str(x))
    recurse(lisp_tree)

    def tree_to_str(node):
        if isinstance(node, str):
            return node
        else:
            return '( %s )' % ' '.join(tree_to_str(child) for child in node)
    return tree_to_str(lisp_tree)


def preprocess_sql(logical_form):
    s = re.sub(' +', ' ', logical_form).lower()
    s = s.replace('and 1 = 1', '')
    s = s.replace('where 1 = 1', '')
    s = s.replace('max (', 'max(')
    s = s.replace('min (', 'min(')
    s = s.replace('avg (', 'avg(')
    s = s.replace('count (', 'count(')
    s = s.replace('sum (', 'sum(')
    s = s.replace('< =', '<=')
    s = s.replace('> =', '>=')
    # Domain
    s = s.replace(' flight ', ' flight_base ')
    s = s.replace(' airport ', ' airport_base ')
    s = s.replace(' fare ', ' fare_base ')
    s = s.replace('aircraft_code ', 'aircraft_code_base ')
    s = s.replace('aircraft_code)', 'aircraft_code_base)')
    s = re.sub(' +', ' ', s)
    s = s.replace("( ", "(").replace(" )", ")").replace(";", "").replace('"', "'").replace(' . ', '.').strip()
    return s.strip()


def postprocess_sql(logical_form):
    # Domain
    s = logical_form + ';'
    s = s.replace(' flight_base ', ' flight ')
    s = s.replace(' airport_base ', ' airport ')
    s = s.replace(' fare_base ', ' fare ')
    s = s.replace('aircraft_code_base ', 'aircraft_code ')
    s = s.replace('aircraft_code_base)', 'aircraft_code)')
    s = s.replace('aircraft_code_base;', 'aircraft_code;')
    return s


def standardize_prolog_varnames(ans):
    toks = ans.split(' ')
    varnames = {}
    new_toks = []
    for t in toks:
        if re.match('[A-B|a-b]]', t):
            if t in varnames:
                new_toks.append(varnames[t])
            else:
                new_varname = chr(ord('A')+len(varnames))
                varnames[t] = new_varname
                new_toks.append(new_varname)
        else:
            new_toks.append(t)
    lf = ' '.join(new_toks)
    return lf


def tokenize_prolog(logical_form):
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


# Pre/Post Processors of Prolog
def preprocess_prolog(logical_form):
    tokens = tokenize_prolog(logical_form)
    standardized = standardize_prolog_varnames(" ".join(tokens)).replace(" ", "").lower()
    return standardized


def normalize_prolog_variable_names(logical_form):
    """Standardize variable names in Prolog with De Brujin indices."""
    toks = tokenize_prolog(logical_form)
    # Replace Variable
    cur_vars = []
    new_toks = []
    for w in toks:
        if len(w) == 1 and w.isalpha() and re.match('[a-z]', w):
            if w in cur_vars:
                ind_from_end = len(cur_vars) - cur_vars.index(w) - 1
                new_toks.append('V%d' % ind_from_end)
            else:
                cur_vars.append(w)
                new_toks.append('NV')
        else:
            new_toks.append(w)
    return ''.join(new_toks).lower()


def preprocess_funql(lf):
    l = re.sub(r"\s*\(\s*", "(", lf)
    l = re.sub(r"\s*\)\s*", ")", l)
    l = re.sub(r"\s*,\s*", ",", l)
    l = l.lower()
    return l


if __name__ == '__main__':
    processed = preprocess_prolog('answer_1(A,(is_flight(A),is_to(A,B),const(B,airport_code(mke))))')
    print(processed)
