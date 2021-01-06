# coding=utf8

import re
import copy
from pprint import pprint
from lambda_calculus_to_prolog import FUNCTION_REPLACE_MAP


ENTITY_PATTERN = re.compile(r'^[A-Z|a-z|\\|_|\d]+:_([a-z]+)$')


ENTITY_TYPE_MAP = {
    "ac": "aircraft_code",
    "al": "airline_code",
    "ci": "city_name",
    "ap": "airport_code",
    "fn": "flight_number",
    "cl": "class_description",
    "ti": "time",
    "pd": "day_period",
    "mf": "manufacturer",
    "mn": "month",
    "da": "day",
    "i": "integer",
    "yr": "year",
    "dn": "day_number",
    "do": "dollar",
    "hr": "hour",
    "rc": "meal_code",
    "st": "state_name",
    "fb": "fare_basis_code",
    "me": "meal_description",
    "bat": "basis_type",
    "dc": "days_code"
}


def read_data(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            questions.append(splits[0])
            logical_forms.append(splits[1])
    return questions, logical_forms


def split_tokens(lf):
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        lf = lf.replace(a, b)
    return lf


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
                new_toks.append(new_name + ":" + var_type)
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
    lf = split_tokens(logical_form)
    lf = re.sub(' +', ' ', lf)
    s = standardize_lambda_calculus_varnames(lf)
    variables = ["$v0", "$v1", "$v2", "$v3"]
    for var in variables:
        s = s.replace(var + " e ", "%s:e " % var)
        s = s.replace(var + " i ", "%s:i " % var)
    s = s.replace(' :', ":").replace(
        '\s+', ' ').replace("( ", "(").replace(" )", ")").replace(')\s)', '))').strip().lower()
    s = re.sub(' +', ' ', s)
    return s


def extract_entity(lf):
    tokens = lf.split(":_")
    return tokens


def tokenize_logical_form(logical_form):
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        # ("\\+", " \\+ "),
    ]
    normalized_lc = re.sub(' +', ' ', logical_form)
    for a, b in replacements:
        normalized_lc = normalized_lc.replace(a, b)
    tokens = [t for t in normalized_lc.split()]
    return tokens


def is_var(string):
    return re.match('^[A-Z|a-z]$', string) is not None


def is_entity(string):
    match = ENTITY_PATTERN.match(string.replace('"', ""))
    return match is not None


class Node:
    def __init__(self, lf, lidx, ridx, input_vars=None, output_var=None):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx
        self.input_vars = input_vars
        self.output_var = output_var


def get_function_return_type(function_name):
    candidates = list()
    for _, funcs in FUNCTION_REPLACE_MAP.items():
        for f in funcs:
            if f['name'] == function_name:
                candidates.append(f['return_type'])
        if len(candidates) > 0:
            break
    if len(candidates) > 0:
        for t in candidates:
            if t != 'bool':
                return t
    return None


def process_entity_string(entity, default=""):
    assert isinstance(entity, str)
    if ":_" in entity:
        splits = entity.split(":_")
        entity_name = splits[0]
        entity_type = ENTITY_TYPE_MAP[splits[1]]
    else:
        entity_type = default
        entity_name = entity
    if '_' in entity_name:
        entity_name = entity_name.replace("_", " ")
    return entity_name, entity_type


def is_entity_function(function_name, number_of_arguments, arguments, variable_constraints):
    if function_name not in FUNCTION_REPLACE_MAP:
        assert function_name in ['_minutes_distant',
                                 '_named', '_overnight']
        if function_name == '_minutes_distant':
            return True
        return False

    names = FUNCTION_REPLACE_MAP[function_name]
    rewrite_function_name = function_name
    argument_types = None
    is_meta_function = False
    if len(names) == 1:
        rewrite_function_name = names[0]['name']
        argument_types = names[0]["argument_type"]
        is_meta_function = "is_meta" in names[0] and names[0]['is_meta'] is True
    else:
        # select by arugment number
        feasible_index = []
        for idx, name in enumerate(names):
            if name['number_of_argument'] == number_of_arguments:
                rewrite_function_name = name['name']
                argument_types = name["argument_type"]
                feasible_index.append(idx)
        if len(feasible_index) == 0:
            raise Exception("No feasible functions in Python")
        elif len(feasible_index) == 1:
            idx = feasible_index[0]
            rewrite_function_name = names[idx]['name']
            argument_types = names[idx]['argument_type']
            is_meta_function = "is_meta" in names[idx] and names[idx]['is_meta'] is True
        else:
            # Select by Argument Type
            best_index = 0
            best_count = 0
            for idx in feasible_index:
                name = names[idx]
                types = names[idx]['argument_type']
                count = 0
                for t, arg in zip(types, arguments):
                    _arg = arg.replace('"', "")
                    match = ENTITY_PATTERN.match(_arg)
                    if match:
                        e, et = process_entity_string(_arg)
                        if et == t:
                            count += 1
                    elif _arg.startswith("argmin_") or _arg.startswith("argmax_"):
                        # argmin, argmax
                        index = _arg.index("(") + 1
                        var = _arg[index:index+1]
                        if var in variable_constraints:
                            et = variable_constraints[var]
                            if et == t:
                                count += 1
                    else:
                        if is_var(_arg) and _arg in variable_constraints:
                            et = variable_constraints[_arg]
                            if et == t:
                                count += 1
                if count > best_count:
                    best_index = idx
                    best_count = count
            rewrite_function_name = names[best_index]['name']
            argument_types = names[best_index]['argument_type']
            is_meta_function = "is_meta" in names[best_index] and names[best_index]['is_meta'] is True


    # Variable Inference
    # Derive type constraints, Type Inference
    # print(function_name, rewrite_function_name, number_of_arguments, arguments, argument_types)
    assert number_of_arguments == len(argument_types)
    if is_meta_function:
        if rewrite_function_name in ['equals', 'numerical_equals', 'less_than', 'larger_than']:
            if is_var(arguments[0]):
                arg_variable = arguments[0]
                arg_func = arguments[1]
            elif is_var(arguments[1]):
                arg_variable = arguments[1]
                arg_func = arguments[0]
            else:
                arg_variable, arg_func = None, None
            if arg_variable is not None and arg_func is not None:
                match = ENTITY_PATTERN.match(arg_func.replace('"', ""))
                if match:
                    e, et = process_entity_string(arg_func.replace('"', ""))
                    variable_constraints[arg_variable] = et
                elif arg_func.startswith("argmin(") or arg_func.startswith("argmax("):
                    for _var in [" A:", " B:", " C:"]:
                        processed_var = _var.replace(":", "").strip()
                        if _var in arg_func and processed_var in variable_constraints:
                            variable_constraints[arg_variable] = variable_constraints[processed_var]
                            break
                else:
                    arg_func_return_type = get_function_return_type(
                        arg_func[:arg_func.index("(")])
                    if arg_func_return_type is not None and arg_func_return_type not in ['*', 'bool']:
                        variable_constraints[arg_variable] = arg_func_return_type
    else:
        for argument, atype in zip(arguments, argument_types):
            if is_var(argument):
                variable_constraints[argument] = atype

    candidates = list()
    for _, funcs in FUNCTION_REPLACE_MAP.items():
        for f in funcs:
            if f['name'] == rewrite_function_name:
                candidates.append(f['return_type'])
        if len(candidates) > 0:
            break
    if len(candidates) > 0:
        return candidates[0] != 'bool'
    else:
        return False


def rewrite(function_name, number_of_arguments, arguments, variable_constraints):
    is_entity_func = is_entity_function(function_name, number_of_arguments, arguments, variable_constraints)
    rewritten_function_name = function_name
    rewritten_arguments = list()
    argument_vars = list()
    for arg in arguments:
        if is_var(arg):
            argument_vars.append(1)
        else:
            argument_vars.append(0)
        # Rewrite argument
        if is_entity(arg):
            entity_name, entity_type = extract_entity(arg)
            rewritten_arguments.append('%s(%s)' % (ENTITY_TYPE_MAP[entity_type], entity_name))
        else:
            rewritten_arguments.append(arg)
    # print(number_of_arguments, sum(argument_vars), arguments, rewritten_arguments, is_var('airport_code(mke)'))
    output_variable = None
    input_variables = list()
    if number_of_arguments == 1:
        if sum(argument_vars) > 0:
            if is_entity_func:
                input_variables = rewritten_arguments
                output_variable = None
                expr = "%s(%s)" % (rewritten_function_name, rewritten_arguments[0])
            else:
                # predicate cast
                # TODO: fix
                input_variables = rewritten_arguments
                output_variable = None
                expr = "%s(all)" % rewritten_function_name
        else:
            # no variable
            input_variables = list()
            expr = "%s(%s)" % (rewritten_function_name, ",".join(rewritten_arguments))
    else:
        assert number_of_arguments == 2
        if sum(argument_vars) == number_of_arguments:
            # TODO: fix
            input_variables = rewritten_arguments
            expr = "%s(%s)" % (rewritten_function_name, ",".join(rewritten_arguments))
        elif sum(argument_vars) == 0:
            input_variables = list()
            expr = "%s(%s)" % (rewritten_function_name, ",".join(rewritten_arguments))

            if rewritten_function_name in ['_=', '_<', '_>']:
                print("Rewrite Meta Predicate (Equal, Less Than, larger than)")
                # ( _< ( _fare $0 ) 150:_do )
                for arg_idx, arg in enumerate(arguments):
                    if is_entity(arg):
                        entity_function_name = arguments[number_of_arguments - arg_idx - 1]
                        entity_function_name = entity_function_name[:entity_function_name.index('(')]
                        predicate = "%s%s_%d" % (rewritten_function_name,
                                                  entity_function_name, number_of_arguments - arg_idx)
                        expr = "%s(%s)" % (predicate, rewritten_arguments[arg_idx])
                        break
                else:
                    # No variable & No entity
                    # _>(_capacity(A),_capacity(_aircraft(_turboprop(all))))
                    child_func_1, child_func_2 = arguments[0], arguments[1]
                    child_func_name_1, child_func_name_2 = child_func_1[:child_func_1.index("(")], \
                                                           child_func_2[:child_func_2.index("(")]
                    assert child_func_name_1 == child_func_name_2
                    pattern = re.compile("%s\([A-Z]\)" % child_func_name_1)
                    child_1_match, child_2_match = pattern.match(child_func_1), pattern.match(child_func_2)
                    assert(child_1_match is not None) ^ (child_2_match is not None)
                    if child_1_match is not None:
                        index = 2
                        child = child_func_2
                    else:
                        index = 1
                        child = child_func_1
                    child = child_func_2[child_func_2.index("(")+1:-1]
                    predicate = "%s%s_%d" % (rewritten_function_name, child_func_name_1, index)
                    expr = "%s(%s)" % (predicate, child)
        else:
            index = argument_vars.index(1)
            input_variables = [rewritten_arguments[number_of_arguments - index - 1]]
            output_variable = rewritten_arguments[index]
            expr = "%s_%d(%s)" % (rewritten_function_name, number_of_arguments - index,
                                  rewritten_arguments[number_of_arguments - index - 1])
            if "%s_%d" % (rewritten_function_name, number_of_arguments - index) in ['_equals_2', '_equals_1']\
                and is_entity(arguments[number_of_arguments - index - 1]):
                expr = rewritten_arguments[number_of_arguments - index - 1]

    return expr, input_variables, output_variable


def rewrite_intersection(child_nodes, function_name):
    meta_predicate = "intersection" if function_name == '_and' else 'or'
    assert len(child_nodes) > 1
    _child_nodes = copy.copy(child_nodes)
    object_pattern = re.compile('([A-Z|a-z|:|_]+)\(all\)')
    object_cast = list()
    united_output_vars = set()
    object_united_input_vars = set()
    # Remove unary predicates
    for node in _child_nodes:
        if object_pattern.match(node.lf):
            object_cast.append(node)
            if node.input_vars is not None:
                object_united_input_vars |= set(node.input_vars)
        else:
            if node.output_var is not None and \
                    (not (node.lf.startswith("_=") or node.lf.startswith("_<") or node.lf.startswith("_>"))):
                united_output_vars.add(node.output_var)
    for n in object_cast:
        _child_nodes.remove(n)
    print(object_united_input_vars, united_output_vars)
    if len(object_united_input_vars) == 1 and len(united_output_vars) == 1 \
            and len(object_united_input_vars & united_output_vars) == 1:
        if len(_child_nodes) > 1:
            rewritten_lf = "%s(%s)" % (meta_predicate, ",".join([n.lf for n in _child_nodes]))
        else:
            rewritten_lf = "%s" % _child_nodes[0].lf
        for n in reversed(object_cast):
            predicate = n.lf[:n.lf.index('(')]
            rewritten_lf = "%s(%s)" % (predicate, rewritten_lf)
    elif len(object_united_input_vars) == 0:
        rewritten_lf = "%s(%s)" % (meta_predicate, ",".join([n.lf for n in _child_nodes]))
    elif len(united_output_vars) == 0 and len(object_united_input_vars) == 1:
        if meta_predicate == 'intersection':
            if len(_child_nodes) == 0:
                rewritten_lf = ""
                for idx, n in enumerate(reversed(object_cast)):
                    if idx == 0:
                        rewritten_lf = n.lf
                    else:
                        predicate = n.lf[:n.lf.index('(')]
                        rewritten_lf = "%s(%s)" % (predicate, rewritten_lf)
            else:
                if len(_child_nodes) > 1:
                    rewritten_lf = "intersection(%s)" % (",".join([n.lf for n in _child_nodes]))
                else:
                    rewritten_lf = "%s" % _child_nodes[0].lf
                for n in reversed(object_cast):
                    predicate = n.lf[:n.lf.index('(')]
                    rewritten_lf = "%s(%s)" % (predicate, rewritten_lf)
        else:
            # or
            rewritten_lf = "or(%s)" % (",".join([n.lf for n in child_nodes]))
    else:
        rewritten_lf = "%s(%s)" % (meta_predicate, ",".join([n.lf for n in child_nodes]))
    return rewritten_lf


def replace_sub_lf(main_lf, replace_lf):
    result = main_lf.replace(replace_lf + ",", "")
    result = result.replace("," + replace_lf, "")
    result = result.replace(replace_lf, "")
    return result


def transform_lambda_calculus(logical_form):
    normalized_lf = normalize_lambda_calculus(logical_form)
    # Replace Variable
    normalized_lf = normalized_lf.replace('$v0:e ', 'A ')
    normalized_lf = normalized_lf.replace('$v1:e ', 'B ')
    normalized_lf = normalized_lf.replace('$v2:e ', 'C ')
    normalized_lf = normalized_lf.replace('$v3:e ', 'D ')
    normalized_lf = normalized_lf.replace('$v0:i ', 'A ')
    normalized_lf = normalized_lf.replace('$v1:i ', 'B ')
    normalized_lf = normalized_lf.replace('$v2:i ', 'C ')
    normalized_lf = normalized_lf.replace('$v3:i ', 'D ')
    normalized_lf = normalized_lf.replace('$v0', 'A')
    normalized_lf = normalized_lf.replace('$v1', 'B')
    normalized_lf = normalized_lf.replace('$v2', 'C')
    normalized_lf = normalized_lf.replace('$v3', 'D')
    normalized_lf = re.sub(' +', ' ', normalized_lf)

    # Translate
    if normalized_lf.count('(') == 0:
        # Simple Cases, A single entity
        entity_name, entity_type = extract_entity(normalized_lf)
        funql = 'answer(%s(%s))' % (
            ENTITY_TYPE_MAP[entity_type], entity_name)
    else:
        left_brackets = list()
        tokens = tokenize_logical_form(normalized_lf)
        global_variable_constraints = dict()
        nodes = list()
        for tidx, token in enumerate(tokens):
            if token == '(':
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
                    sub_tokens = tokens[pidx + 1:tidx]
                    function_name = sub_tokens[0]
                    number_of_arguments = len(sub_tokens[1:])
                    rewritten_lf, input_vars, output_var = rewrite(
                        function_name, number_of_arguments, sub_tokens[1:],
                        global_variable_constraints
                    )
                else:
                    # Has children
                    sub_tokens = tokens[pidx + 1:tidx]
                    function_name = sub_tokens[0]
                    _inside_bracket_stack = 0
                    other_children = list()
                    children_num = 0
                    children_position = list()
                    for sub_token in sub_tokens[1:]:
                        if sub_token == '(':
                            _inside_bracket_stack += 1
                            if _inside_bracket_stack == 1:
                                children_num += 1
                                children_position.append('bracket')
                        elif sub_token == ')':
                            _inside_bracket_stack -= 1
                        else:
                            if _inside_bracket_stack == 0:
                                children_num += 1
                                other_children.append(sub_token)
                                children_position.append('token')
                    assert children_num == len(children_position)
                    string = list()

                    if function_name == '_lambda':
                        assert len(other_children) == 1 and len(children_nodes) == 1
                        child_node = children_nodes.pop(0)
                        rewritten_lf = child_node.lf
                        input_vars = child_node.input_vars
                        output_var = child_node.output_var
                    elif function_name in ['_argmin', '_argmax', '_sum']:
                        assert len(other_children) == 1 and len(
                            children_nodes) == 2
                        variable = other_children.pop(0)
                        node_1, node_2 = children_nodes.pop(
                            0), children_nodes.pop(0)
                        entity_function = node_2.lf[:node_2.lf.index('(')]
                        predicate_name = "%s%s" % (function_name[1:], entity_function)
                        rewritten_lf = "%s(%s)" % (
                            predicate_name, node_1.lf)
                        output_var = variable
                        input_vars = list()
                    elif function_name == '_count':
                        assert len(other_children) == 1 and len(children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        input_vars = list()
                        output_var = None
                        rewritten_lf = "count(%s)" % (child_node.lf)
                    elif function_name == '_exists':
                        assert len(other_children) == 1 and len(
                            children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        rewritten_lf = "%s" % child_node.lf
                        input_vars = child_node.input_vars
                        output_var = child_node.output_var

                        match_count = 0
                        # Match predicates with two variable
                        pattern_1 = re.compile("(([A-Z|a-z|:|_]+)\(([A-Z|a-z]),([A-Z|a-z])\))")
                        results = pattern_1.findall(child_node.lf)
                        if len(results) > 0 and len(results) == 1:
                            match_count += 1
                            print("Exists Match predicates with two variable")
                            assert len(results) == 1 and variable in global_variable_constraints
                            result = results[0]
                            replace_predicate = result[0]
                            child_lf = replace_sub_lf(child_node.lf, replace_predicate)
                            target_index = result.index(variable) - 1
                            rewritten_lf = "%s_%d(%s)" % (result[1], target_index, child_lf)
                            print(rewritten_lf)

                        pattern_2 = re.compile("(((_=|_<|_>)_[1|2])\(([_|A-Z|a-z|:|\d]+)\(([A-Z])\)\))")
                        results = pattern_2.findall(child_node.lf)
                        if len(results) > 0:
                            match_count += 1
                            print("Exists Match Meta Predicate", len(results))
                            print(results)
                            assert len(results) in [1, 2] and variable in global_variable_constraints
                            if len(results) == 1:
                                result = results[0]
                                replace_predicate = result[0]
                                child_lf = replace_sub_lf(child_node.lf, replace_predicate)
                                if child_lf == '':
                                    if global_variable_constraints[variable] == 'flight_id':
                                        child_lf = '_flight(all)'
                                print(child_lf)
                                assert len(child_lf) > 0 and result[-1] == variable and result[2] == '_='
                                rewritten_lf = "%s(%s)" % (result[3], child_lf)
                            else:
                                # TODO: manually fixed
                                print("TODO: manually fixed")
                        print("Exists Match Count: %d" % match_count)

                    elif function_name  == '_the':
                        assert len(other_children) == 1 and len(
                            children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        rewritten_lf = "%s" % child_node.lf
                        input_vars = child_node.input_vars
                        output_var = child_node.output_var
                    elif function_name in ['_max', '_min']:
                        assert len(other_children) == 1 and len(
                            children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        child_lf = child_node.lf
                        rewritten_lf = "%s(%s)" % (function_name, child_lf)
                        input_vars = list()
                        output_var = None
                    elif function_name in ['_and', '_or']:
                        child_node_count = 0
                        output_var = children_nodes[0].output_var
                        input_vars = list()
                        rewritten_lf = rewrite_intersection(children_nodes, function_name)
                    elif function_name == '_not':
                        assert len(children_position) == 1 and len(children_nodes) == 1
                        child_node = children_nodes.pop(0)
                        rewritten_lf = "not(%s)" % (child_node.lf)
                        input_vars, output_var = child_node.input_vars, child_node.output_var
                    else:
                        for position in children_position:
                            if position == 'bracket':
                                n = children_nodes.pop(0)
                                string.append(n.lf)
                            else:
                                sub_token = other_children.pop(0)
                                string.append(sub_token)
                        rewritten_lf, input_vars, output_var = rewrite(function_name, children_num, string,
                                                                       global_variable_constraints)
                new_node = Node(rewritten_lf, pidx, tidx, input_vars=input_vars, output_var=output_var)
                nodes.append(new_node)
            else:
                if tidx > 0 and (not tokens[tidx - 1] == '(') and ":_" in token:
                    # token is not function name
                    tokens[tidx] = '%s' % tokens[tidx]
        assert len(nodes) == 1
        funql = nodes[0].lf

        funql = "answer(%s)" % funql

    return funql


def tokenize_funql(funql):
    normalized_lf = funql.replace(" ", "::")
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        (',', ' , '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    tokens = [t if "::" not in t else t.replace("::", " ") for t in normalized_lf.split()]
    return tokens


def is_correct_funql(funql):
    tokens = tokenize_funql(funql)
    if funql.count(")") != funql.count("("):
        return False
    if "()" in funql:
        print("Empty Object")
        return False
    for token in tokens:
        if re.match('[A-Z]', token):
            return False
    return True


def tokenize_funql_2(funql):
    normalized_lf = funql.replace(" ", "::")
    replacements = [
        ('(', '( '),
        (')', ' ) '),
        (',', ' , '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    tokens = [t if "::" not in t else t.replace("::", " ") for t in normalized_lf.split()]
    return tokens


class FunQLNode:
    def __init__(self, lf, lidx, ridx, function_name):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx
        self.function_name = function_name
        self.children = list()


def fix_funql_intersection(funql):
    # Build FunQL Tree
    left_brackets = list()
    funql_tokens = tokenize_funql_2(funql)
    nodes = list()
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

            sub_lf = "".join(funql_tokens[pidx:tidx+1])
            function_name = funql_tokens[pidx][:-1]
            if len(children_nodes) == 0:
                function_name = sub_lf
            node = FunQLNode(sub_lf, pidx, tidx, function_name)
            for child in children_nodes:
                node.children.append(child)
            nodes.append(node)
        tidx += 1
    assert len(nodes) == 1 and nodes[0].lf == funql
    node = nodes[0]

    def _fix(node):
        # Fix intersection
        for cidx, child in enumerate(node.children):
            if child.lf.startswith("intersection") and len(child.children) == 1:
                print("Problematic Intersection")
                node.children[cidx] = child.children[0]
            _fix(child)
    _fix(node)

    # Get fixed funql
    def _aggregate(node):
        if len(node.children) == 0:
            node_lf = node.function_name
        else:
            child_lf = list()
            for child in node.children:
                child_lf.append(_aggregate(child))
            node_lf = "%s(%s)" % (node.function_name, ",".join(child_lf))
        return node_lf

    fixed_funql = _aggregate(node)
    return fixed_funql


def simplify_funql_object_predicates(funql):
    funql = funql.replace("_economy(all)", "_economy(_flight(all))")
    funql = funql.replace("_nonstop(all)", "_nonstop(_flight(all))")
    funql = funql.replace("_connecting(all)", "_connecting(_flight(all))")
    funql = funql.replace("_limousine(all)", "_limousine(_ground_transport(all))")
    funql = funql.replace("_taxi(all)", "_taxi(_ground_transport(all))")
    funql = funql.replace("_oneway(all)", "_oneway(_flight(all))")
    funql = funql.replace("_round_trip(all)", "_round_trip(_flight(all))")
    funql = funql.replace("_aircraft(_turboprop(all))", "_turboprop(_aircraft(all))")
    funql = funql.replace("_turboprop(all)", "_turboprop(_aircraft(all))")
    funql = funql.replace("_aircraft_code:_t(all)", "_aircraft(all)")
    funql = funql.replace("_meal:_t(all)", "_meal_code(all)")
    return funql


if __name__ == '__main__':
    questions, logical_forms = read_data(
        './atis_lambda_train.tsv')

    all_object_predicates = set()
    sorted_logical_forms = sorted([(q,lf,) for q, lf in zip(questions, logical_forms)], key=lambda x: len(x[1]))
    # with open("atis_funql_test.log", "w") as f:
    for lidx, (question, lf) in enumerate(sorted_logical_forms):
        print(lidx)
        print(question)
        print(lf)
        funql = transform_lambda_calculus(lf)
        funql = fix_funql_intersection(funql)
        funql = simplify_funql_object_predicates(funql)
        print(funql)

        # Find all object predicates
        all_object_pattern = re.compile('([_|a-z|\d|:]+)\(all\)')
        results = all_object_pattern.findall(funql)
        for result in results:
            all_object_predicates.add(result)
        print("===\n\n")
        # if not is_correct_funql(funql):
            # f.write("Incorrect FunQL\n")
            # f.write("%s\n%s\n%s\n===\n\n" % (question, lf, funql))
    pprint(all_object_predicates)