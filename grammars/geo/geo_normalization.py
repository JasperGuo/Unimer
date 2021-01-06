# coding=utf8

import re


def anonymize_prolog_variable_names(logical_form):
    p = re.sub('[A-G]', 'A', logical_form).lower()
    return p


def tokenize_prolog(logical_form):
    # Tokenize Prolog
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


def normalize_prolog_variable_names(logical_form):
    """Standardize variable names in Prolog with De Brujin indices."""
    toks = tokenize_prolog(logical_form)
    # Replace Variable
    cur_vars = []
    new_toks = []
    for w in toks:
        if len(w) == 1 and w.isalpha() and re.match('[A-G]', w):
            if w in cur_vars:
                ind_from_end = len(cur_vars) - cur_vars.index(w) - 1
                new_toks.append('V%d' % ind_from_end)
            else:
                cur_vars.append(w)
                new_toks.append('NV')
        else:
            new_toks.append(w)
    return ''.join(new_toks).lower()


def recover_normalized_prolog_variable_name(logical_form):
    """Undo the variable name standardization."""
    toks = tokenize_prolog(logical_form)
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


def normalize_sql(logical_form):
    s = logical_form.replace("( ", "(").replace(" )", ")").replace(
        ";", "").replace('"', "'").replace(' . ', '.').strip().lower()
    s = s.replace('max (', 'max(')
    s = s.replace('min (', 'min(')
    s = s.replace('avg (', 'avg(')
    s = s.replace('count (', 'count(')
    s = s.replace('sum (', 'sum(')
    s = s.replace('count(1)', 'count(*)')
    return s


def normalize_lambda_calculus(logical_form):
    s = logical_form.replace(
        '\s+', ' ').replace("( ", "(").replace(" )", ")").replace(') )', '))').replace(' :', ':').strip().lower()
    return s


def normalize_prolog(lf):
    l = re.sub(r"\s*\(\s*", "(", lf)
    l = re.sub(r"\s*\)\s*", ")", l)
    l = re.sub(r"\s*,\s*", ",", l)
    l = l.lower()
    return l


def normalize_funql(lf):
    l = re.sub(r"\s*\(\s*", "(", lf)
    l = re.sub(r"\s*\)\s*", ")", l)
    l = re.sub(r"\s*,\s*", ",", l)
    l = l.lower()
    return l
