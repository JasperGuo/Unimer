# coding=utf8

import os
import re
import itertools
import collections
import numpy as np
from typing import List
from allennlp.data.tokenizers import Token


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


class ATISSeq2SeqLambdaCalculusEntityMatcher:
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

    ST_CITIES = [(m, "%s:_ci" % m.replace(" . ", "_")) for m in ('st . louis', 'st . petersburg', 'st . paul')]

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

        self.handle_times()
        self.handle_rc()
        self.handle_stop()
        self.handle_dollars()
        self.handle_flight_numbers()

    def handle_times(self):
        # Mod 12 deals with 12am/12pm special cases...
        self.add_handler('([0-9]{1,2}) am$',
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
                if self.entries[name] != entries:
                    print("Collision detected: %s -> %s, %s" % (name, self.entries[name], entity))
                continue
            self.entries[name] = entity

            # Update self.unique_word_map
            for w in name.split(' '):
                if w in self.seen_words:
                    # This word is not unique!
                    if w in self.unique_word_map:
                        del self.unique_word_map[w]
                else:
                    self.unique_word_map[w] = entity
                    self.seen_words.add(w)

    def add_handler(self, regex, func):
        self.handlers.append((regex, func))

    def _match_candidates(self, tokens: List[Token]) -> List[str]:
        words = [t.text for t in tokens]
        entities = [None for i in range(len(words))]
        ind_pairs = sorted(list(itertools.combinations(range(len(words) + 1), 2)),
                        key=lambda x: x[0] - x[1])
        words = [strip_unk(w) for w in words]  # Strip unk:%06d stuff

        # Entries
        for i, j in ind_pairs:
            if any(x for x in entities[i:j]): continue
            span = ' '.join(words[i:j])
            if span in self.entries:
                entity = self.entries[span]
                for k in range(i, j):
                    entities[k] = entity

        # Handlers
        for i, j in ind_pairs:
            if any(x for x in entities[i:j]): continue
            span = ' '.join(words[i:j])
            for regex, func in self.handlers:
                m = re.match(regex, span)
                if m:
                    entity = func(m)
                    for k in range(i, j):
                        entities[k] = entity

        # Unique words
        for i in range(len(words)):
            if entities[i]: continue
            word = words[i]
            if entities[i]: continue
            if word in self.unique_word_map:
                entity = self.unique_word_map[word]
                entities[i] = entity

        return entities

    def match(self, tokens: List[Token]) -> List[str]:
        entity_candidates = self._match_candidates(tokens)
        return entity_candidates


if __name__ == '__main__':
    matcher = ATISSeq2SeqLambdaCalculusEntityMatcher('../../data/atis/db')
    print(matcher)
