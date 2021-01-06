# coding=utf8


import re


def tokenize_prolog(logical_form):
    # Tokenize Prolog
    normalized_lf = logical_form.replace(" ", "::")
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        (',', ' , '),
        (';', ' ; '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    toks = [t if "::" not in t else t.replace(
        "::", " ") for t in normalized_lf.split()]
    return toks


def standardize_prolog_varnames(prolog):
    toks = tokenize_prolog(prolog)
    varnames = {}
    new_toks = []
    for t in toks:
        if re.match('^[A-Z]$', t) or re.match('^_\d+$', t):
            if t in varnames:
                new_toks.append(varnames[t])
            else:
                new_varname = chr(ord('A')+len(varnames))
                varnames[t] = new_varname
                new_toks.append(new_varname)
        else:
            new_toks.append(t)
    lf = ''.join(new_toks)
    lf = lf.replace('\\+ (', '\+(')
    return lf


def read_data(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            questions.append(splits[0])
            logical_forms.append(standardize_prolog_varnames(splits[1]))
    return questions, logical_forms


def tokenize_prolog_2(funql):
    normalized_lf = funql.replace(" ", "::")
    replacements = [
        ('(', '( '),
        (')', ' ) '),
        (',', ' , '),
        (';', ' ; '),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    tokens = [t.strip() if "::" not in t else t.replace("::", " ").strip() for t in normalized_lf.split()]
    return tokens


class Node:
    def __init__(self, lf, lidx, ridx, input_vars=None, output_var=None):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx
        self.input_vars = input_vars
        self.output_var = output_var


def is_var(t):
    return re.match('^[A-Z]$', t) or re.match('^_\d+$', t)


def rewrite(function_name, arguments, variable_constraints):

    rewritten_function_name = function_name[:-1]
    valid_arguments = [arg for arg in arguments if arg != ',']
    number_of_arguments = len(valid_arguments)
    argument_vars = list()
    for arg in valid_arguments:
        if is_var(arg):
            argument_vars.append(1)
        else:
            argument_vars.append(0)
    output_variable = None
    input_variables = list()
    if number_of_arguments == 1:
        if sum(argument_vars) == 0:
            raise Exception("No unary entity predicate")
        else:
            # no variable
            input_variables = valid_arguments
            output_variable = valid_arguments[0]
            expr = "%s(all)" % rewritten_function_name
    else:
        # 2 or 3
        if sum(argument_vars) == number_of_arguments:
            # TODO: fix
            input_variables = valid_arguments
            expr = "%s(%s)" % (rewritten_function_name, ",".join(valid_arguments))
        elif sum(argument_vars) == 0:
            raise Exception("No binary entity predicate")
        else:
            assert sum(argument_vars) == 1
            # At least one argument vars
            index = argument_vars.index(1)
            input_variables = valid_arguments
            output_variable = valid_arguments[index]
            valid_arguments.remove(valid_arguments[index])
            expr = "%s(%s)" % (rewritten_function_name, ",".join(valid_arguments))
    return expr, input_variables, output_variable


def rewrite_intersection(nodes):

    input_vars = list()
    output_var = None
    for n in nodes:
        if n.output_var is not None:
            output_var = n.output_var
            break

    # Merge Const
    const_nodes = list()
    for node in nodes:
        if node.lf.startswith('const('):
            const_nodes.append(node)
    for cn in const_nodes:
        nodes.remove(cn)
    # Merge
    for cn in const_nodes:
        assert cn.output_var is not None
        for node in nodes:
            if node.input_vars is not None \
                    and cn.output_var in node.input_vars:
                tokens = [t for t in tokenize_prolog_2(node.lf) if t != ',']
                for tidx, t in enumerate(tokens):
                    if is_var(t) and tokens[tidx] == cn.output_var:
                        tokens[tidx] = cn.lf
                        break
                if len(node.input_vars) == 2:
                    node.lf = '%s_%d(%s)' % (tokens[0][:-1], tidx - 1, cn.lf)
                    index = 1 - node.input_vars.index(cn.output_var)

                    node.output_var = node.input_vars[index]
                    output_var = node.output_var
                    # print("Rewrite Output Var: ", node.output_var)
                else:
                    node.lf = ''.join(tokens)
                break

    is_all_same = True
    prev_output_var = None
    for nidx, node in enumerate(nodes):
        if nidx == 0:
            prev_output_var = node.output_var
        else:
            if node.output_var is None or node.output_var != prev_output_var:
                is_all_same = False
                break

    unary_predicate_nodes = list()
    if is_all_same:
        # Take job(all) first
        for node in nodes:
            if node.lf.endswith('(all)'):
                unary_predicate_nodes.append(node)
        for un in unary_predicate_nodes:
            nodes.remove(un)
        unary_predicate_nodes = unary_predicate_nodes[::-1]

    if len(unary_predicate_nodes) > 0:
        if len(nodes) == 0:
            rewritten_lf = unary_predicate_nodes[0].lf
            for un in unary_predicate_nodes[1:]:
                tokens = tokenize_prolog_2(un.lf)
                rewritten_lf = "%s(%s)" % (tokens[0][:-1], rewritten_lf)
        else:
            if len(nodes) == 1:
                rewritten_lf = nodes[0].lf
            else:
                rewritten_lf = "%s(%s)" % ("intersect", ",".join([n.lf for n in nodes]))
            for un in unary_predicate_nodes:
                tokens = tokenize_prolog_2(un.lf)
                rewritten_lf = "%s(%s)" % (tokens[0][:-1], rewritten_lf)
    else:
        assert len(nodes) > 0
        if len(nodes) == 1:
            rewritten_lf = nodes[0].lf
        else:
            rewritten_lf = "%s(%s)" % ("intersect", ",".join([n.lf for n in nodes]))

    return rewritten_lf, input_vars, output_var


def translate(prolog):
    left_brackets = list()
    tokens = tokenize_prolog_2(prolog)
    # print(tokens)
    global_variable_constraints = dict()
    nodes = list()
    for tidx, token in enumerate(tokens):
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

            # Rewrite
            # FunQL has a very nested structure
            if len(children_nodes) == 0:
                sub_tokens = tokens[pidx:tidx]
                function_name = sub_tokens[0]
                rewritten_lf, input_vars, output_var = rewrite(
                    function_name, sub_tokens[1:],
                    global_variable_constraints
                )
            else:
                # Has children
                sub_tokens = tokens[pidx:tidx]
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

                if function_name == '(':
                    if ';' in other_children:
                        meta = 'or'
                    else:
                        meta = 'intersect'
                    if meta == 'intersect':
                        rewritten_lf, input_vars, output_var = rewrite_intersection(children_nodes)
                    else:
                        output_var = children_nodes[0].output_var
                        input_vars = list()
                        rewritten_lf = "%s(%s)" % (meta, ",".join([n.lf for n in children_nodes]))
                elif function_name == '\\+(':
                    output_var = children_nodes[0].output_var
                    input_vars = list()
                    rewritten_lf = "%s(%s)" % ("not", ",".join([n.lf for n in children_nodes]))
                    # print("Not: ", input_vars, output_var)
                else:
                    arguments = list()
                    for position in children_position:
                        if position == 'bracket':
                            n = children_nodes.pop(0)
                            arguments.append(n.lf)
                        else:
                            sub_token = other_children.pop(0)
                            arguments.append(sub_token)
                    rewritten_lf, input_vars, output_var = rewrite(
                        function_name, arguments,
                        global_variable_constraints
                    )
            new_node = Node(rewritten_lf, pidx, tidx, input_vars=input_vars, output_var=output_var)
            nodes.append(new_node)
    assert len(nodes) == 1
    funql = nodes[0].lf
    return funql


def tokenize_funql(funql):
    normalized_lf = funql.replace(" ", "::")
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        (',', ' , '),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    tokens = [t if "::" not in t else t.replace("::", " ") for t in normalized_lf.split()]
    return tokens


def validate(funql):
    tokens = tokenize_funql(funql)
    for token in tokens:
        if is_var(token):
            return False
    return True


if __name__ == '__main__':
    questions, prologs = read_data('./job_prolog_train.tsv')
    sorted_prologs = sorted([(q, lf) for q, lf in zip(questions, prologs)], key=lambda x: len(x[1]))
    with open("job_funql_train.log", "w") as f:
        for idx, (question, prolog) in enumerate(sorted_prologs):
            print(idx)
            print(question)
            print(prolog)
            funql = translate(prolog)
            is_valid = validate(funql)
            print("Is Valid: ", is_valid)
            print(funql)
            print('===\n\n')
            if not is_valid:
                f.write("Incorrect FunQL\n")
                f.write("%s\n%s\n%s\n===\n\n" % (question, prolog, funql))
            else:
                f.write("%s\n%s\n%s\n===\n\n" % (question, prolog, funql))

