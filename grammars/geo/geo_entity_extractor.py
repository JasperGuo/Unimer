# coding=utf8

import os
from allennlp.data.tokenizers import Token, WordTokenizer
from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter


def funql_entity_extractor(grammar, funql):
    """
    :param grammar: FunQL grammar 1
    :param funql:
    :return:
    """
    applied_production_rules = grammar.parse(funql)
    entities = set()
    for rule in applied_production_rules:
        if rule.lhs == 'object' and len(rule.rhs_nonterminal) == 0:
            # country
            entities.add('usa')
        elif rule.lhs in grammar.copy_terminal_set:
            rhs = rule.rhs.replace('"', "").replace("\'", "").replace('[', "").replace("]", "")
            if rhs == '_':
                continue
            entities.add(rhs)
    return entities


def prolog_entity_extractor(grammar, prolog):
    """
    :param grammar: Prolog Grammar 1
    :param prolog:
    :return:
    """
    applied_production_rules = grammar.parse(prolog)
    entities = set()
    for rule in applied_production_rules:
        if rule.lhs == 'object' and len(rule.rhs_nonterminal) == 0:
            # country
            entities.add('usa')
        elif rule.lhs in grammar.copy_terminal_set:
            rhs = rule.rhs.replace('"', "").replace("\'", "").replace('[', "").replace("]", "")
            if rhs == '_':
                continue
            entities.add(rhs)
    return entities


def lambda_calculus_entity_extractor(grammar, lc):
    """
    :param grammar: Lambda Calculus Grammar 1
    :param prolog:
    :return:
    """
    applied_production_rules = grammar.parse(lc)
    entities = set()
    for rule in applied_production_rules:
        if rule.lhs == 'constant':
            print(len(rule.rhs_nonterminal))
        if rule.lhs == 'constant' and len(rule.rhs_nonterminal) == 0:
            # country
            entities.add(rule.rhs.replace('"', "").replace('(', '').replace(')', '').replace("\'", "").replace('[', "").replace("]", ""))
            print(rule)
        elif rule.lhs in grammar.copy_terminal_set:
            rhs = rule.rhs.replace('"', "").replace("\'", "").replace('[', "").replace("]", "")
            if rhs == '_':
                continue
            entities.add(rhs)
    return entities


def sql_entity_extractor(grammar, lc):
    """
    :param grammar: SQL Grammar 1
    :param prolog:
    :return:
    """
    applied_production_rules = grammar.parse(lc)
    entities = set()
    for rule in applied_production_rules:
        if rule.lhs in grammar.copy_terminal_set:
            rhs = rule.rhs.replace('"', "").replace("\'", "").replace('[', "").replace("]", "")
            entities.add(rhs)
    return entities


def replace_funql_entity(grammar, funql, funql_tokens, candidates):
    entities = funql_entity_extractor(grammar, funql)
    replaced_tokens = list()
    is_valid = True
    for token in funql_tokens:
        text = token.text.replace("'", "")
        if text in entities:
            # entity
            for candidate in candidates:
                if candidate['value'] == text or \
                        ('abbreviation' in candidate and candidate['abbreviation'] == text):
                    replaced_tokens.append(Token('@entity_%d' % candidate['index']))
                    break
            else:
                is_valid = False
                replaced_tokens.append(token)
        else:
            replaced_tokens.append(token)
    return is_valid, replaced_tokens


def replace_prolog_entity(grammar, prolog, prolog_tokens, candidates):
    entities = prolog_entity_extractor(grammar, prolog)
    replaced_tokens = list()
    is_valid = True
    for token in prolog_tokens:
        text = token.text.replace("'", "")
        if text in entities:
            # entity
            for candidate in candidates:
                if candidate['value'] == text or \
                        ('abbreviation' in candidate and candidate['abbreviation'] == text):
                    replaced_tokens.append(Token('@entity_%d' % candidate['index']))
                    break
            else:
                is_valid = False
                replaced_tokens.append(token)
        else:
            replaced_tokens.append(token)
    return is_valid, replaced_tokens


def replace_lambda_calculus_entity(grammar, lc, lc_tokens, candidates):
    entities = lambda_calculus_entity_extractor(grammar, lc)
    replaced_tokens = list()
    is_valid = True
    for token in lc_tokens:
        text = token.text.replace("'", "")
        if text in entities:
            # entity
            for candidate in candidates:
                print(candidate)
                if candidate['formatted_value'] == text:
                    replaced_tokens.append(Token('@entity_%d' % candidate['index']))
                    break
            else:
                is_valid = False
                replaced_tokens.append(token)
        else:
            replaced_tokens.append(token)
    return is_valid, replaced_tokens


def replace_sql_entity(grammar, sql, sql_tokens, candidates):
    entities = sql_entity_extractor(grammar, sql)
    replaced_tokens = list()
    is_valid = True
    for token in sql_tokens:
        text = token.text.replace("'", "").replace('"', "")
        if text in entities:
            # entity
            for candidate in candidates:
                if candidate['value'] == text or \
                        ('abbreviation' in candidate and candidate['abbreviation'] == text):
                    replaced_tokens.append(Token('@entity_%d' % candidate['index']))
                    break
            else:
                is_valid = False
                replaced_tokens.append(token)
        else:
            replaced_tokens.append(token)
    return is_valid, replaced_tokens


def test_funql_entity_extractor():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('geo', 'funql')
    grammar = get_grammar('geo', 'funql')
    funql = preprocessor(
        "answer(count(intersection(state(loc_2(countryid('usa'))), traverse_1(shortest(river(all))))))")
    entities = funql_entity_extractor(grammar, funql)
    print(entities)


def test_funql_entity_replacer():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor, get_logical_form_tokenizer
    preprocessor = get_logical_form_preprocessor('geo', 'funql')
    grammar = get_grammar('geo', 'funql')
    funql = preprocessor(
        "answer(count(intersection(state(loc_2(countryid('usa'))), traverse_1(shortest(river(all))))))")
    # Test Replace
    funql = preprocessor("answer(len(longest(river(loc_2(stateid('california'))))))")
    funql_tokenizer = get_logical_form_tokenizer('geo', 'funql')
    funql_tokens = funql_tokenizer.tokenize(funql)

    question = 'how long is the longest river in california'
    question_tokenizer = WordTokenizer(SpacyWordSplitter())
    question_tokens = question_tokenizer.tokenize(question)

    from geo_gnn_entity_matcher import GeoGNNEntityMatcher
    base_path = os.path.join('../../', 'data', 'geo')
    entity_path = os.path.join(base_path, 'geo_entities.json')
    matcher = GeoGNNEntityMatcher(entity_path, max_ngram=6)
    candidates = matcher.match(question_tokens)
    for can_idx, can in enumerate(candidates):
        can['index'] = can_idx

    is_valid, replaced_tokens = replace_funql_entity(grammar, funql, funql_tokens, candidates)
    print(funql_tokens)
    print(is_valid)
    print(replaced_tokens)


def test_prolog_entity_extractor():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('geo', 'prolog')
    grammar = get_grammar('geo', 'prolog')
    prolog = preprocessor("answer(A,(capital(A),loc(A,B),state(B),loc(C,B),city(C),const(C,cityid(durham,_))))")
    entities = funql_entity_extractor(grammar, prolog)
    print(entities)


def test_prolog_entity_replacer():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor, get_logical_form_tokenizer
    preprocessor = get_logical_form_preprocessor('geo', 'prolog', normalize_var_with_de_brujin_index=True)
    grammar = get_grammar('geo', 'prolog')
    prolog = preprocessor(
        "answer(A,(capital(A),loc(A,B),state(B),loc(C,B),city(C),const(C,cityid(durham,_))))",
    ).lower()

    # Test Replace
    prolog_tokenizer = get_logical_form_tokenizer('geo', 'prolog')
    prolog_tokens = prolog_tokenizer.tokenize(prolog)

    question = 'what is the capital of states that have cities named durham ?'
    question_tokenizer = WordTokenizer(SpacyWordSplitter())
    question_tokens = question_tokenizer.tokenize(question)

    from geo_gnn_entity_matcher import GeoGNNEntityMatcher
    base_path = os.path.join('../../', 'data', 'geo')
    entity_path = os.path.join(base_path, 'geo_entities.json')
    matcher = GeoGNNEntityMatcher(entity_path, max_ngram=6)
    candidates = matcher.match(question_tokens)
    for can_idx, can in enumerate(candidates):
        can['index'] = can_idx

    is_valid, replaced_tokens = replace_funql_entity(grammar, prolog, prolog_tokens, candidates)
    print(prolog_tokens)
    print(is_valid)
    print(replaced_tokens)


def test_lambda_calculus_entity_replacer():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor, get_logical_form_tokenizer
    preprocessor = get_logical_form_preprocessor('geo', 'lambda')
    grammar = get_grammar('geo', 'lambda')
    lc = preprocessor(
        "(lambda $0:e (and:<t*,t> (major:<lo,t> $0) (city:<c,t> $0) (loc:<lo,<lo,t>> $0 alaska:s)))",
    )

    # Test Replace
    lc_tokenizer = get_logical_form_tokenizer('geo', 'lambda')
    lc_tokens = lc_tokenizer.tokenize(lc)

    question = 'what are the major cities in alaska'
    question_tokenizer = WordTokenizer(SpacyWordSplitter())
    question_tokens = question_tokenizer.tokenize(question)

    from geo_gnn_entity_matcher import GeoLambdaCalculusGNNEntityMatcher
    base_path = os.path.join('../../', 'data', 'geo')
    entity_path = os.path.join(base_path, 'geo_entities.json')
    matcher = GeoLambdaCalculusGNNEntityMatcher(entity_path, max_ngram=6)
    candidates = matcher.match(question_tokens)
    for can_idx, can in enumerate(candidates):
        can['index'] = can_idx

    is_valid, replaced_tokens = replace_lambda_calculus_entity(grammar, lc, lc_tokens, candidates)
    print(lc_tokens)
    print(is_valid)
    print(replaced_tokens)


def test_sql_entity_replacer():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor, get_logical_form_tokenizer
    preprocessor = get_logical_form_preprocessor('geo', 'sql')
    grammar = get_grammar('geo', 'sql')
    sql = preprocessor(
        'SELECT CITYalias0.POPULATION FROM CITY AS CITYalias0 WHERE CITYalias0.CITY_NAME = "erie" AND CITYalias0.STATE_NAME = "pennsylvania" ;')

    # Test Replace
    sql_tokenizer = get_logical_form_tokenizer('geo', 'sql')
    sql_tokens = sql_tokenizer.tokenize(sql)

    question = 'what is the population of erie pennsylvania'
    question_tokenizer = WordTokenizer(SpacyWordSplitter())
    question_tokens = question_tokenizer.tokenize(question)

    from geo_gnn_entity_matcher import GeoGNNEntityMatcher
    base_path = os.path.join('../../', 'data', 'geo')
    entity_path = os.path.join(base_path, 'geo_entities.json')
    matcher = GeoGNNEntityMatcher(entity_path, max_ngram=6)
    candidates = matcher.match(question_tokens)
    for can_idx, can in enumerate(candidates):
        can['index'] = can_idx

    is_valid, replaced_tokens = replace_sql_entity(grammar, sql, sql_tokens, candidates)
    print(sql_tokens)
    print("Is Valid: ", is_valid)
    print(replaced_tokens)


def test_sql_entity_extractor():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('geo', 'sql')
    grammar = get_grammar('geo', 'sql')
    print(grammar.copy_terminal_set)
    sql = preprocessor('SELECT CITYalias0.POPULATION FROM CITY AS CITYalias0 WHERE CITYalias0.CITY_NAME = "erie" AND CITYalias0.STATE_NAME = "pennsylvania" ;')
    entities = sql_entity_extractor(grammar, sql)
    print(entities)


if __name__ == '__main__':
    test_sql_entity_replacer()
