# coding=utf8

import os
import re
import copy
import itertools
import collections
import numpy as np
from overrides import overrides
from typing import List, Dict
from allennlp.data.tokenizers import Token, WordTokenizer
from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter
from .atis_entity_extractor import lambda_calculus_entity_extractor, funql_entity_extractor, prolog_entity_extractor


def clean_id(s, id_suffix, strip=None):
    true_id = s.replace(' ', '_')
    if strip:
        for v in strip:
            true_id = true_id.replace(v, '').strip()
    return '%s:%s' % (true_id, id_suffix)


def clean_name(s, strip=None, split=None, prefix=None):
    if split:
        for v in split:
            s = s.replace(v, ' ')
    if strip:
        for v in strip:
            s = s.replace(v, '')
    if prefix:
        s = prefix + s
    return s


def read_db(db_path, basename, id_col, name_col, id_suffix,
            strip_id=None, strip_name=None, split_name=None, prefix_name=None):
    filename = os.path.join(db_path, basename)
    data = []  # Pairs of (name, id)
    with open(filename) as f:
        for line in f:
            row = [s[1:-1] for s in re.findall('"[^"]*"|[0-9]+', line.strip())]
            cur_name = clean_name(row[name_col].lower(), strip=strip_name,
                                  split=split_name, prefix=prefix_name)
            cur_id = clean_id(row[id_col].lower(), id_suffix, strip=strip_id)
            data.append((cur_name, cur_id))
    return data


def print_aligned(a, b, indent=0):
    a_toks = []
    b_toks = []
    for x, y in zip(a, b):
        cur_len = max(len(x), len(y))
        a_toks.append(x.ljust(cur_len))
        b_toks.append(y.ljust(cur_len))

    prefix = ' ' * indent
    print('%s%s' % (prefix, ' '.join(a_toks)))
    print('%s%s' % (prefix, ' '.join(b_toks)))


def parse_entry(line):
    """Parse an entry from the CCG lexicon."""
    return tuple(line.strip().split(' :- NP : '))


def strip_unk(w):
    # Strip unk:%06d identifiers
    m = re.match('^unk:[0-9]{6,}:(.*)$', w)
    if m:
        return m.group(1)
    else:
        return w


class ATISGNNLambdaCalculusEntityMatcher:
    TYPE_DICT = {
        'ci': 'city',
        'da': 'day',
        'al': 'airline',
        'ti': 'time',
        'pd': 'time of day',
        'dn': 'date number',
        'mn': 'month',
        'ap': 'airport',
        'cl': 'class',
        'fb': 'fare code',
        'fn': 'flight number',
        'me': 'meal',
        'do': 'dollars',
        'rc': 'restrictions',
        'ac': 'aircraft',
        'yr': 'year',
        'mf': 'manufacturer',
        'dc': 'dc',
        'st': 'state',
        'hr': 'hour',
        'i': 'stop'
    }

    DAYS_OF_WEEK = [
        (s, '%s:_da' % s)
        for s in ('monday', 'tuesday', 'wednesday', 'thursday',
                  'friday', 'saturday', 'sunday')
    ]

    NEXT_DAYS_OF_WEEK = [('day following next wednesday', 'thursday:_da')]

    # For dates
    WORD_NUMBERS = [('one', '1:_dn'), ('two', '2:_dn'), ('three', '3:_dn'), ('four', '4:_dn'), ('five', '5:_dn'),
                    ('six', '6:_dn'), ('seven', '7:_dn'), ('eight', '8:_dn'), ('nine', '9:_dn'), ('ten', '10:_dn'),
                    ('eleven', '11:_dn'), ('twelve', '12:_dn'), ('thirteen', '13:_dn'), ('fourteen', '14:_dn'),
                    ('fifteen', '15:_dn'), ('sixteen', '16:_dn'), ('seventeen', '17:_dn'), ('eighteen', '18:_dn'),
                    ('nineteen', '19:_dn'), ('twenty', '20:_dn'), ('twenty one', '21:_dn'),
                    ('twenty two', '22:_dn'),
                    ('twenty three', '23:_dn'), ('twenty four', '24:_dn'), ('twenty five', '25:_dn'),
                    ('twenty six', '26:_dn'), ('twenty seven', '27:_dn'), ('twenty eight', '28:_dn'),
                    ('twenty nine', '29:_dn'), ('thirty', '30:_dn'), ('thirty one', '31:_dn')]

    ORDINAL_NUMBERS = [('second', '2:_dn'), ('third', '3:_dn'), ('fourth', '4:_dn'), ('fifth', '5:_dn'),
                       ('sixth', '6:_dn'), ('seventh', '7:_dn'), ('eighth', '8:_dn'), ('ninth', '9:_dn'),
                       ('tenth', '10:_dn'), ('eleventh', '11:_dn'), ('twelfth', '12:_dn'), ('thirteenth', '13:_dn'),
                       ('fourteenth', '14:_dn'), ('fifteenth', '15:_dn'), ('sixteenth', '16:_dn'),
                       ('seventeenth', '17:_dn'), ('eighteenth', '18:_dn'), ('nineteenth', '19:_dn'),
                       ('twentieth', '20:_dn'), ('twenty first', '21:_dn'), ('twenty second', '22:_dn'),
                       ('twenty third', '23:_dn'), ('twenty fourth', '24:_dn'), ('twenty fifth', '25:_dn'),
                       ('twenty sixth', '26:_dn'), ('twenty seventh', '27:_dn'), ('twenty eighth', '28:_dn'),
                       ('twenty ninth', '29:_dn'), ('thirtieth', '30:_dn'),
                       ('thirty first', '31:_dn')]

    MEALS = [(m, '%s:_me' % m) for m in ('breakfast', 'lunch', 'dinner', 'snack')]

    MEAL_CODES = [('s/', 's_:_rc'), ('sd / d', 'sd_d:_rc'), ('d / s', 'd_s:_rc')]

    ST_CITIES = [(m, "%s:_ci" % m.replace(" . ", "_")) for m in ('st . louis', 'st . petersburg', 'st . paul')]

    BAT_CODES = [('737', '737:_bat'), ('767', '767:_bat')]

    AP_CODES = [('mco', 'mco:_ap'), ('ord', 'ord:_ap')]

    AL_CODES = [('us air', 'usair:_al'), ('delta', 'delta:_al'), ('ff', 'ff:_al'),
                ('canadian airlines international', 'canadian_airlines_international:_al')]

    def __init__(self, db_path):
        self.entries = collections.OrderedDict()
        self.handlers = []
        self.unique_word_map = collections.OrderedDict()
        self.seen_words = set()

        # CCG Lexicon
        filename = os.path.join(db_path, 'lexicon.txt')
        entries = []
        with open(filename) as f:
            for line in f:
                x, y = line.strip().split(' :- NP : ')
                y = y.replace(':', ':_').strip()
                entries.append((x, y))
        self.add_entries(entries)

        # Read DB
        self.add_entries(read_db(db_path, 'CITY.TAB', 1, 1, '_ci', strip_id=['.']))
        self.add_entries(self.DAYS_OF_WEEK)
        self.add_entries([(x + 's', y) for x, y in self.DAYS_OF_WEEK])  # Handle "on tuesdays"
        self.add_entries(read_db(db_path, 'AIRLINE.TAB', 0, 1, '_al',
                                 strip_name=[', inc.', ', ltd.']))
        self.add_entries(read_db(db_path, 'INTERVAL.TAB', 0, 0, '_pd'))
        self.add_entries(read_db(db_path, 'MONTH.TAB', 1, 1, '_mn'))
        self.add_entries(read_db(db_path, 'AIRPORT.TAB', 0, 1, '_ap',
                                 strip_name=[], split_name=['/']))
        self.add_entries(read_db(db_path, 'COMP_CLS.TAB', 1, 1, '_cl'))
        self.add_entries(read_db(db_path, 'CLS_SVC.TAB', 0, 0, '_fb', prefix_name='code '))
        self.add_entries(self.MEALS)
        self.add_entries(self.WORD_NUMBERS)
        self.add_entries(self.ORDINAL_NUMBERS)
        self.add_entries(self.ST_CITIES)
        self.add_entries(self.MEAL_CODES)
        self.add_entries(self.BAT_CODES)
        self.add_entries(self.AP_CODES)
        self.add_entries(self.AL_CODES)
        self.add_entries(self.NEXT_DAYS_OF_WEEK)

        self.handle_times()
        self.handle_rc()
        self.handle_stop()
        self.handle_dollars()
        self.handle_flight_numbers()

    def handle_times(self):
        # Mod 12 deals with 12am/12pm special cases...
        self.add_handler('([0-9]{1,2})\s*am$',
                         lambda m: '%d00:_ti' % (int(m.group(1)) % 12))
        self.add_handler('([0-9]{1,2}) pm$',
                         lambda m: '%d00:_ti' % (int(m.group(1)) % 12 + 12))
        self.add_handler('([0-9]{1,2})([0-9]{2}) am$',
                         lambda m: '%d%02d:_ti' % (int(m.group(1)) % 12, int(m.group(2))))
        self.add_handler('([0-9]{1,2})([0-9]{2}) pm$',
                         lambda m: '%d%02d:_ti' % (int(m.group(1)) % 12 + 12, int(m.group(2))))
        self.add_handler("([0-9]{1,2}) o'clock$",
                         lambda m: '%d00:_ti' % (int(m.group(1)) % 12))
        self.add_handler("([0-9]{1,2}) o'clock am$",
                         lambda m: '%d00:_ti' % (int(m.group(1)) % 12))
        self.add_handler("([0-9]{1,2}) o'clock pm$",
                         lambda m: '%d00:_ti' % (int(m.group(1)) % 12 + 12))
        self.add_handler("([0-9]+) hours$",
                         lambda m: '%d:_hr' % (int(m.group(1))))

    def handle_flight_numbers(self):
        self.add_handler('[0-9]{2,}$', lambda m: '%d:_fn' % int(m.group(0)))

    def handle_dollars(self):
        self.add_handler('([0-9]+)$', lambda m: '%d:_do' % int(m.group(1)))
        self.add_handler('([0-9]+) dollars$', lambda m: '%d:_do' % int(m.group(1)))

    def handle_rc(self):
        self.add_handler(re.compile(r'ap/(\d+)$'), lambda m: 'ap_%d:_rc' % int(m.group(1)))
        self.add_handler(re.compile(r'ap(\d+)$'), lambda m: 'ap_%d:_rc' % int(m.group(1)))

    def handle_stop(self):
        self.add_handler('([0-9]+) stop$', lambda m: '%d:_i' % int(m.group(1)))
        self.add_handler('([0-9]+) stops$', lambda m: '%d:_i' % int(m.group(1)))

    def add_entries(self, entries):
        for name, entity in entries:
            # Update self.entries
            if name in self.entries:
                if entity not in self.entries[name]:
                    self.entries[name].append(entity)
            else:
                self.entries[name] = [entity]

            # Update self.unique_word_map
            # for w in name.split(' '):
            #     if w in self.seen_words:
            #         # This word is not unique!
            #         if w in self.unique_word_map:
            #             del self.unique_word_map[w]
            #     else:
            #         self.unique_word_map[w] = entity
            #         self.seen_words.add(w)

    def add_handler(self, regex, func):
        self.handlers.append((regex, func))

    def _match_candidates(self, tokens: List[Token]) -> List:
        words = [t.text for t in tokens]
        entities = [[] for i in range(len(words))]
        ind_pairs = sorted(list(itertools.combinations(range(len(words) + 1), 2)),
                        key=lambda x: x[0] - x[1])
        ret_entries = []
        words = [strip_unk(w) for w in words]  # Strip unk:%06d stuff

        # Handlers
        for i, j in ind_pairs:
            if any(x for x in entities[i:j]): continue
            span = ' '.join(words[i:j])
            for regex, func in self.handlers:
                m = re.match(regex, span)
                if m:
                    entity = func(m)
                    assert isinstance(entity, str)
                    for k in range(i, j):
                        entities[k] += [entity]
                    ret_entries.append(((i, j), [entity]))

        # Entries
        for i, j in ind_pairs:
            # if any(x for x in entities[i:j]): continue
            span = ' '.join(words[i:j])
            if span in self.entries:
                entity = self.entries[span]
                assert isinstance(entity, list)
                for k in range(i, j):
                    entities[k] += entity
                ret_entries.append(((i, j), entity))

        # Unique words
        for i in range(len(words)):
            if any(x for x in entities[i:i+1]): continue
            word = words[i]
            if entities[i]: continue
            if word in self.unique_word_map:
                entity = self.unique_word_map[word]
                entities[i] = [entity]
                ret_entries.append(((i, i+1), [entity]))

        return ret_entries

    def match(self, tokens: List[Token]) -> List[Dict]:
        entity_candidates = self._match_candidates(tokens)
        formatted_entity_candidates = list()
        for ((beg_idx, end_idx), entities) in entity_candidates:
            fes = list()
            for e in entities:
                match = re.match("^(.*):_(.*)$", e)
                if match is None:
                    assert re.match('^\d+$', e)
                    ev = e
                    et = 'i'
                else:
                    ev = match.group(1)
                    et = match.group(2)
                fes.append({
                    "value": ev.replace('_', " "),
                    "beg_idx": beg_idx,
                    "end_idx": end_idx,
                    "type": et,
                    "formatted_value": e
                })
            formatted_entity_candidates += fes

        # Remove Duplicate entities
        entity_dict = dict()
        for entity in formatted_entity_candidates:
            if entity['formatted_value'] not in entity_dict:
                entity_dict[entity['formatted_value']] = list()
            entity_dict[entity['formatted_value']].append(entity)

        results = list()
        for _, entities in entity_dict.items():
            indices = list()
            for e in entities:
                beg_idx, end_idx = e['beg_idx'], e['end_idx']
                indices += list(range(beg_idx, end_idx))
            ne = copy.deepcopy(entities[0])
            del ne['beg_idx']
            del ne['end_idx']
            ne['indices'] = list(set(indices))
            results.append(ne)

        return results


class ATISGNNEntityMatcher(ATISGNNLambdaCalculusEntityMatcher):

    def __init__(self, db_path):
        super().__init__(db_path)
        self.add_entries([('new york', 'lga:_ap'), ('the airport in dallas', 'dfw:_ap')])

    @overrides
    def match(self, tokens: List[Token]) -> List[Dict]:
        entity_candidates = super().match(tokens)
        for entity in entity_candidates:
            formatted_value = entity['formatted_value']
            match = re.match("^(.*):_(.*)$", formatted_value)
            if match is None:
                assert re.match('^\d+$', e)
                ev = formatted_value
                et = 'i'
            else:
                ev = match.group(1)
                et = match.group(2)
            entity['formatted_value'] = ev

        # Remove Duplicate entities
        entity_dict = dict()
        for entity in entity_candidates:
            if entity['formatted_value'] not in entity_dict:
                entity_dict[entity['formatted_value']] = list()
            entity_dict[entity['formatted_value']].append(entity)

        results = list()
        for _, entities in entity_dict.items():
            types = list()
            for e in entities:
                types.append(e['type'])
            ne = copy.deepcopy(entities[0])
            ne['type'] = ';'.join(types)
            results.append(ne)

        return results


def test_entity_linking():
    base_path = os.path.join('../../', 'data', 'atis')
    entity_path = os.path.join(base_path, 'db')

    matcher = ATISGNNEntityMatcher(entity_path)
    toknerizer = WordTokenizer(SpacyWordSplitter())

    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('atis', 'prolog')
    grammar = get_grammar('atis', 'prolog')

    train_data = os.path.join(base_path, 'atis_prolog_test.tsv')
    empty_count = 0
    max_number_of_candidates = 0
    numbers = list()
    invalid_count = 0
    inst_count = 0
    with open(train_data, 'r') as f:
        for lidx, line in enumerate(f):
            line = line.strip()
            sentence, funql = line.split('\t')
            tokens = toknerizer.tokenize(sentence)
            candidates = matcher.match(tokens)
            inst_count += 1

            if len(candidates) > max_number_of_candidates:
                max_number_of_candidates = len(candidates)

            has_duplicate_entity = False
            for cidx1, can1 in enumerate(candidates):
                for cidx2, can2 in enumerate(candidates):
                    if cidx1 == cidx2:
                        continue
                    if can1['value'] == can2['value'] and can1['type'] == can2['type']:
                        has_duplicate_entity = True
                        break
                if has_duplicate_entity:
                    break

            if len(candidates) == 0:
                empty_count += 1
            numbers.append(len(candidates))

            # Validate
            processed_funql = preprocessor(funql).lower()
            golden_entities = prolog_entity_extractor(grammar, processed_funql)

            valid = True
            for ge in golden_entities:
                for candidate in candidates:
                    compare_value = candidate['value'] if 'formatted_value' not in candidate \
                        else candidate['formatted_value']
                    if compare_value == ge or candidate.get('abbreviation', "") == ge:
                        break
                else:
                    valid = False
            if not valid:
                invalid_count += 1

            print(lidx)
            print(sentence)
            print(tokens)
            print(funql)
            print("Number of Candidates: ", len(candidates))
            print("Has Duplicate Candidates: ", has_duplicate_entity)
            print(candidates)
            print(golden_entities)
            print("Is Valid: ", valid)
            print('===\n\n')

    print("Largest number of candidates: ", max_number_of_candidates)
    print("Number of empty candidates: ", empty_count)
    print("Averaged candidates: ", np.mean(numbers))
    print("Invalid Count: ", invalid_count)
    print("Overall Recall: ", (inst_count - invalid_count) / inst_count)



if __name__ == '__main__':
    # matcher = ATISGNNLambdaCalculusEntityMatcher('../../data/atis/db')
    # from allennlp.data.tokenizers import Token, WordTokenizer
    # from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter
    # toknerizer = WordTokenizer(SpacyWordSplitter())
    #
    # question = "i'm looking for flights from pittsburgh to philadelphia leaving before 9am"
    # tokens = toknerizer.tokenize(question)
    #
    # matched_entities = matcher.match(tokens)
    # for entity in matched_entities:
    #     string = " ".join([tokens[idx].text for idx in entity['indices']])
    #     print(string, entity['value'], entity['type'])

    test_entity_linking()