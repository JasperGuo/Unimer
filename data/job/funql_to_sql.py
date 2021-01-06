# coding=utf8

import re
import mysql.connector


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="job",
    auth_plugin='mysql_native_password'
)


def get_result(sql):
    _sql = sql
    cursor = db.cursor()
    cursor.execute(_sql)
    # print(cursor.description)
    headers = cursor.description
    results = cursor.fetchall()
    return results


def is_country_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"canada"']:
        return True
    sql = "SELECT DISTINCT country FROM country WHERE country = %s" % query_value
    return len(get_result(sql)) > 0


def is_city_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"texas"', '"boston"', '"washington"', '"tulsa"',
                       '"new york"', '"los alamos"', '"seattle"', '"nashville"',
                       '"california"', '"colorado"', '"san jose"']:
        return True
    sql = "SELECT DISTINCT city_name FROM city WHERE city_name = %s" % query_value
    return len(get_result(sql)) > 0


def is_degree_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"BACS"', '"MSEE"', '"master"', '"MBA"', '"MA"']:
        return True
    sql = "SELECT DISTINCT job_id FROM job WHERE req_deg = %s or des_deg = %s" % (query_value, query_value)
    return len(get_result(sql)) > 0


def is_language_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"fortran"', '"cobol ii"', '"visual j++"', '"haskell"',
                       '"lisp"', '"pascal"', '"ada"', '"latex"', '"prolog"',
                       '"oracle"']:
        return True
    sql = "SELECT DISTINCT language FROM language WHERE language = %s" % query_value
    return len(get_result(sql)) > 0


def is_platform_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"pdp11"', '"silicon graphics"', '"x86"', '"linux"', '"commodores"']:
        return True
    sql = "SELECT DISTINCT platform FROM platform WHERE platform = %s" % query_value
    return len(get_result(sql)) > 0


def is_application_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"autocad"', '"microsoft word"', '"apache"', '"speedy3dgraphics"']:
        return True
    sql = "SELECT DISTINCT application FROM application WHERE application = %s" % query_value
    return len(get_result(sql)) > 0


def is_company_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"Microsoft"', '"JPL"', '"Dell"', '"Trilogy"', '"ibm"',
                       '"IBM"', '"HP"', '"Apple"', '"National Instruments"', '"Boeing"',
                       '"Lockheed Martin Aeronautics"', '"Compaq"', '"Applied Materials"']:
        return True
    sql = "SELECT DISTINCT company FROM job WHERE company = %s" % query_value
    return len(get_result(sql)) > 0


def is_recruiter_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"Longhorn"', '"Phil Smith"']:
        return True
    sql = "SELECT DISTINCT recruiter FROM job WHERE recruiter = %s" % query_value
    return len(get_result(sql)) > 0


def is_title_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"Ic Design Engineer"', '"Test Engineer"', '"research assistant"',
                       '"Sql Engineer"', '"Senior Consulting Engineer"',
                       '"NetWare Administrator"', '"Senior Development Engineer"',
                       '"Manufacturing Manager"', '"intern"', '"Consultant"']:
        return True
    sql = "SELECT DISTINCT title FROM job WHERE title = %s" % query_value
    return len(get_result(sql)) > 0


def is_area_value(value):
    if '"' in value:
        query_value = value
    else:
        query_value = '"%s"' % value
    if query_value in ['"ai"', '"statistics"', '"oil pipeline modeling"', '"management"']:
        return True
    sql = "SELECT DISTINCT area FROM area WHERE area = %s" % query_value
    return len(get_result(sql)) > 0


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


def derive_filters(function_name, arguments, filters, select):
    function_name = function_name[:-1]
    if function_name == 'const':
        return

    # Filters
    if function_name == 'loc_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_city_value(value) or is_country_value(value)
        if is_country_value(value):
            filters.append(('country', 'country', '=', value))
        else:
            filters.append(('city', 'city_name', '=', value))
    elif function_name == 'req_exp_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert re.match('^\d+$', value)
        filters.append(('job', 'req_exp', '=', int(value)))
    elif function_name == 'req_deg_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_degree_value(value)
        filters.append(('job', 'req_deg', '=', value))
    elif function_name == 'platform_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_platform_value(value)
        filters.append(('platform', 'platform', '=', value))
    elif function_name == 'language_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_language_value(value)
        filters.append(('language', 'language', '=', value))
    elif function_name == 'application_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_application_value(value)
        filters.append(('application', 'application', '=', value))
    elif function_name == 'company_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_company_value(value)
        filters.append(('job', 'company', '=', value))
    elif function_name == 'recruiter_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_recruiter_value(value)
        filters.append(('job', 'recruiter', '=', value))
    elif function_name == 'des_deg_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_degree_value(value)
        filters.append(('job', 'des_deg', '=', value))
    elif function_name == 'des_exp_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert re.match('^\d+$', value)
        filters.append(('job', 'des_exp', '=', int(value)))
    elif function_name == 'country_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_country_value(value)
        filters.append(('country', 'country', '=', value))
    elif function_name == 'title_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_title_value(value)
        filters.append(('job', 'title', '=', value))
    elif function_name == 'area_1':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is not None
        value = match.group(1)
        assert is_area_value(value)
        filters.append(('area', 'area', '=', value))
    # Unary
    elif function_name == 'req_exp':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^\d+$', argument_str)
        assert match is None
        filters.append(('job', 'req_exp', 'is not', 'NULL'))
    elif function_name == 'des_exp':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^\d+$', argument_str)
        assert match is None
        filters.append(('job', 'des_exp', 'is not', 'NULL'))
    elif function_name == 'req_deg':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is None
        filters.append(('job', 'req_deg', 'is not', 'NULL'))
    elif function_name == 'des_deg':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)$', argument_str)
        assert match is None
        filters.append(('job', 'des_deg', 'is not', 'NULL'))
    elif function_name == 'salary_greater_than':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^(\d+),(year|hour|month|)$', argument_str)
        filters.append(('salary', 'money', '>=', int(match.group(1))))
        filters.append(('salary', 'time', '=', match.group(2)))
    elif function_name == 'salary_less_than':
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        match = re.match('^(\d+),(year|hour|month|)$', argument_str)
        filters.append(('salary', 'money', '<=', int(match.group(1))))
        filters.append(('salary', 'time', '=', match.group(2)))
    # Alter select
    elif function_name == 'req_exp_0':
        # Return experience
        select.append(('job', 'req_exp'))
    elif function_name == 'req_deg_0':
        # Return experience
        select.append(('job', 'req_deg'))
    elif function_name == 'platform_0':
        # Return experience
        select.append(('platform', 'platform'))
    elif function_name == 'language_0':
        select.append(('language', 'language'))
    elif function_name == 'company_0':
        select.append(('job', 'company'))
    elif function_name == 'des_exp_0':
        select.append(('job', 'des_exp'))
    elif function_name == 'title_0':
        select.append(('job', 'title'))
    elif function_name == 'loc_0':
        select.append(('city', 'city_name'))
    elif function_name == "not":
        argument_str = "".join(arguments[:-1]).replace("'", '"')
        index = argument_str.index('(')
        child_function_name = argument_str[:index]
        match = re.match('^\(const\((["|a-z|A-Z|_|\d|_|\s|\+|/]+)\)\)$', argument_str[index:])
        if child_function_name == 'req_exp_1':
            value = match.group(1)
            key = ('job', 'req_exp', int(value))
        elif child_function_name == 'req_deg':
            key = ('job', 'req_deg',)
        elif child_function_name == 'area_1':
            value = match.group(1)
            key = ('area', 'area', value)
        elif child_function_name == 'loc_1':
            value = match.group(1)
            key = ('city', 'city_name', value)
        elif child_function_name == 'req_deg_1':
            value = match.group(1)
            key = ('job', 'req_deg', value)
        elif child_function_name == 'language_1':
            value = match.group(1)
            print("Language Not Value: ", value)
            key = ('language', 'language', value)
        elif child_function_name == 'platform_1':
            value = match.group(1)
            key = ('platform', 'platform', value)
        elif child_function_name == 'company_1':
            value = match.group(1)
            key = ('job', 'company', value)
        elif child_function_name == 'req_exp':
            key = ('job', 'req_exp')
        elif child_function_name == 'area_1':
            value = match.group(1)
            key = ('area', 'area', value)
        else:
            assert child_function_name == 'or'
            # raise Exception("Not other")

        if child_function_name != 'or':
            target_filter = None
            target_filter_idx = 0
            for fidx, filter in enumerate(filters):
                if filter[0] == key[0] and filter[1] == key[1]:
                    if len(key) == 3:
                        if filter[-1] == key[-1]:
                            if target_filter is not None:
                                raise Exception("Only expect 1 filter")
                            target_filter = filter
                            target_filter_idx = fidx
                    else:
                        if target_filter is not None:
                            raise Exception("Only expect 1 filter")
                        target_filter = filter
                        target_filter_idx =fidx

            print(key)
            assert target_filter is not None
            op = target_filter[-2]
            not_filter = None
            if op == '=':
                not_filter = (target_filter[0], target_filter[1], "!=", target_filter[-1])
            elif op == 'is not':
                not_filter = (target_filter[0], target_filter[1], "is", target_filter[-1])
            elif op == '>':
                not_filter = (target_filter[0], target_filter[1], "is", "NULL")
            assert not_filter is not None
            filters[target_filter_idx] = not_filter


class Node:
    def __init__(self, lf, lidx, ridx):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx


def to_sql(select, filters):
    select_clause = "SELECT DISTINCT %s.%s" % (select[0][0], select[0][1])
    where_clause = list()
    tables = {select[0][0]}
    for filter in filters:
        tables.add(filter[0])
        value = filter[-1]
        if isinstance(value, str) and value != 'NULL':
            if '"' in value:
                query_value = value
            else:
                query_value = '"%s"' % value
        else:
            query_value = value
        clause = "%s.%s %s %s" % (filter[0], filter[1], filter[2], query_value)
        where_clause.append(clause)
    where_clause = " AND ".join(where_clause)

    if "job" not in tables:
        tables.add("job")
    assert "job" in tables
    # from clause
    tables = sorted(list(tables))
    tables.remove("job")
    tables = ['job'] + tables

    if len(tables) == 1:
        from_clause = "job"
    else:
        from_clause = ""
        for tidx, t in enumerate(tables):
            if tidx == 0:
                continue
            elif tidx == 1:
                from_clause = "job JOIN %s ON job.job_id = %s.job_id" % (t, t)
            else:
                from_clause += " JOIN %s ON job.job_id = %s.job_id" % (t, t)

    if len(where_clause) > 0:
        sql = select_clause + " FROM " + from_clause + " WHERE " + where_clause
    else:
        sql = select_clause + " FROM " + from_clause
    return sql


def translate(funql):
    funql_tokens = tokenize_funql(funql)

    # A list of four tuples (table, column, op, value)
    sql_select = list()
    sql_where = list()
    left_brackets = list()
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

            if len(children_nodes) == 0:
                sub_tokens = funql_tokens[pidx:tidx+1]
                function_name = sub_tokens[0]
                derive_filters(
                    function_name, sub_tokens[1:], sql_where, sql_select
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

                derive_filters(
                    function_name, sub_tokens[1:], sql_where, sql_select
                )

            new_node = Node(lf, pidx, tidx)
            nodes.append(new_node)

    print(sql_where)
    if len(sql_select) == 0:
        sql_select.append(("job", "job_id"))
    print(sql_select)
    assert len(sql_select) == 1

    sql = to_sql(sql_select, sql_where)
    print(sql)
    return sql


if __name__ == '__main__':
    questions, prologs = read_data('./job_funql_test_fixed.tsv')
    sorted_prologs = sorted([(q, lf) for q, lf in zip(questions, prologs)], key=lambda x: len(x[1]))
    with open("job_sql_test.log", "w") as f:
        for idx, (question, prolog) in enumerate(sorted_prologs):
            print(idx)
            print(question)
            print(prolog)
            sql = translate(prolog)
            print("==\n\n")
            f.write("%s\n%s\n%s\n===\n\n" % (question, prolog, sql))
