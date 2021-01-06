# coding=utf8


def read_data():
    questions, logical_forms = list(), list()
    paths = [
        "../../data/atis/atis_funql_train.tsv",
        "../../data/atis/atis_funql_dev.tsv",
        "../../data/atis/atis_funql_test.tsv"]
    for p in paths:
        with open(p, "r") as f:
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
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    tokens = [t if "::" not in t else t.replace("::", " ") for t in normalized_lf.split()]
    return tokens


def get_relations(logical_forms):
    relations = set()
    meta_relations = set()
    for lf in logical_forms:
        tokens = tokenize_funql(lf)
        for token in tokens:
            if token.endswith("(") and token[:-1] not in ['intersection', 'or', 'not']:
                if token.startswith('argmax') or token.startswith('argmin') \
                        or token.startswith('_<') or token.startswith('_>') \
                        or token.startswith('_=') or token.startswith('_equals') \
                        or token.startswith('sum') or token.startswith('count'):
                    meta_relations.add(token[:-1])
                else:
                    relations.add(token[:-1])
    return sorted(list(relations)), sorted(list(meta_relations))


if __name__ == '__main__':
    questions, logical_forms = read_data()
    relations, meta_relations = get_relations(logical_forms)

    # Meta Relations
    print("Binary Relations")
    print("""GRAMMAR_DICTIONARY['meta'] = %s""" % (["(%s)" % r for r in meta_relations]))
    for r in meta_relations:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" predicate ")")']""" % (r, r))
    print("==\n\n")


    # Relations
    print("Relations")
    print("""GRAMMAR_DICTIONARY['relation'] = %s""" % (["(%s)" % r for r in relations]))
    for r in relations:
        print("""GRAMMAR_DICTIONARY['%s'] = ['("%s(" predicate ")")']""" % (r, r))
    print("==\n\n")
