# coding=utf8
from allennlp.data import Token


def lambda_calculus_entity_extractor(grammar, lc):
    """
    :param grammar: Lambda Calculus Grammar 1
    :param prolog:
    :return:
    """
    applied_production_rules = grammar.parse(lc)
    entities = set()
    for rule in applied_production_rules:
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
            value = rule.rhs.replace('"', "").replace('(', '').replace(')', '').replace("\'", "").replace('[', "").replace("]", "")
            if value == 'hour9':
                entities.add('9')
            elif value == 'days_codesa':
                entities.add('sa')
            else:
                assert value == 'manufacturerboeing'
                entities.add('boeing')
        elif rule.lhs in grammar.copy_terminal_set:
            rhs = rule.rhs.replace('"', "").replace("\'", "").replace('[', "").replace("]", "")
            if rhs == '_':
                continue
            entities.add(rhs)
    return entities


def prolog_entity_extractor(grammar, prolog):
    """
    :param grammar: Prolog grammar 1
    :param funql:
    :return:
    """
    applied_production_rules = grammar.parse(prolog)
    entities = set()
    for rule in applied_production_rules:
        if rule.lhs == 'object' and len(rule.rhs_nonterminal) == 0:
            value = rule.rhs.replace('"', "").replace('(', '').replace(')', '').replace("\'", "").replace('[', "").replace("]", "")
            if value == 'hour9':
                entities.add('9')
            elif value == 'days_codesa':
                entities.add('sa')
            else:
                assert value == 'manufacturerboeing'
                entities.add('boeing')
        elif rule.lhs in grammar.copy_terminal_set:
            rhs = rule.rhs.replace('"', "").replace("\'", "").replace('[', "").replace("]", "")
            if rhs == '_':
                continue
            entities.add(rhs)
    return entities


def replace_lambda_calculus_entity(grammar, lc, lc_tokens, candidates):
    entities = lambda_calculus_entity_extractor(grammar, lc)
    replaced_tokens = list()
    is_valid = True
    for token in lc_tokens:
        text = token.text.replace("'", "")
        if text in entities:
            # entity
            for candidate in candidates:
                if candidate['formatted_value'] == text:
                    replaced_tokens.append(Token('@entity_%d' % candidate['index']))
                    break
            else:
                is_valid = False
                replaced_tokens.append(token)
        else:
            replaced_tokens.append(token)
    return is_valid, replaced_tokens


def replace_funql_entity(grammar, funql, funql_tokens, candidates):
    entities = funql_entity_extractor(grammar, funql)
    replaced_tokens = list()
    is_valid = True
    for token in funql_tokens:
        text = token.text.replace("'", "")
        if text in entities:
            # entity
            for candidate in candidates:
                if candidate['formatted_value'] == text:
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
                if candidate['formatted_value'] == text:
                    replaced_tokens.append(Token('@entity_%d' % candidate['index']))
                    break
            else:
                is_valid = False
                replaced_tokens.append(token)
        else:
            replaced_tokens.append(token)
    return is_valid, replaced_tokens


def test_lambda_calculus_entity_extractor():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('atis', 'lambda')
    grammar = get_grammar('atis', 'lambda')
    lc = preprocessor("( _lambda $v1 e ( _exists $v0 ( _and ( _flight $v0 ) ( _from $v0 washington:_ci ) ( _to $v0 toronto:_ci ) ( _day $v0 saturday:_da ) ( _= ( _fare $v0 ) $v1 ) ) ) )")
    entities = lambda_calculus_entity_extractor(grammar, lc)
    print(entities)


def test_funql_entity_extractor():
    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('atis', 'funql')
    grammar = get_grammar('atis', 'funql')
    lc = preprocessor("answer(intersection(_meal_2(meal_description(snack)),_airline_2(airline_code(ff))))")
    entities = funql_entity_extractor(grammar, lc)
    print(entities)


if __name__ == '__main__':
    test_funql_entity_extractor()
