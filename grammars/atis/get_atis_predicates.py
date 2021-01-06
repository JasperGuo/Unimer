# coding=utf8


def read_data():
    questions, logical_forms = list(), list()
    paths = ["../../data/atis/atis_lambda_train.tsv",
             "../../data/atis/atis_lambda_dev.tsv",
             "../../data/atis/atis_lambda_test.tsv"]
    for p in paths:
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                splits = line.split('\t')
                questions.append(splits[0])
                logical_forms.append(splits[1])
    return questions, logical_forms


def tokenize_logical_form(lf):
    return lf.split()


def extract_predicate_and_entity(logical_forms):
    predicates = set()
    entities = set()
    variables = set()
    for lf in logical_forms:
        tokens = tokenize_logical_form(lf)
        for token in tokens:
            if token.startswith("_"):
                predicates.add(token)
            elif ":_" in token:
                entities.add(token)
            elif token.startswith("$"):
                variables.add(token)
    return predicates, entities, variables


if __name__ == '__main__':
    questions, logical_forms = read_data()
    for q, lf in zip(questions, logical_forms):
        print(q)
        print(lf)
        print("==\n\n")

    predicates, entities, variables = extract_predicate_and_entity(logical_forms)
    print("Predicates")
    print(predicates)

    print("Entities: ")
    entity_dict = dict()
    for entity in entities:
        splits = entity.split(":")
        etype = splits[1]
        if etype not in entity_dict:
            entity_dict[etype] = list()
        entity_dict[etype].append(entity)
    for etype, _entities in entity_dict.items():
        print(etype)
        print(['"%s"' % e for e in _entities])
    print("***\n\n")

    print("Variables:")
    _vars = ['"%s"' % v for v in variables]
    print(_vars)
