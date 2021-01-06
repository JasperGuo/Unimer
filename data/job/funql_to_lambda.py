# coding-utf8


import re


def read_data(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            questions.append(splits[0])
            logical_forms.append(splits[1])
    return questions, logical_forms


def tokenize_funql(funql):
    normalized_lf = funql.replace(" ", "::")
    replacements = [
        ('(', '( '),
        (')', ' ) '),
        (',', ' , '),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    tokens = [t if "::" not in t else t.replace("::", " ") for t in normalized_lf.split()]
    return tokens


class Node:
    def __init__(self, lf, lidx, ridx):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx


def derive_fo_logits(function_name, arguments, fo_logits, funcs, vars):
    function_name = function_name[:-1]
    if function_name == 'const':
        return

    if function_name in {"loc_1", "req_exp_1", "req_deg_1", "platform_1",
                         "language_1", "application_1", "company_1", "recruiter_1",
                         "des_deg_1", "des_exp_1", "country_1", "title_1", "area_1"}:
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        job_var = vars['job']
        logit = "(%s %s %s)" % (function_name[:function_name.rindex("_")], job_var, value)
        fo_logits.append(logit)
    elif function_name in {"req_exp", "des_exp", "req_deg", "des_deg"}:
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is None
        job_var = vars['job']
        logit = "(%s %s)" % (function_name, job_var)
        fo_logits.append(logit)
    elif function_name in {"salary_greater_than", "salary_less_than"}:
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^(\d+),(year|hour|month|)$', argument_str)
        job_var = vars['job']
        logit = "(%s %s %s %s)" % (function_name, job_var,
                                   int(match.group(1)), match.group(2))
        fo_logits.append(logit)
    elif function_name in {"req_exp_0", "req_deg_0", "platform_0", "language_0", "company_0",
                           "des_exp_0", "title_0", "loc_0"}:
        # Exists
        vars['return_entity'] = "$1"
        job_var = vars['job']
        logit = "(%s %s %s)" % (function_name[:function_name.rindex("_")], job_var, "$1")
        fo_logits.append(logit)
        funcs.append("req_deg_0")
    elif function_name == 'job':
        job_var = vars['job']
        logit = "(%s %s)" % ("job", job_var)
        for l in fo_logits:
            if l == logit:
                break
        else:
            fo_logits.insert(0, logit)
    elif function_name == "not":
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        index = argument_str.index('(')
        child_function_name = argument_str[:index]
        match = re.match('^\(const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)\)$', argument_str[index:])
        if child_function_name in {'req_exp_1', 'area_1', 'loc_1', 'req_deg_1', 'language_1',
                                   'platform_1', 'company_1', 'area_1'}:
            job_var = vars['job']
            value = match.group(1)
            key = "(%s %s %s)" % (child_function_name[:child_function_name.rindex("_")], job_var, value)
        elif child_function_name in {"req_exp", "des_exp", "req_deg", "des_deg"}:
            job_var = vars['job']
            key = "(%s %s)" % (child_function_name, job_var)
        else:
            assert child_function_name == 'or'
            # raise Exception("Not other")

        if child_function_name != 'or':
            target_logit = None
            target_logit_idx = 0
            for fidx, logit in enumerate(fo_logits):
                if logit == key:
                    if target_logit is not None:
                        raise Exception("Only expect 1 logit")
                    target_logit = logit
                    target_logit_idx = fidx
            print(key)
            assert target_logit is not None
            fo_logits[target_logit_idx] = "(not_ %s)" % target_logit


def to_lc(lambda_fo_logits, lambda_func):
    if len(lambda_fo_logits) == 1:
        body = lambda_fo_logits[0]
    else:
        body = "(and_ %s)" % " ".join(lambda_fo_logits)
    if lambda_func == "job":
        lc = "(lambda $0:e %s)" % body
    else:
        lc = "(lambda $1:e (exists_ $0:e %s))" % body
    return lc


def translate(funql):
    funql_tokens = tokenize_funql(funql)

    # A list of four tuples (table, column, op, value)
    lambda_func = list()
    lambda_fo_logits = list()
    left_brackets = list()
    nodes = list()
    vars = {"job": "$0"}
    for tidx, token in enumerate(funql_tokens):
        if token.endswith('('):
            left_brackets.append(tidx)
        elif token == ')':
            pidx = left_brackets.pop()
            children_nodes = list()
            for nidx, node in enumerate(nodes):
                if pidx < node.lidx and tidx > node.ridx:
                    children_nodes.append(node)
            for n in children_nodes:
                nodes.remove(n)

            if len(children_nodes) == 0:
                sub_tokens = funql_tokens[pidx:tidx+1]
                function_name = sub_tokens[0]
                derive_fo_logits(
                    function_name, sub_tokens[1:], lambda_fo_logits,
                    lambda_func, vars
                )
                lf = "".join(sub_tokens)
            else:
                # Has children
                sub_tokens = funql_tokens[pidx:tidx+1]
                function_name = sub_tokens[0]
                _inside_bracket_stack = 0
                other_children = list()
                children_num = 0
                children_position = list()
                for sub_token in sub_tokens[1:]:
                    if sub_token.endswith('('):
                        _inside_bracket_stack += 1
                        if _inside_bracket_stack == 1:
                            children_num += 1
                            children_position.append('bracket')
                    elif sub_token == ')':
                        _inside_bracket_stack -= 1
                    else:
                        if _inside_bracket_stack == 0 and sub_token != ',':
                            children_num += 1
                            other_children.append(sub_token)
                            children_position.append('token')
                assert children_num == len(children_position)
                lf = "".join(sub_tokens)

                derive_fo_logits(
                    function_name, sub_tokens[1:], lambda_fo_logits,
                    lambda_func, vars
                )

            new_node = Node(lf, pidx, tidx)
            nodes.append(new_node)
    print(lambda_fo_logits)
    if len(lambda_func) == 0:
        lambda_func.append("job")
    assert len(lambda_func) == 1 and len(lambda_fo_logits) >= 1
    lc = to_lc(lambda_fo_logits, lambda_func[0])
    return lc


if __name__ == '__main__':
    questions, funqls = read_data('./job_funql_test_fixed.tsv')
    sorted_funqls = sorted([(q, lf) for q, lf in zip(questions, funqls)], key=lambda x: len(x[1]))
    with open("job_lambda_test.log", "w") as f:
        for idx, (question, funql) in enumerate(sorted_funqls):
            print(idx)
            print(question)
            print(funql)
            lc = translate(funql)
            print(lc)
            print("==\n\n")
            f.write("%s\n%s\n%s\n===\n\n" % (question, funql, lc))
