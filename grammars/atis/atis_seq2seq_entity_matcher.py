# coding=utf8

import os
import re
import itertools
import collections
from typing import List
from allennlp.data.tokenizers import Token


def clean_id(s, id_suffix, strip=None):
    true_id = s.replace(' ', '_')
    if strip:
        for v in strip:
            true_id = true_id.replace(v, '').strip()
    return '%s' % true_id


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


def strip_unk(w):
    # Strip unk:%06d identifiers
    m = re.match('^unk:[0-9]{6,}:(.*)$', w)
    if m:
        return m.group(1)
    else:
        return w


class ATISSeq2SeqEntityMatcher:

    DAYS_OF_WEEK = [
        (s, '%s' % s)
        for s in ('monday', 'tuesday', 'wednesday', 'thursday',
                  'friday', 'saturday', 'sunday')
    ]

    # For dates
    WORD_NUMBERS = [('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'), ('five', '5'),
                    ('six', '6'), ('seven', '7'), ('eight', '8'), ('nine', '9'), ('ten', '10'),
                    ('eleven', '11'), ('twelve', '12'), ('thirteen', '13'), ('fourteen', '14'),
                    ('fifteen', '15'), ('sixteen', '16'), ('seventeen', '17'), ('eighteen', '18'),
                    ('nineteen', '19'), ('twenty', '20'), ('twenty one', '21'),
                    ('twenty two', '22'),
                    ('twenty three', '23'), ('twenty four', '24'), ('twenty five', '25'),
                    ('twenty six', '26'), ('twenty seven', '27'), ('twenty eight', '28'),
                    ('twenty nine', '29'), ('thirty', '30'), ('thirty one', '31')]

    ORDINAL_NUMBERS = [('second', '2'), ('third', '3'), ('fourth', '4'), ('fifth', '5'),
                       ('sixth', '6'), ('seventh', '7'), ('eighth', '8'), ('ninth', '9'),
                       ('tenth', '10'), ('eleventh', '11'), ('twelfth', '12'), ('thirteenth', '13'),
                       ('fourteenth', '14'), ('fifteenth', '15'), ('sixteenth', '16'),
                       ('seventeenth', '17'), ('eighteenth', '18'), ('nineteenth', '19'),
                       ('twentieth', '20'), ('twenty first', '21'), ('twenty second', '22'),
                       ('twenty third', '23'), ('twenty fourth', '24'), ('twenty fifth', '25'),
                       ('twenty sixth', '26'), ('twenty seventh', '27'), ('twenty eighth', '28'),
                       ('twenty ninth', '29'), ('thirtieth', '30'),
                       ('thirty first', '31')]

    MEALS = [(m, '%s' % m) for m in ('breakfast', 'lunch', 'dinner', 'snack')]

    ST_CITIES = [(m, "%s" % m.replace(" . ", "_")) for m in ('st . louis', 'st . petersburg', 'st . paul')]

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
                y = y[:y.index(":")]
                entries.append((x, y))
        self.add_entries(entries)

        # Read DB
        city_entries = read_db(db_path, 'CITY.TAB', 1, 1, '', strip_id=['.'])
        self.add_entries(city_entries)
        self.add_entries(self.DAYS_OF_WEEK)
        self.add_entries([(x + 's', y) for x, y in self.DAYS_OF_WEEK])  # Handle "on tuesdays"
        self.add_entries(read_db(db_path, 'AIRLINE.TAB', 0, 1, '',
                                 strip_name=[', inc.', ', ltd.']))
        self.add_entries(read_db(db_path, 'INTERVAL.TAB', 0, 0, ''))
        self.add_entries(read_db(db_path, 'MONTH.TAB', 1, 1, ''))
        self.add_entries(read_db(db_path, 'AIRPORT.TAB', 0, 1, '',
                                 strip_name=[], split_name=['/']))
        self.add_entries(read_db(db_path, 'COMP_CLS.TAB', 1, 1, ''))
        self.add_entries(read_db(db_path, 'CLS_SVC.TAB', 0, 0, '', prefix_name='code '))
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
                         lambda m: '%d00' % (int(m.group(1)) % 12))
        self.add_handler('([0-9]{1,2}) pm$',
                         lambda m: '%d00' % (int(m.group(1)) % 12 + 12))
        self.add_handler('([0-9]{1,2})([0-9]{2}) am$',
                         lambda m: '%d%02d' % (int(m.group(1)) % 12, int(m.group(2))))
        self.add_handler('([0-9]{1,2})([0-9]{2}) pm$',
                         lambda m: '%d%02d' % (int(m.group(1)) % 12 + 12, int(m.group(2))))
        self.add_handler("([0-9]{1,2}) o'clock$",
                         lambda m: '%d00' % (int(m.group(1)) % 12))
        self.add_handler("([0-9]{1,2}) o'clock am$",
                         lambda m: '%d00' % (int(m.group(1)) % 12))
        self.add_handler("([0-9]{1,2}) o'clock pm$",
                         lambda m: '%d00' % (int(m.group(1)) % 12 + 12))
        self.add_handler("([0-9]+) hours$",
                         lambda m: '%d' % (int(m.group(1))))

    def handle_flight_numbers(self):
        self.add_handler('[0-9]{2,}$', lambda m: '%d' % int(m.group(0)))

    def handle_dollars(self):
        self.add_handler('([0-9]+)$', lambda m: '%d' % int(m.group(1)))
        self.add_handler('([0-9]+) dollars$', lambda m: '%d' % int(m.group(1)))

    def handle_rc(self):
        self.add_handler(re.compile(r'ap/(\d+)$'), lambda m: 'ap_%d' % int(m.group(1)))
        self.add_handler(re.compile(r'ap(\d+)$'), lambda m: 'ap_%d' % int(m.group(1)))

    def handle_stop(self):
        self.add_handler('([0-9]+) stop$', lambda m: '%d' % int(m.group(1)))
        self.add_handler('([0-9]+) stops$', lambda m: '%d' % int(m.group(1)))

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

    def get_rule_ids(self, entities, rules: List, copy_terminal_set: List) -> List:
        rule_ids = list()
        if isinstance(entities, str):
            entities = [entities]
        for entity in entities:
            for rule in rules:
                if rule.lhs not in copy_terminal_set:
                    continue
                terminal = rule.rhs.strip('[] ').replace("'", "").replace('"', '')
                if terminal == entity:
                    rule_ids.append(rule.rule_id)
                    break
            else:
                print("Cannot find a corresponding rule for terminal %s" % entity)
        return rule_ids

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
    matcher = ATISSeq2SeqEntityMatcher('../../data/atis/db')
    print(matcher)
