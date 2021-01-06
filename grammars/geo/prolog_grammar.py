# coding=utf-8
"""
Prolog Grammar
"""
import copy
from typing import List, Dict
from pprint import pprint
from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar as _Grammar

# First-order logical form

ROOT_RULE = 'statement -> ["answer(" var "," goal ")"]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['("answer(" var "," goal ")")']
# Goal
GRAMMAR_DICTIONARY['goal'] = [
    '(unit_relation)',
    '(meta)',
    '("(" predicate conjunction ")")'
]
GRAMMAR_DICTIONARY['conjunction'] = [
    '("," predicate conjunction)',
    '""'
]
GRAMMAR_DICTIONARY['predicate'] = ['(meta)', '(unit_relation)', '(binary_relation)',
                                   '(declaration)', '("not" declaration)', '("not((" predicate conjunction "))")']

# Meta Predicates
GRAMMAR_DICTIONARY['meta'] = [
    '(largest)', '(smallest)', '(highest)', '(lowest)', '(longest)', '(shortest)', '(count)', '(most)', '(fewest)', '(sum)'
]
GRAMMAR_DICTIONARY['largest'] = [
    '("largest(" var "," goal ")")']
GRAMMAR_DICTIONARY['smallest'] = [
    '("smallest(" var "," goal ")")']
GRAMMAR_DICTIONARY['highest'] = [
    '("highest(" var "," goal ")")']
GRAMMAR_DICTIONARY['lowest'] = [
    '("lowest(" var "," goal ")")']
GRAMMAR_DICTIONARY['longest'] = [
    '("longest(" var "," goal ")")']
GRAMMAR_DICTIONARY['shortest'] = [
    '("shortest(" var "," goal ")")']
GRAMMAR_DICTIONARY['count'] = [
    '("count(" var "," goal "," var ")")']
GRAMMAR_DICTIONARY['most'] = [
    '("most(" var "," var "," goal")")']
GRAMMAR_DICTIONARY['fewest'] = [
    '("fewest(" var "," var "," goal")")']
GRAMMAR_DICTIONARY['sum'] = [
    '("sum(" var "," goal "," var ")")']

# Declaration
GRAMMAR_DICTIONARY['declaration'] = [
    '("const(" var "," object ")")']

# Object
GRAMMAR_DICTIONARY['object'] = [
    '("countryid(usa)")', '(city)', '(state)', '(river)', '(place)']
GRAMMAR_DICTIONARY['city'] = [
    '("cityid(" city_name "," state_abbre ")")']
GRAMMAR_DICTIONARY['state'] = ['("stateid(" state_name ")")']
GRAMMAR_DICTIONARY['river'] = ['("riverid(" river_name ")")']
GRAMMAR_DICTIONARY['place'] = ['("placeid(" place_name ")")']

# Retrieve
GRAMMAR_DICTIONARY['retrieve'] = [
    '(area)', '(len)', '(population)'
]
GRAMMAR_DICTIONARY['area'] = ['("area(" var ")")']
GRAMMAR_DICTIONARY['len'] = ['("len(" var ")")']
GRAMMAR_DICTIONARY['population'] = ['("population(" var ")")']

# Relation
GRAMMAR_DICTIONARY['unit_relation'] = [
    '(is_capital)',
    '(is_city)',
    '(is_major)',
    '(is_place)',
    '(is_river)',
    '(is_state)',
    '(is_lake)',
    '(is_mountain)',
]
GRAMMAR_DICTIONARY['is_capital'] = ['("capital(" var ")")']
GRAMMAR_DICTIONARY['is_city'] = ['("city(" var ")")']
GRAMMAR_DICTIONARY['is_major'] = ['("major(" var ")")']
GRAMMAR_DICTIONARY['is_place'] = ['("place(" var ")")']
GRAMMAR_DICTIONARY['is_river'] = ['("river(" var ")")']
GRAMMAR_DICTIONARY['is_lake'] = ['("lake(" var ")")']
GRAMMAR_DICTIONARY['is_state'] = ['("state(" var ")")']
GRAMMAR_DICTIONARY['is_mountain'] = ['("mountain(" var ")")']


GRAMMAR_DICTIONARY['binary_relation'] = [
    '(is_area)',
    '(is_captial_of)',
    '(is_equal)',
    '(is_density)',
    '(is_elevation)',
    '(is_high_point)',
    '(is_low_point)',
    '(is_higher)',
    '(is_lower)',
    '(is_longer)',
    '(is_located_in)',
    '(is_len)',
    '(is_next_to)',
    '(is_size)',
    '(is_traverse)',
    '(is_population)'
]
GRAMMAR_DICTIONARY['is_area'] = [
    '("area(" var "," var ")")']
GRAMMAR_DICTIONARY['is_captial_of'] = [
    '("capital(" var "," var ")")']
GRAMMAR_DICTIONARY['is_equal'] = [
    '"equal(" var "," var ")"']
GRAMMAR_DICTIONARY['is_density'] = [
    '"density(" var "," var ")"']
GRAMMAR_DICTIONARY['is_elevation'] = [
    '("elevation(" var "," var ")")', '("elevation(" var "," literal ")")']
GRAMMAR_DICTIONARY['is_high_point'] = [
    '("high_point(" var "," var ")")']
GRAMMAR_DICTIONARY['is_low_point'] = [
    '("low_point(" var "," var ")")']
GRAMMAR_DICTIONARY['is_higher'] = [
    '("higher(" var "," var ")")']
GRAMMAR_DICTIONARY['is_lower'] = [
    '("lower(" var "," var ")")']
GRAMMAR_DICTIONARY['is_longer'] = [
    '("longer(" var "," var ")")']
GRAMMAR_DICTIONARY['is_located_in'] = [
    '("loc(" var "," var ")")']
GRAMMAR_DICTIONARY['is_len'] = ['("len(" var "," var ")")']
GRAMMAR_DICTIONARY['is_next_to'] = [
    '("next_to(" var "," var ")")']
GRAMMAR_DICTIONARY['is_size'] = [
    '("size(" var "," var ")")']
GRAMMAR_DICTIONARY['is_traverse'] = [
    '("traverse(" var "," var ")")']
GRAMMAR_DICTIONARY['is_population'] = [
    '("population(" var "," var ")")']

# Terminal
# Original Variable
GRAMMAR_DICTIONARY['var'] = ['"a"', '"b"', '"c"',
                             '"d"', '"e"', '"f"', '"g"', '"nv"', '"v0"', '"v1"', '"v2"',
                             '"v3"', '"v4"', '"v5"', '"v6"', '"v7"']  # Normalized Variable
GRAMMAR_DICTIONARY['literal'] = ['"0"', '"0.0"', '"1.0"']
GRAMMAR_DICTIONARY['city_name'] = ['"albany"', '"tempe"', '"chicago"', '"montgomery"', '"columbus"', '"kalamazoo"', '"\'new orleans\'"', '"riverside"', '"\'fort wayne\'"', '"\'scotts valley\'"', '"boston"', '"flint"', '"dallas"', '"atlanta"', '"\'san jose\'"', '"denver"', '"plano"', '"boulder"', '"minneapolis"', '"seattle"', '"\'baton rouge\'"',
                                   '"sacramento"', '"washington"', '"\'des moines\'"', '"rochester"', '"springfield"', '"indianapolis"', '"dover"', '"detroit"', '"tucson"', '"houston"', '"portland"', '"salem"', '"durham"', '"miami"', '"\'san diego\'"', '"\'salt lake city\'"', '"spokane"', '"austin"', '"pittsburgh"', '"erie"', '"\'new york\'"', '"\'san francisco\'"', '"\'san antonio\'"']
GRAMMAR_DICTIONARY['state_abbre'] = ['"_"', '"dc"', '"sd"',
                                     '"az"', '"mo"', '"wa"', '"tx"', '"mn"', '"me"', '"ma"', '"pa"']
GRAMMAR_DICTIONARY['state_name'] = ['"\'new hampshire\'"', '"utah"', '"delaware"', '"tennessee"', '"\'new mexico\'"', '"oregon"', '"arizona"', '"iowa"',
                                    '"georgia"', '"arkansas"', '"pennsylvania"', '"oklahoma"', '"illinois"', '"kentucky"', '"wisconsin"', '"\'new jersey\'"', '"hawaii"', '"minnesota"', '"nebraska"', '"maryland"', '"massachusetts"', '"mississippi"',
                                    '"nevada"', '"\'south carolina\'"', '"kansas"', '"idaho"', '"michigan"', '"alabama"', '"louisiana"', '"virginia"', '"washington"', '"california"', '"alaska"', '"texas"', '"colorado"', '"missouri"', '"vermont"', '"montana"', '"florida"', '"wyoming"', '"ohio"', '"\'west virginia\'"', '"indiana"', '"\'north carolina\'"', '"\'rhode island\'"', '"maine"', '"\'new york\'"', '"\'north dakota\'"', '"\'south dakota\'"']
GRAMMAR_DICTIONARY['river_name'] = ['"ohio"', '"\'rio grande\'"', '"delaware"', '"\'north platte\'"',
                                    '"chattahoochee"', '"mississippi"', '"colorado"', '"missouri"', '"red"', '"potomac"']
GRAMMAR_DICTIONARY['place_name'] = ['"\'death valley\'"',
                                    '"\'mount whitney\'"', '"\'mount mckinley\'"', '"\'guadalupe peak\'"']

COPY_TERMINAL_SET = {'literal', 'city_name', 'state_abbre',
                     'state_name', 'river_name', 'place_name'}
