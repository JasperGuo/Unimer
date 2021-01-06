# coding=utf8

import os
import re
import numpy as np
from typing import List
from overrides import overrides
from nltk.corpus import stopwords
from allennlp.data.tokenizers import Token
from .atis.atis_entity_matcher import ATISEntityMatcher
from .atis.atis_sql_entity_matcher import ATISSQLEntityMatcher
from .atis.atis_lambda_calculus_entity_matcher import ATISLambdaCalculusEntityMatcher
from .atis.atis_seq2seq_entity_matcher import ATISSeq2SeqEntityMatcher
from .atis.atis_seq2seq_sql_entity_matcher import ATISSeq2SeqSQLEntityMatcher
from .atis.atis_seq2seq_lambda_calculus_entity_matcher import ATISSeq2SeqLambdaCalculusEntityMatcher


class BasicEntityMatcher():

    def process_terminal_rule(self, rule):
        # Process terminal
        terminal = rule.rhs.strip('[] ')
        terminal = terminal.replace("'", "").replace('"', "").replace("_", " ").replace("%", "").replace(":", " : ")
        terminal = re.sub(' +', ' ', terminal)
        terminal_tokens = terminal.lower().split(" ")
        try:
            index = terminal_tokens.index(":")
        except ValueError:
            pass
        else:
            terminal_tokens = terminal_tokens[:index]
        return terminal_tokens

    def match(self, question_tokens: List[Token], rules: List,
              copy_terminal_set: List, pad_index: int, max_ngram=6):
        token_rule_map = list()
        stop_words = set(stopwords.words('english'))
        for token in question_tokens:
            matches = list()
            if token.text in stop_words:
                matches = [pad_index]
            else:
                for rule in rules:  # Instance of Production Rule
                    if rule.lhs in copy_terminal_set:
                        # Process terminal
                        terminal = rule.rhs.strip('[] ')
                        terminal = terminal.replace("'", "").replace('"', "").replace("_", " ").replace("%",
                                                                                                        "").replace(
                            ":", " ")
                        terminal = re.sub(' +', ' ', terminal)
                        terminal_tokens = terminal.lower().split(" ")
                        if token.text in terminal_tokens:
                            matches.append(rule.rule_id)
                if len(matches) == 0:
                    matches = [pad_index]
            token_rule_map.append(np.array(matches, dtype=np.int))
        return token_rule_map


class EntityMatcher(BasicEntityMatcher):

    @overrides
    def match(self, question_tokens: List[Token], rules: List,
              copy_terminal_set: List, pad_index: int, max_ngram=6):
        length = len(question_tokens)
        token_rule_map = [list() for i in range(length)]
        stop_words = set(stopwords.words('english'))
        tidx = 0
        while tidx < length:
            token = question_tokens[tidx]
            if token.text in stop_words:
                tidx += 1
                continue
            for i in range(min(max_ngram, length - tidx)):
                string = ' '.join([t.text for t in question_tokens[tidx:tidx + 1 + i]]).strip().lower()
                for rule in rules:
                    if rule.lhs in copy_terminal_set:
                        terminal_tokens = self.process_terminal_rule(rule)
                        terminal_string = ' '.join(terminal_tokens)
                        if string == terminal_string:
                            # Add rule
                            for index in range(tidx, tidx + 1 + i):
                                token_rule_map[index].append(rule.rule_id)
            tidx += 1
        for midx, m in enumerate(token_rule_map):
            if len(m) == 0:
                m.append(pad_index)
            token_rule_map[midx] = np.array(m, dtype=np.int)
        return token_rule_map


class GEOLambdaCalculusEntityMatcher(EntityMatcher):

    @overrides
    def process_terminal_rule(self, rule):
        # Process terminal
        terminal = rule.rhs.strip('[] ')
        terminal = terminal.replace("'", "").replace('"', "").lower().strip()
        terminal = re.sub(' +', ' ', terminal)
        terminal_tokens = terminal.split(':')
        assert len(terminal_tokens) == 2
        terminal_type = terminal_tokens[1]
        terminal_tokens = terminal_tokens[0].split("_")
        if terminal_type == 'r':
            # River
            terminal_tokens.remove("river")
        elif terminal_type == 'c':
            terminal_tokens = terminal_tokens[:-1]
        return terminal_tokens


def get_entity_matcher(task, language):
    matcher = None
    if task == 'atis':
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'atis', 'db')
        if language in ['lambda', 'lambda2', 'lambda3', 'lambda4',]:
            matcher = ATISLambdaCalculusEntityMatcher(db_path)
        elif language in ['prolog', 'funql', 'typed_funql', 'prolog2']:
            matcher = ATISEntityMatcher(db_path)
        else:
            matcher = ATISSQLEntityMatcher(db_path)
    elif task == 'geo':
        if language in ['lambda', 'lambda2']:
            matcher = GEOLambdaCalculusEntityMatcher()
        else:
            matcher = EntityMatcher()
    elif task == 'job':
        matcher = EntityMatcher()
    return matcher


def get_seq2seq_entity_matcher(task, language):
    matcher = None
    if task == 'atis':
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'atis', 'db')
        if language in ['lambda', 'lambda2', 'lambda3', 'lambda4',]:
            matcher = ATISSeq2SeqLambdaCalculusEntityMatcher(db_path)
        elif language in ['prolog', 'funql', 'typed_funql', 'prolog2']:
            matcher = ATISSeq2SeqEntityMatcher(db_path)
        else:
            matcher = ATISSeq2SeqSQLEntityMatcher(db_path)
    return matcher
