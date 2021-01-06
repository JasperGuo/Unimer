# coding=utf8

import re


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
        if re.match('[A-Z]', w) or re.match('_\d+', w):
            if w in cur_vars:
                ind_from_end = len(cur_vars) - cur_vars.index(w) - 1
                new_toks.append('V%d' % ind_from_end)
            else:
                cur_vars.append(w)
                new_toks.append('NV')
        else:
            new_toks.append(w)
    return ''.join(new_toks)


def preprocess_prolog(logical_form):
    normalized_prolog = normalize_prolog_variable_names(logical_form)
    normalized_prolog = re.sub(r"\s*\(\s*", "(", normalized_prolog)
    normalized_prolog = re.sub(r"\s*\)\s*", ")", normalized_prolog)
    normalized_prolog = re.sub(r"\s*,\s*", ",", normalized_prolog)
    normalized_prolog = normalized_prolog.replace("\+ r", "\+r")
    normalized_prolog = normalized_prolog
    return normalized_prolog


def preprocess_funql(lf):
    l = re.sub(r"\s*\(\s*", "(", lf)
    l = re.sub(r"\s*\)\s*", ")", l)
    l = re.sub(r"\s*,\s*", ",", l)
    return l


def postprocess_prolog(logical_form):
    normalized_prolog = logical_form.replace("windo nt", "windows nt")
    normalized_prolog = normalized_prolog.replace("windo 95", "windows 95")
    return normalized_prolog


def postprocess_sql(logical_form):
    normalized_sql = logical_form.replace("windo nt", "windows nt")
    normalized_sql = normalized_sql.replace("windo 95", "windows 95")
    normalized_sql = normalized_sql.replace("\\'", "'")
    return normalized_sql


def postprocess_lambda(logical_form):
    normalized_lc = logical_form.replace("windo nt", "windows nt")
    normalized_lc = normalized_lc.replace("windo 95", "windows 95")
    normalized_lc = normalized_lc.replace("\\'", "'")
    return normalized_lc


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
        '\s+', ' ').replace("( ", "(").replace(" )", ")").replace(') )', '))').replace(' :', ':').strip()
    s = s.replace('"', "'").replace(') )', '))')

    return s


if __name__ == '__main__':
    sql = '(lambda $0:e (and (job $0) (language $0 perl) (company $0 "Lockheed Martin Aeronautics") (loc $0 colorado)))'
    normalized_sql = normalize_lambda_calculus(sql).replace("'", "\\'")
    sql_ = postprocess_lambda(normalized_sql)
    print(sql)
    print(normalized_sql)
    print(sql_)
