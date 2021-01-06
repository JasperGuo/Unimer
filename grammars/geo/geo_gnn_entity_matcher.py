# coding=utf8

import re
import os
import copy
import json
import numpy as np
from nltk.corpus import stopwords
from typing import List, Dict
from overrides import overrides
from allennlp.data.tokenizers import Token, WordTokenizer
from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter
from .geo_entity_extractor import funql_entity_extractor, lambda_calculus_entity_extractor, sql_entity_extractor
from .lambda_calculus_grammar import GRAMMAR_DICTIONARY


class GeoGNNEntityMatcher:

    def __init__(self, entity_path, max_ngram: int = 6):
        with open(entity_path, 'r') as f:
            self._entities = json.load(f)
        self._max_ngram = max_ngram
        self._stop_words = set(stopwords.words('english'))

    def match(self, tokens: List[Token]) -> List[Dict]:
        length = len(tokens)
        candidates = list()
        for eidx, entity in enumerate(self._entities):
            value = entity['value'].strip()
            abbreviation = entity.get('abbreviation', None)
            for tidx, t in enumerate(tokens):
                if t.text in self._stop_words:
                    continue
                for i in range(min(self._max_ngram, length - tidx)):
                    string = ' '.join([t.text for t in tokens[tidx:tidx+1+i]]).strip()
                    if string == value or (abbreviation is not None and string == abbreviation):
                        e = copy.copy(entity)
                        e['span_beg_idx'] = tidx
                        e['span_end_idx'] = tidx + 1 + i
                        candidates.append(e)
        is_remove_other_country = any([e['type'] == 'country' and e['value'] == 'usa' for e in candidates])
        valid_candidates = list()
        if is_remove_other_country:
            for candidate in candidates:
                if candidate['type'] != 'country' or candidate['value'] == 'usa':
                    valid_candidates.append(candidate)
        else:
            valid_candidates = candidates
        return valid_candidates


class GeoSQLGNNEntityMatcher(GeoGNNEntityMatcher):

    @overrides
    def match(self, tokens: List[Token]) -> List[Dict]:
        candidates = super().match(tokens)
        for number in ['1', '150000', '750']:
            candidates.append({"value": number, "type": "number"})
        return candidates


class GeoLambdaCalculusGNNEntityMatcher(GeoGNNEntityMatcher):

    SUFFIX_MAP = {
        "p": "place",
        "lo": "location",
        "m": "mountain",
        "l": "lake",
        "c": "city",
        "s": "state",
        "ro": "road",
        "r": "river"
    }

    def __init__(self, entity_path, max_ngram: int = 6):
        super().__init__(entity_path, max_ngram)
        self.get_formatted_value()

    def get_formatted_value(self):
        for state in GRAMMAR_DICTIONARY['state']:
            state_value = state.replace('"', "").replace(':s', "").replace("_", " ")
            for entity in self._entities:
                if entity['value'] == state_value and entity['type'] == 'state':
                    entity['formatted_value'] = state.replace('"', "")

        for city in GRAMMAR_DICTIONARY['city']:
            city_value = city.replace('"', "")
            match = re.match('^([a-z|_]+)_([a-z]+):c$', city_value)
            city_value = match.group(1).replace("_", " ")
            new_entities = list()
            for entity in self._entities:
                if entity['value'] == city_value and entity['type'] == 'city':
                    if "formatted_value" in entity:
                        if len(new_entities) > 0:
                            continue
                        print("Add new entities: ", city, entity)
                        ne = copy.deepcopy(entity)
                        ne['formatted_value'] = city.replace('"', "")
                        new_entities.append(ne)
                    else:
                        entity['formatted_value'] = city.replace('"', "")
            self._entities += new_entities

        for river in GRAMMAR_DICTIONARY['river']:
            # First preserve river and find all entities
            # Then, remove river
            river_value = river.replace('"', "")[:-2].replace("_", " ")
            is_found =  False
            for entity in self._entities:
                if entity['value'] == river_value and entity['type'] == 'river':
                    entity['formatted_value'] = river.replace('"', "")
                    is_found = True

            if is_found:
                continue

            assert river_value.split()[-1] == 'river'
            river_value = ' '.join(river_value.split()[:-1])
            for entity in self._entities:
                if entity['value'] == river_value and entity['type'] == 'river':
                    assert 'formatted_value' not in entity
                    entity['formatted_value'] = river.replace('"', "")

        for mountain in GRAMMAR_DICTIONARY['mountain']:
            mountain_value = mountain.replace('"', "")[:-2].replace('_', ' ')
            print(mountain_value)
            for entity in self._entities:
                if entity['value'] == mountain_value and (entity['type'] in ['mountain', 'highest point', 'lowest point']):
                    assert 'formatted_value' not in mountain_value
                    # entity['type'] = 'mountain'
                    entity['formatted_value'] = mountain.replace('"', "")

        for place in GRAMMAR_DICTIONARY['place']:
            place_value = place.replace('"', "")[:-2].replace('_', ' ')
            print(place_value)
            new_entities = list()
            for entity in self._entities:
                if entity['value'] == place_value and (entity['type'] in ['mountain', 'highest point', 'lowest point']):
                    if 'formatted_value' not in entity:
                        entity['formatted_value'] = place.replace('"', "")
                        print(entity)
                    else:
                        if len(new_entities) > 0:
                            continue
                        ne = copy.deepcopy(entity)
                        ne['formatted_value'] = place.replace('"', "")
                        new_entities.append(ne)
                        print("Add new entities: ", place, ne)
            if len(new_entities):
                self._entities += new_entities

        for name in GRAMMAR_DICTIONARY['names']:
            name_value = name.replace('"', "")[:-2].replace('_', ' ')
            new_entities = list()
            for entity in self._entities:
                if entity['value'] == name_value:
                    if 'formatted_value' not in entity:
                        entity['formatted_value'] = name.replace('"', "")
                        print(entity)
                    else:
                        if len(new_entities) > 0:
                            continue
                        ne = copy.deepcopy(entity)
                        ne['type'] = 'name'
                        ne['formatted_value'] = name.replace('"', "")
                        new_entities.append(ne)
                        print("Add new entities: ", name, ne)
            if len(new_entities):
                self._entities += new_entities

        # Country
        for entity in self._entities:
            if 'formatted_value' in entity:
                continue
            if entity['type'] == 'country':
                assert entity['abbreviation'] == 'usa'
                entity['formatted_value'] = 'usa:co'
            elif entity['value'] == 'death valley':
                entity['formatted_value'] = 'death_valley:lo'
            elif entity['type'] == 'city':
                entity['formatted_value'] = entity['value'].replace(' ', "_") + ":c"
            elif entity['type'] == 'state':
                entity['formatted_value'] = entity['value'].replace(' ', "_") + ":s"
            elif entity['type'] == 'river':
                if entity['value'].endswith('river'):
                    entity['formatted_value'] = entity['value'].replace(' ', '_') + ':r'
                else:
                    entity['formatted_value'] = entity['value'].replace(" ", "_") + "_river:r"
            elif entity['type'] in ['lowest point', 'highest point']:
                entity['formatted_value'] = entity['value'].replace(' ', '_') + ':p'
            elif entity['type'] == 'mountain':
                entity['formatted_value'] = entity['value'].replace(' ', '_') + ':m'
            elif entity['type'] == 'lake':
                entity['formatted_value'] = entity['value'].replace(' ', '_') + ':l'
            elif entity['type'] == 'road':
                entity['formatted_value'] = entity['value'].replace(' ', '_') + ':ro'

    def get_state_name_by_abbreviation(self, abbrev):
        name = None
        for entity in self._entities:
            if entity.get('abbreviation', '') == abbrev:
                name = entity['value']
        assert name is not None
        return name


    @overrides
    def match(self, tokens: List[Token]) -> List[Dict]:
        candidates = super().match(tokens)

        # Avoid duplicate value
        for cidx1, can1 in enumerate(candidates):
            for can2 in candidates[cidx1+1:]:
                if can1['value'] == can2['value'] and can1['type'] == can2['type']:
                    suffix_1, suffix_2 = can1['formatted_value'].split(':')[-1], can2['formatted_value'].split(':')[-1]
                    if suffix_1 != suffix_2:
                        suffix_2_string = self.SUFFIX_MAP[suffix_2]
                        can2['value'] = can2['value'] + ' ' + suffix_2_string
                    else:
                        if suffix_1 == 'c':
                            match1 = re.match('^([a-z|_]+)_([a-z]+):c$', can1['formatted_value'])
                            state_1 = self.get_state_name_by_abbreviation(match1.group(2))
                            can1['value'] = can1['value'] + ' ' + state_1

                            match2 = re.match('^([a-z|_]+)_([a-z]+):c$', can2['formatted_value'])
                            state_2 = self.get_state_name_by_abbreviation(match2.group(2))
                            can2['value'] = can2['value'] + ' ' + state_2
        return candidates


def test_entity_linking():
    base_path = os.path.join('../../', 'data', 'geo')
    entity_path = os.path.join(base_path, 'geo_entities.json')

    matcher = GeoSQLGNNEntityMatcher(entity_path, max_ngram=6)
    toknerizer = WordTokenizer(SpacyWordSplitter())

    import sys
    sys.path += ['../../']
    from grammars.grammar import get_grammar
    from grammars.utils import get_logical_form_preprocessor
    preprocessor = get_logical_form_preprocessor('geo', 'sql', normalize_var_with_de_brujin_index=False)
    grammar = get_grammar('geo', 'sql')

    train_data = os.path.join(base_path, 'geo_sql_question_based_train.tsv')
    empty_count = 0
    max_number_of_candidates = 0
    numbers = list()
    invalid_count = 0
    with open(train_data, 'r') as f:
        for lidx, line in enumerate(f):
            line = line.strip()
            sentence, funql = line.split('\t')
            tokens = toknerizer.tokenize(sentence)
            candidates = matcher.match(tokens)

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
            golden_entities = sql_entity_extractor(grammar, processed_funql)

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


if __name__ == '__main__':
    # base_path = os.path.join('../../', 'data', 'geo')
    # entity_path = os.path.join(base_path, 'geo_entities.json')
    #
    # matcher = GeoLambdaCalculusGNNEntityMatcher(entity_path, max_ngram=6)
    test_entity_linking()
