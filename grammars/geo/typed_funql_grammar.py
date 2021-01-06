# coding=utf8

"""
Typed Prolog Grammar
"""

ROOT_RULE = 'statement -> [Query]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['(Query ws)']
GRAMMAR_DICTIONARY['Query'] = [
    '("answer(" City ")")',
    '("answer(" Country ")")',
    '("answer(" Num ")")',
    '("answer(" Place ")")',
    '("answer(" State ")")',
    '("answer(" River ")")',
]

# Country
GRAMMAR_DICTIONARY['Country'] = [
    '("countryid(\'usa\')")',
    '("country(all)")',
    '("each(" Country ")")',
    '("exclude(" Country "," Country ")")',
    '("intersection(" Country "," Country ")")',
    '("largest(" Country ")")',
    '("smallest(" Country ")")',
    '("loc_1(" City ")")',
    '("loc_1(" Place ")")',
    '("loc_1(" River ")")',
    '("loc_1(" State ")")',
    '("most(" Country ")")',
    '("traverse_1(" River ")")',
]

# State
GRAMMAR_DICTIONARY['State'] = [
    '("stateid(" StateName ")")',
    '("state(" State ")")',
    '("state(all)")',
    '("smallest(" State ")")',
    '("smallest_one(area_1(" State "))")',
    '("smallest_one(density_1(" State "))")',
    '("smallest_one(population_1(" State "))")',
    '("largest(" State ")")',
    '("largest_one(area_1(" State "))")',
    '("largest_one(density_1(" State "))")',
    '("largest_one(population_1(" State "))")',
    '("each(" State ")")',
    '("exclude(" State "," State ")")',
    '("intersection(" State "," State ")")',
    '("fewest(" State ")")',
    '("most(" State ")")',
    '("most(" Place ")")',
    '("most(" River ")")',
    '("most(" City ")")',
    '("next_to_1(" State ")")',
    '("next_to_2(" State ")")',
    '("next_to_2(" River ")")',
    '("traverse_1(" River ")")',
    '("loc_1(" River ")")',
    '("capital_2(" City ")")',
    '("loc_1(" City ")")',
    '("high_point_2(" Place ")")',
    '("low_point_2(" Place ")")',
    '("loc_1(" Place ")")',
    '("loc_2(" Country ")")',
]
GRAMMAR_DICTIONARY['StateAbbrev'] = ['"\'dc\'"', '"\'pa\'"', '"\'ga\'"', '"\'me\'"', '"\'wa\'"', '"\'tx\'"',
                                     '"\'ma\'"', '"\'sd\'"', '"\'az\'"', '"\'mn\'"', '"\'mo\'"']
GRAMMAR_DICTIONARY['StateName'] = ['"\'washington\'"', '"\'kansas\'"', '"\'pennsylvania\'"', '"\'new york\'"', '"\'south carolina\'"', '"\'california\'"', '"\'west virginia\'"', '"\'kentucky\'"', '"\'vermont\'"', '"\'hawaii\'"', '"\'new mexico\'"', '"\'montana\'"', '"\'illinois\'"', '"\'georgia\'"', '"\'louisiana\'"', '"\'indiana\'"', '"\'oklahoma\'"', '"\'utah\'"', '"\'arkansas\'"', '"\'michigan\'"', '"\'alaska\'"', '"\'alabama\'"', '"\'missouri\'"', '"\'wisconsin\'"', '"\'wyoming\'"',
                                   '"\'maine\'"', '"\'florida\'"', '"\'south dakota\'"', '"\'tennessee\'"', '"\'north carolina\'"', '"\'new jersey\'"', '"\'minnesota\'"', '"\'arizona\'"', '"\'new hampshire\'"', '"\'texas\'"', '"\'colorado\'"', '"\'mississippi\'"', '"\'idaho\'"', '"\'oregon\'"', '"\'maryland\'"', '"\'north dakota\'"', '"\'nebraska\'"', '"\'rhode island\'"', '"\'ohio\'"', '"\'massachusetts\'"', '"\'virginia\'"', '"\'nevada\'"', '"\'delaware\'"', '"\'iowa\'"']

# City
GRAMMAR_DICTIONARY['City'] = [
    '("city(all)")',
    '("city(" City ")")',
    '("loc_2(" State ws ")")',
    '("loc_2(" Country ")")',
    '("capital(" City ")")',
    '("capital(" Place ")")',
    '("capital(all)")',
    '("capital_1(" Country ")")',
    '("capital_1(" State ")")',
    '("cityid(" CityName "," StateAbbrev ")")',
    '("cityid(" CityName ",_)")',
    '("each(" City ")")',
    '("exclude(" City "," City ")")',
    '("intersection(" City "," City ")")',
    '("fewest(" City ")")',
    '("largest(" City ")")',
    '("largest_one(density_1(" City "))")',
    '("largest_one(population_1(" City "))")',
    '("largest_one(density_1(" City "))")',
    '("smallest(" City ")")',
    '("smallest_one(population_1(" City "))")',
    '("loc_1(" Place ")")',
    '("major(" City ")")',
    '("most(" City ")")',
    '("traverse_1(" River ")")',
]
GRAMMAR_DICTIONARY['CityName'] = ['"\'washington\'"', '"\'minneapolis\'"', '"\'sacramento\'"', '"\'rochester\'"', '"\'indianapolis\'"', '"\'portland\'"', '"\'new york\'"', '"\'erie\'"', '"\'san diego\'"', '"\'baton rouge\'"', '"\'miami\'"', '"\'kalamazoo\'"', '"\'durham\'"', '"\'salt lake city\'"', '"\'des moines\'"', '"\'pittsburgh\'"', '"\'riverside\'"', '"\'dover\'"', '"\'chicago\'"', '"\'albany\'"', '"\'tucson\'"', '"\'austin\'"',
                                   '"\'san antonio\'"', '"\'houston\'"', '"\'scotts valley\'"', '"\'montgomery\'"', '"\'springfield\'"', '"\'boston\'"', '"\'boulder\'"', '"\'san francisco\'"', '"\'flint\'"', '"\'fort wayne\'"', '"\'spokane\'"', '"\'san jose\'"', '"\'tempe\'"', '"\'dallas\'"', '"\'new orleans\'"', '"\'seattle\'"', '"\'denver\'"', '"\'salem\'"', '"\'detroit\'"', '"\'plano\'"', '"\'atlanta\'"', '"\'columbus\'"']

# Num
GRAMMAR_DICTIONARY['Num'] = [
    '(Digit)',
    '("area_1(" City ")")',
    '("area_1(" Country ")")',
    '("area_1(" Place ")")',
    '("area_1(" State ")")',
    '("count(" City ")")',
    '("count(" Country ")")',
    '("count(" Place ")")',
    '("count(" River ")")',
    '("count(" State ")")',
    '("density_1(" City ")")',
    '("density_1(" Country ")")',
    '("density_1(" State ")")',
    '("elevation_1(" Place ")")',
    '("population_1(" City ")")',
    '("population_1(" Country ")")',
    '("population_1(" State ")")',
    '("size(" City ")")',
    '("size(" Country ")")',
    '("size(" State ")")',
    '("smallest(" Num ")")',
    '("sum(" Num ")")',
    '("len(" River  ")")'
]
GRAMMAR_DICTIONARY['Digit'] = ['"0.0"', '"1.0"', '"0"']

# Place
GRAMMAR_DICTIONARY['Place'] = [
    '("loc_2(" City ")")',
    '("loc_2(" State ")")',
    '("loc_2(" Country ws")")',
    '("each(" Place ")")',
    '("elevation_2(" Num ")")',
    '("exclude(" Place "," Place ")")',
    '("intersection(" Place "," Place ")")',
    '("fewest(" Place ")")',
    # '("most(" Place ")")',
    '("largest(" Place ")")',
    '("smallest(" Place ")")',
    '("highest(" Place ")")',
    '("lowest(" Place ")")',
    '("high_point_1(" State ")")',
    '("low_point_1(" State ")")',
    '("higher_1(" Place ")")',
    '("higher_2(" Place ")")',
    '("lower_1(" Place ")")',
    '("lower_2(" Place ")")',
    '("lake(" Place ")")',
    '("lake(all)")',
    '("mountain(" Place ")")',
    '("mountain(all)")',
    '("place(" Place ")")',
    '("place(all)")',
    '("placeid(" PlaceName ")")',
    '("major(" Place ")")'
]
GRAMMAR_DICTIONARY['PlaceName'] = ['"\'guadalupe peak\'"', '"\'mount whitney\'"',
                                    '"\'mount mckinley\'"', '"\'death valley\'"']

# River
GRAMMAR_DICTIONARY['River'] = [
    '("river(" River ")")',
    '("loc_2(" State ")")',
    '("loc_2(" Country ")")',
    '("each(" River ")")',
    '("exclude(" River "," River ")")',
    '("intersection(" River "," River ")")',
    '("fewest(" River ")")',
    '("longer(" River ")")',
    '("longest(" River ")")',
    '("major(" River ")")',
    # '("most(" River ")")',
    '("most(" State ws")")',
    '("river(all)")',
    '("riverid(" RiverName ")")',
    '("shortest(" River ")")',
    '("traverse_2(" City ")")',
    '("traverse_2(" Country ")")',
    '("traverse_2(" State ")")',
]
GRAMMAR_DICTIONARY['RiverName'] = ['"\'chattahoochee\'"', '"\'north platte\'"', '"\'rio grande\'"', '"\'ohio\'"',
                                    '"\'potomac\'"', '"\'missouri\'"', '"\'red\'"', '"\'colorado\'"', '"\'mississippi\'"', '"\'delaware\'"']
GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']

COPY_TERMINAL_SET = {'RiverName', 'PlaceName', 'Digit', 'CityName',
                     'StateName', 'StateAbbrev'}