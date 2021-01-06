# coding=utf8

import copy
from typing import List, Dict, Set
from pprint import pprint
from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar as _Grammar
from grammars.basic import ProductionRule
from grammars.utils import format_grammar_string, initialize_valid_actions, SqlVisitor
from grammars.geo import prolog_grammar, funql_grammar, sql_grammar, \
     lambda_calculus_grammar, typed_funql_grammar, typed_prolog_grammar, \
         sql_grammar_2, sql_grammar_3, lambda_calculus_grammar_2
from grammars.atis import lambda_calculus_grammar as atis_lambda_calculus_grammar
from grammars.atis import lambda_calculus_grammar_2 as atis_lambda_calculus_grammar_2
from grammars.atis import lambda_calculus_grammar_3 as atis_lambda_calculus_grammar_3
from grammars.atis import lambda_calculus_grammar_4 as atis_lambda_calculus_grammar_4
from grammars.atis import sql_grammar as atis_sql_grammar
from grammars.atis import sql_grammar_2 as atis_sql_grammar_2
from grammars.atis import sql_grammar_3 as atis_sql_grammar_3
from grammars.atis import prolog_grammar as atis_prolog_grammar
from grammars.atis import prolog_grammar_2 as atis_prolog_grammar_2
from grammars.atis import funql_grammar as atis_funql_grammar
from grammars.atis import typed_funql_grammar as atis_typed_funql_grammar
from grammars.job import prolog_grammar as job_prolog_grammar
from grammars.job import funql_grammar as job_funql_grammar
from grammars.job import sql_grammar as job_sql_grammar
from grammars.job import lambda_grammar as job_lambda_grammar


class Grammar:

    def __init__(self, grammar_dictionary: Dict, root_rule: str, copy_terminal_set: Set = None):
        self._grammar_dictionary = copy.deepcopy(grammar_dictionary)

        # Non terminals
        self._non_terminals = sorted(list(self._grammar_dictionary.keys()))

        pprint(format_grammar_string(self._grammar_dictionary))

        _grammar = _Grammar(format_grammar_string(self._grammar_dictionary))
        self._grammar = _grammar
        valid_actions = initialize_valid_actions(_grammar)
        all_actions = set()
        for action_list in valid_actions.values():
            all_actions.update(action_list)
        production_rule_strs = sorted(all_actions)

        self._root_rule = root_rule

        self._production_rules = list()
        self._nonterminals_dict = dict()
        self._rule2id = dict()
        self._id2rule = dict()
        rule_id = 1
        for production_rule_str in production_rule_strs:
            print(production_rule_str)
            nonterminal, rhs = production_rule_str.split(' -> ')
            production_rule_str = ' '.join(production_rule_str.split(' '))
            assert nonterminal in self._non_terminals
            rhs_nonterminal = [term for term in rhs.strip(
                '[] ').split(' ') if term in self._non_terminals]
            self._production_rules.append(ProductionRule(
                rule_id, production_rule_str, nonterminal, rhs, rhs_nonterminal))
            self._rule2id[production_rule_str] = rule_id
            self._id2rule[rule_id] = self._production_rules[-1]
            if nonterminal not in self._nonterminals_dict:
                self._nonterminals_dict[nonterminal] = list()
            self._nonterminals_dict[nonterminal].append(
                self._production_rules[-1])
            rule_id += 1
        self._copy_terminal_set = copy_terminal_set

    @property
    def production_rules(self):
        return self._production_rules

    @property
    def copy_terminal_set(self):
        return self._copy_terminal_set

    @property
    def root_rule_id(self):
        return self._rule2id[self._root_rule]

    @property
    def num_rules(self):
        return len(self._rule2id)

    @property
    def num_non_terminals(self):
        return len(self._non_terminals)

    def parse(self, query: str):
        sql_visitor = SqlVisitor(self._grammar)
        q = query.replace("``", "'").replace("''", "'")
        try:
            applied_production_rules = sql_visitor.parse(q) if query else []
        except ParseError as e:
            raise e
            # applied_production_rules = list()
        rules = list()
        for rule in applied_production_rules:
            lhs, rhs = rule.split(' -> ')
            rule_str = rule
            rules.append(copy.deepcopy(self.get_production_rule_by_id(
                self.get_production_rule_id(rule_str))))
        return rules

    def get_production_rule_by_id(self, rule_id) -> ProductionRule:
        if rule_id not in self._id2rule:
            return None
        return self._id2rule[rule_id]

    def get_production_rule_ids_by_nonterminal_id(self, nonterminal_id: int) -> List[int]:
        nonterminal = self._non_terminals[nonterminal_id]
        production_rules = self._nonterminals_dict[nonterminal]
        return [p.rule_id for p in production_rules]

    def get_production_rule_ids_by_nonterminal(self, nonterminal: str) -> List[int]:
        production_rules = self._nonterminals_dict[nonterminal]
        return [p.rule_id for p in production_rules]

    def get_production_rules_by_nonterminal(self, nonterminal: str) -> List[ProductionRule]:
        return self._nonterminals_dict[nonterminal]

    def get_production_rule_id(self, production_rule: str) -> int:
        return self._rule2id[production_rule]

    def get_non_terminal_id(self, nonterminal):
        return self._non_terminals.index(nonterminal)

    def get_non_terminal(self, nonterminal_id):
        if nonterminal_id >= len(self._non_terminals):
            return None
        return self._non_terminals[nonterminal_id]


def get_grammar(dataset, language):
    if dataset == 'geo':
        if language == 'funql':
            copy_terminal_set = funql_grammar.COPY_TERMINAL_SET
            return Grammar(funql_grammar.GRAMMAR_DICTIONARY, funql_grammar.ROOT_RULE, copy_terminal_set)
        if language == 'typed_funql':
            copy_terminal_set = typed_funql_grammar.COPY_TERMINAL_SET
            return Grammar(typed_funql_grammar.GRAMMAR_DICTIONARY, typed_funql_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'prolog':
            copy_terminal_set = prolog_grammar.COPY_TERMINAL_SET
            return Grammar(prolog_grammar.GRAMMAR_DICTIONARY, prolog_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'prolog2':
            copy_terminal_set = typed_prolog_grammar.COPY_TERMINAL_SET
            return Grammar(typed_prolog_grammar.GRAMMAR_DICTIONARY, typed_prolog_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'sql':
            copy_terminal_set = sql_grammar.COPY_TERMINAL_SET
            return Grammar(sql_grammar.GRAMMAR_DICTIONARY, sql_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'sql2':
            copy_terminal_set = sql_grammar_2.COPY_TERMINAL_SET
            return Grammar(sql_grammar_2.GRAMMAR_DICTIONARY, sql_grammar_2.ROOT_RULE, copy_terminal_set)
        elif language == 'sql3':
            return Grammar(sql_grammar_3.GRAMMAR_DICTIONARY, sql_grammar_3.ROOT_RULE)
        elif language == 'lambda':
            copy_terminal_set = lambda_calculus_grammar.COPY_TERMINAL_SET
            return Grammar(lambda_calculus_grammar.GRAMMAR_DICTIONARY, lambda_calculus_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'lambda2':
            copy_terminal_set = lambda_calculus_grammar_2.COPY_TERMINAL_SET
            return Grammar(lambda_calculus_grammar_2.GRAMMAR_DICTIONARY, lambda_calculus_grammar_2.ROOT_RULE, copy_terminal_set)
    elif dataset == 'job':
        if language == 'prolog':
            copy_terminal_set = job_prolog_grammar.COPY_TERMINAL_SET
            return Grammar(job_prolog_grammar.GRAMMAR_DICTIONARY, job_prolog_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'funql':
            copy_terminal_set = job_funql_grammar.COPY_TERMINAL_SET
            return Grammar(job_funql_grammar.GRAMMAR_DICTIONARY, job_funql_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'sql':
            copy_terminal_set = job_sql_grammar.COPY_TERMINAL_SET
            return Grammar(job_sql_grammar.GRAMMAR_DICTIONARY, job_sql_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'lambda':
            copy_terminal_set = job_lambda_grammar.COPY_TERMINAL_SET
            return Grammar(job_lambda_grammar.GRAMMAR_DICTIONARY, job_lambda_grammar.ROOT_RULE, copy_terminal_set)
    elif dataset == 'atis':
        if language == 'lambda':
            copy_terminal_set = atis_lambda_calculus_grammar.COPY_TERMINAL_SET
            return Grammar(atis_lambda_calculus_grammar.GRAMMAR_DICTIONARY, atis_lambda_calculus_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'lambda2':
            copy_terminal_set = atis_lambda_calculus_grammar_2.COPY_TERMINAL_SET
            return Grammar(atis_lambda_calculus_grammar_2.GRAMMAR_DICTIONARY, atis_lambda_calculus_grammar_2.ROOT_RULE, copy_terminal_set)
        elif language == 'lambda3':
            copy_terminal_set = atis_lambda_calculus_grammar_3.COPY_TERMINAL_SET
            return Grammar(atis_lambda_calculus_grammar_3.GRAMMAR_DICTIONARY, atis_lambda_calculus_grammar_3.ROOT_RULE, copy_terminal_set)
        elif language == 'lambda4':
            copy_terminal_set = atis_lambda_calculus_grammar_4.COPY_TERMINAL_SET
            return Grammar(atis_lambda_calculus_grammar_4.GRAMMAR_DICTIONARY, atis_lambda_calculus_grammar_4.ROOT_RULE,
                           copy_terminal_set)
        elif language in 'sql':
            copy_terminal_set = atis_sql_grammar.COPY_TERMINAL_SET
            return Grammar(atis_sql_grammar.GRAMMAR_DICTIONARY, atis_sql_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'sql2':
            copy_terminal_set = atis_sql_grammar_2.COPY_TERMINAL_SET
            return Grammar(atis_sql_grammar_2.GRAMMAR_DICTIONARY, atis_sql_grammar_2.ROOT_RULE, copy_terminal_set)
        elif language == 'sql3':
            copy_terminal_set = atis_sql_grammar_3.COPY_TERMINAL_SET
            return Grammar(atis_sql_grammar_3.GRAMMAR_DICTIONARY, atis_sql_grammar_3.ROOT_RULE, copy_terminal_set)
        elif language == 'prolog':
            copy_terminal_set = atis_prolog_grammar.COPY_TERMINAL_SET
            return Grammar(atis_prolog_grammar.GRAMMAR_DICTIONARY, atis_prolog_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'prolog2':
            copy_terminal_set = atis_prolog_grammar_2.COPY_TERMINAL_SET
            return Grammar(atis_prolog_grammar_2.GRAMMAR_DICTIONARY, atis_prolog_grammar_2.ROOT_RULE, copy_terminal_set)
        elif language == 'funql':
            copy_terminal_set = atis_funql_grammar.COPY_TERMINAL_SET
            return Grammar(atis_funql_grammar.GRAMMAR_DICTIONARY, atis_funql_grammar.ROOT_RULE, copy_terminal_set)
        elif language == 'typed_funql':
            copy_terminal_set = atis_typed_funql_grammar.COPY_TERMINAL_SET
            return Grammar(atis_typed_funql_grammar.GRAMMAR_DICTIONARY, atis_typed_funql_grammar.ROOT_RULE, copy_terminal_set)
    return None
