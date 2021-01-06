# coding=utf


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


def tokenize_funql(funql):
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


def transform(funql):
    expression = funql
    tokens = tokenize_funql(expression)
    print(tokens)
    all_entity_types = {"%s(" % value for _, value in ENTITY_TYPE_MAP.items()}

    transformed_tokens = list()
    tidx = 0
    while tidx < len(tokens):
        token = tokens[tidx]
        if token in all_entity_types and tidx + 2 < len(tokens) and tokens[tidx + 2] == ')':
            transformed_tokens.append("build_entity(")
            transformed_tokens.append('"%s"' % token[:-1])
            transformed_tokens.append(",")
            transformed_tokens.append('"%s"' % tokens[tidx + 1])
            transformed_tokens.append(")")
            tidx += 3
        elif token == 'all':
            print(transformed_tokens)
            print(token, transformed_tokens[-1], tokens[tidx + 1])
            assert transformed_tokens[-1].endswith('(') and tokens[tidx + 1] == ')'
            transformed_tokens[-1] = "%s_all(" % transformed_tokens[-1][:-1]
            tidx += 1
        else:
            if token.startswith('_'):
                token = token[1:]
            if token in ['count(', 'min(', 'or(', 'not(', 'max(']:
                token = token.replace("(", "_(")
            token = token.replace(":_", "_").replace("<_", "less_than_").replace(">_", "larger_than_")
            transformed_tokens.append(token)
            tidx += 1
    expression = "".join(transformed_tokens)
    return expression


if __name__ == '__main__':
    funql = "answer(_flight(intersection(_to_2(airport_code(dal)),_from_2(_airport(all)))))"
    expression = transform(funql)
    print(expression)

    # data = list()
    # with open('../../../data/atis/atis_funql_test.tsv', 'r') as f:
    #     for line in f:
    #         line = line.strip()
    #         data.append(line.split('\t'))
    # for idx, (question, funql) in enumerate(data):
    #     print(idx)
    #     print(question)
    #     print(funql)
    #     expression = transform(funql)
    #     print(expression)
    #     print('====\n\n')
