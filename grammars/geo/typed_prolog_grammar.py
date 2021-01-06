# codinng=utf8

ROOT_RULE = 'statement -> ["answer(" Var "," Form ")"]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['("answer(" Var "," Form ")")']

# Variable
GRAMMAR_DICTIONARY['Var'] = ['"a"', '"b"', '"c"',
                             '"d"', '"e"', '"f"', '"g"', '"nv"', '"v0"', '"v1"', '"v2"',
                             '"v3"', '"v4"', '"v5"', '"v6"', '"v7"']  # Normalized Variable

GRAMMAR_DICTIONARY['Form'] = [
    '("(" Form conjunction ")")',
    '("area(" Var "," Var ")")',
    '("capital(" Var ")")',
    '("capital(" Var "," Var ")")',
    '("city(" Var ")")',
    '("country(" Var ")")',
    '("state(" Var ")")',
    '("lake(" Var ")")',
    '("river(" Var ")")',
    '("mountain(" Var ")")',
    '("place(" Var ")")',
    '("major(" Var ")")',
    '("const(" Var "," City ")")',
    '("const(" Var "," "countryid(usa)" ")")',
    '("const(" Var "," Place ")")',
    '("const(" Var "," River ")")',
    '("const(" Var "," State ")")',
    '("count(" Var "," Form "," Var ")")',
    '("density(" Var "," Var ")")',
    '("elevation(" Var "," Num ")")',
    '("elevation(" Var "," Var ")")',
    '("fewest(" Var "," Var "," Form ")")',
    '("high_point(" Var "," Var ")")',
    '("higher(" Var "," Var ")")',
    '("highest(" Var "," Form ")")',
    '("largest(" Var "," Form ")")',
    '("len(" Var "," Var ")")',
    '("loc(" Var "," Var ")")',
    '("longer(" Var "," Var ")")',
    '("longest(" Var "," Form ")")',
    '("low_point(" Var "," Var ")")',
    '("lower(" Var "," Var ")")',
    '("lowest(" Var "," Form ")")',
    '("most(" Var "," Var "," Form ")")',
    '("next_to(" Var "," Var ")")',
    '("not(" Form ")")',
    '("population(" Var "," Var ")")',
    '("shortest(" Var "," Form ")")',
    '("size(" Var "," Var ")")',
    '("smallest(" Var "," Form ")")',
    '("sum(" Var "," Form "," Var ")")',
    '("traverse(" Var "," Var ")")'
]

GRAMMAR_DICTIONARY['conjunction'] = [
    '("," Form conjunction)',
    '""'
]

GRAMMAR_DICTIONARY['City'] = [
    '("cityid(" CityName "," StateAbbrev ")")',
    '("cityid(" CityName ",_)")',
]
GRAMMAR_DICTIONARY['State'] = ['("stateid(" StateName ")")']
GRAMMAR_DICTIONARY['River'] = ['("riverid(" RiverName ")")']
GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']

GRAMMAR_DICTIONARY['Place'] = ['("placeid(" PlaceName ")")']

GRAMMAR_DICTIONARY['Num'] = ['"0.0"', '"1.0"', '"0"']

GRAMMAR_DICTIONARY['CityName'] = ['"albany"', '"tempe"', '"chicago"', '"montgomery"', '"columbus"', '"kalamazoo"', '"\'new orleans\'"', '"riverside"', '"\'fort wayne\'"', '"\'scotts valley\'"', '"boston"', '"flint"', '"dallas"', '"atlanta"', '"\'san jose\'"', '"denver"', '"plano"', '"boulder"', '"minneapolis"', '"seattle"', '"\'baton rouge\'"',
                                   '"sacramento"', '"washington"', '"\'des moines\'"', '"rochester"', '"springfield"', '"indianapolis"', '"dover"', '"detroit"', '"tucson"', '"houston"', '"portland"', '"salem"', '"durham"', '"miami"', '"\'san diego\'"', '"\'salt lake city\'"', '"spokane"', '"austin"', '"pittsburgh"', '"erie"', '"\'new york\'"', '"\'san francisco\'"', '"\'san antonio\'"']
GRAMMAR_DICTIONARY['StateAbbrev'] = ['"_"', '"dc"', '"sd"',
                                     '"az"', '"mo"', '"wa"', '"tx"', '"mn"', '"me"', '"ma"', '"pa"']
GRAMMAR_DICTIONARY['StateName'] = ['"\'new hampshire\'"', '"utah"', '"delaware"', '"tennessee"', '"\'new mexico\'"', '"oregon"', '"arizona"', '"iowa"',
                                    '"georgia"', '"arkansas"', '"pennsylvania"', '"oklahoma"', '"illinois"', '"kentucky"', '"wisconsin"', '"\'new jersey\'"', '"hawaii"', '"minnesota"', '"nebraska"', '"maryland"', '"massachusetts"', '"mississippi"',
                                    '"nevada"', '"\'south carolina\'"', '"kansas"', '"idaho"', '"michigan"', '"alabama"', '"louisiana"', '"virginia"', '"washington"', '"california"', '"alaska"', '"texas"', '"colorado"', '"missouri"', '"vermont"', '"montana"', '"florida"', '"wyoming"', '"ohio"', '"\'west virginia\'"', '"indiana"', '"\'north carolina\'"', '"\'rhode island\'"', '"maine"', '"\'new york\'"', '"\'north dakota\'"', '"\'south dakota\'"']
GRAMMAR_DICTIONARY['RiverName'] = ['"ohio"', '"\'rio grande\'"', '"delaware"', '"\'north platte\'"',
                                    '"chattahoochee"', '"mississippi"', '"colorado"', '"missouri"', '"red"', '"potomac"']
GRAMMAR_DICTIONARY['PlaceName'] = ['"\'death valley\'"',
                                    '"\'mount whitney\'"', '"\'mount mckinley\'"', '"\'guadalupe peak\'"']

COPY_TERMINAL_SET = {'Num', 'CityName', 'StateAbbrev', 'StateName',
                     'RiverName', 'PlaceName'}