# coding=utf8


ROOT_RULE = 'statement -> [mquery]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY["statement"] = ['(mquery ws)']
GRAMMAR_DICTIONARY["mquery"] = [
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause)',
    '(ws select_clause ws from_clause ws where_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws where_clause)',
    '(ws select_clause ws from_clause ws groupby_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws groupby_clause)',
    '(ws select_clause ws from_clause)'
]

# SELECT
GRAMMAR_DICTIONARY["select_clause"] = [
    '(select_with_distinct ws select_results)']
GRAMMAR_DICTIONARY["select_with_distinct"] = [
    '(ws "select" ws "distinct")', '(ws "select")']
GRAMMAR_DICTIONARY["select_results"] = [
    '(ws subject ws "," ws select_results)', '(ws subject)']

# FROM
GRAMMAR_DICTIONARY["from_clause"] = ['(ws "from" ws source)']
GRAMMAR_DICTIONARY["source"] = [
    '(ws table_name ws table_alias ws "," ws source)', '(ws table_name ws table_alias)']

# ORDER
GRAMMAR_DICTIONARY["orderby_clause"] = ['ws "order by" ws subject']

# GROUP BY
GRAMMAR_DICTIONARY["groupby_clause"] = ['(ws "group by" ws subject)']

# WHERE
GRAMMAR_DICTIONARY["where_clause"] = ['(ws "where" wsp condition)']
GRAMMAR_DICTIONARY["condition"] = ['(ws single ws "and" wsp condition)',
                                   '(ws single ws "or" wsp condition)',
                                   '(single)']
GRAMMAR_DICTIONARY["single"] = ['(expr)',
                                '("(" ws condition ws ")")',
                                '("not" ws single)']

GRAMMAR_DICTIONARY["expr"] = [
    '(subject wsp "between" wsp value wsp "and" wsp value)',
    '(subject wsp "not" wsp "between" wsp value wsp "and" wsp value)',
    '(subject wsp "is" wsp "not" wsp "null")',
    '(subject wsp "not" wsp "in" wsp "(" ws mquery ws ")")',
    '(subject wsp "in" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "all" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "any" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws value)',
]
GRAMMAR_DICTIONARY["value"] = ['non_literal_number', 'string', 'col_ref']
GRAMMAR_DICTIONARY["subject"] = ['function', 'col_ref']
GRAMMAR_DICTIONARY["col_ref"] = ['(table_alias ws "." ws column_name)', '"*"']

GRAMMAR_DICTIONARY["function"] = ['(fname ws "(" ws "distinct" ws col_ref ws ")")',
                                  '(fname ws "(" ws col_ref ws ")")']
GRAMMAR_DICTIONARY["fname"] = ['"count"', '"sum"', '"max"', '"min"']

# TODO(MARK): This is not tight enough. AND/OR are strictly boolean value operators.
GRAMMAR_DICTIONARY["binaryop"] = ['"="', '"!="', '"<>"',
                                  '">="', '"<="', '">"', '"<"', '"like"', '"not like"']

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY['wsp'] = ['~"\s+"i']
GRAMMAR_DICTIONARY["table_name"] = ['"aircraft"', '"airline"', '"airport_base"', '"airport_service"',
                                    '"city"', '"class_of_service"', '"code_description"',
                                    '"compartment_class"', '"date_day"', '"days"',
                                    '"dual_carrier"', '"equipment_sequence"', '"fare_base"',
                                    '"fare_basis"', '"flight_base"', '"flight_fare"', '"flight_leg"',
                                    '"flight_stop"', '"food_service"', '"ground_service"',
                                    '"month"', '"restriction"', '"state"', '"time_interval"',
                                    '"time_zone"']

GRAMMAR_DICTIONARY["table_alias"] = [
    '"aircraft_4"', '"aircraft_1"', '"aircraft_2"', '"aircraft_3"', '"airline_1"',
    '"airport_service_6"', '"airport_service_1"', '"airport_service_2"',
    '"airport_service_3"', '"airport_service_4"', '"airport_service_5"',
    '"airport_4"', '"airport_1"', '"airport_2"', '"airport_3"', '"city_6"',
    '"city_1"', '"city_2"', '"city_3"', '"city_4"', '"city_5"',
    '"class_of_service_1"', '"date_day_5"', '"date_day_1"', '"date_day_2"',
    '"date_day_3"', '"date_day_4"', '"days_10"', '"days_1"', '"days_2"',
    '"days_3"', '"days_4"', '"days_5"', '"days_6"', '"days_7"', '"days_8"',
    '"days_9"', '"equipment_sequence_3"', '"equipment_sequence_1"',
    '"equipment_sequence_2"', '"fare_basis_6"', '"fare_basis_1"', '"fare_basis_2"',
    '"fare_basis_3"', '"fare_basis_4"', '"fare_basis_5"', '"fare_5"', '"fare_1"',
    '"fare_2"', '"fare_3"', '"fare_4"', '"flight_fare_5"', '"flight_fare_1"',
    '"flight_fare_2"', '"flight_fare_3"', '"flight_fare_4"', '"flight_leg_2"',
    '"flight_leg_1"', '"flight_stop_2"', '"flight_stop_1"', '"flight_4"',
    '"flight_1"', '"flight_2"', '"flight_3"', '"food_service_2"',
    '"food_service_1"', '"ground_service_1"', '"restriction_1"', '"state_4"',
    '"state_1"', '"state_2"', '"state_3"'
]

GRAMMAR_DICTIONARY["column_name"] = [
    '"*"', '"meal_code"', '"range_miles"', '"departure_flight_number"', '"manufacturer"',
    '"aircraft_description"', '"stop_time"', '"stop_airport"', '"fare_airline"', '"no_discounts"',
    '"engines"', '"month_name"', '"restriction_code"', '"propulsion"', '"pressurized"',
    '"from_airport"', '"wide_body"', '"flight_days"', '"time_zone_name"', '"capacity"', '"fare_id"',
    '"class_type"', '"period"', '"minimum_connect_time"', '"stops"', '"service_name"', '"city_code"',
    '"begin_time"', '"meal_description"', '"end_time"', '"minutes_distant"', '"round_trip_required"',
    '"one_direction_cost"', '"day_number"', '"flight_id"', '"time_zone_code"', '"wing_span"',
    '"length"', '"stop_number"', '"pay_load"', '"airport_code"', '"miles_distant"',
    '"hours_from_gmt"', '"departure_airline"', '"to_airport"', '"rank"', '"city_name"',
    '"dual_airline"', '"saturday_stay_required"', '"economy"', '"weight"', '"premium"',
    '"booking_class"', '"day_name"', '"airport_location"', '"ground_fare"', '"days_code"',
    '"note"', '"transport_type"', '"basic_type"', '"compartment"', '"leg_flight"',
    '"arrival_airline"', '"maximum_stay"', '"month_number"', '"minimum_stay"', '"state_name"',
    '"flight_number"', '"year"', '"airline_flight"', '"country_name"', '"arrival_flight_number"',
    '"dual_carrier"', '"meal_number"', '"class_description"', '"departure_time"', '"airline_name"',
    '"airline_code"', '"application"', '"fare_basis_code"', '"stopovers"', '"high_flight_number"',
    '"airport_name"', '"low_flight_number"', '"discounted"', '"season"', '"advance_purchase"',
    '"arrival_time"', '"basis_days"', '"leg_number"', '"main_airline"', '"aircraft_code_sequence"',
    '"stop_days"', '"time_elapsed"', '"aircraft_code_base"', '"connections"', '"state_code"', '"night"',
    '"cruising_speed"', '"direction"', '"round_trip_cost"', '"description"', '"code"', '"aircraft_code"'
]
GRAMMAR_DICTIONARY["non_literal_number"] = ['"137338"', '"1600"', '"1645"', '"2130"', '"1940"', '"1628"', '"1017"', '"2220"', '"2300"', '"1083"', '"1850"', '"1000"', '"1765"', '"1024"', '"1030"', '"1615"', '"1994"', '"1222"', '"1630"', '"1291"', '"1130"', '"2230"', '"2153"', '"1500"', '"1220"', '"1830"', '"1930"', '"1620"', '"1845"', '"1288"', '"1159"', '"1110"', '"1209"', '"1990"', '"1425"', '"1039"', '"1530"', '"2134"', '"1401"', '"1430"', '"1993"', '"1205"', '"3357"', '"1200"', '"1300"', '"1900"', '"1991"', '"1310"', '"1730"', '"2400"', '"1745"', '"1619"', '"1923"', '"2030"', '"1700"', '"1505"', '"2200"', '"2000"', '"1230"', '"4400"', '"1992"', '"2359"', '"1759"', '"1410"', '"2159"', '"2226"', '"1115"', '"2100"', '"2358"', '"2330"', '"2010"', '"1715"', '"1145"', '"1330"', '"1045"', '"1245"', '"1524"', '"1400"', '"1100"', '"3724"', '"1800"', '"727"', '"324"', '"163"', '"540"', '"106"', '"500"', '"329"', '"539"', '"650"',
                                            '"73S"', '"466"', '"645"', '"800"', '"281"', '"200"', '"417"', '"402"', '"767"', '"766"', '"323"', '"343"', '"601"', '"497"', '"720"', '"928"', '"700"', '"737"', '"269"', '"838"', '"747"', '"900"', '"72S"', '"600"', '"459"', '"257"', '"345"', '"746"', '"825"', '"932"', '"139"', '"823"', '"100"', '"400"', '"530"', '"555"', '"815"', '"813"', '"311"', '"315"', '"852"', '"201"', '"301"', '"430"', '"229"', '"930"', '"279"', '"505"', '"755"', '"415"', '"212"', '"705"', '"297"', '"150"', '"210"', '"230"', '"733"', '"352"', '"771"', '"300"', '"845"', '"630"', '"270"', '"757"', '"217"', '"271"', '"718"', '"734"', '"830"', '"730"', '"819"', '"416"', '"296"', '"31"', '"20"', '"17"', '"19"', '"27"', '"22"', '"28"', '"71"', '"82"', '"14"', '"24"', '"29"', '"21"', '"25"', '"18"', '"12"', '"13"', '"11"', '"16"', '"30"', '"98"', '"23"', '"60"', '"26"', '"15"', '"10"', '"41"', '"8"', '"0"', '"2"', '"9"', '"6"', '"5"', '"1"', '"3"', '"4"', '"7"']
GRAMMAR_DICTIONARY["string"] = ['"\'%canadian airlines international%\'"', '"\'general mitchell international\'"', '"\'stapleton international\'"', '"\'continental airlines\'"', '"\'%canadian airlines%\'"', '"\'westchester county\'"', '"\'air taxi operation\'"', '"\'salt lake city\'"', '"\'north carolina\'"', '"\'st. petersburg\'"', '"\'rapid transit\'"', '"\'san francisco\'"', '"\'indianapolis\'"', '"\'philadelphia\'"', '"\'kansas city\'"', '"\'%limousine%\'"', '"\'los angeles\'"', '"\'minneapolis\'"', '"\'%stapleton%\'"', '"\'cincinnati\'"', '"\'washington\'"', '"\'new jersey\'"', '"\'long beach\'"', '"\'fort worth\'"', '"\'rental car\'"', '"\'pittsburgh\'"', '"\'california\'"', '"\'limousine\'"', '"\'cleveland\'"', '"\'st. louis\'"', '"\'minnesota\'"', '"\'san diego\'"', '"\'baltimore\'"', '"\'las vegas\'"', '"\'nashville\'"', '"\'wednesday\'"', '"\'charlotte\'"', '"\'breakfast\'"', '"\'turboprop\'"', '"\'tennessee\'"', '"\'%pearson%\'"', '"\'milwaukee\'"', '"\'thursday\'"', '"\'columbus\'"', '"\'new york\'"', '"\'san jose\'"', '"\'colorado\'"', '"\'michigan\'"', '"\'%lester%\'"', '"\'business\'"', '"\'saturday\'"', '"\'missouri\'"', '"\'montreal\'"', '"\'st. paul\'"', '"\'phoenix\'"', '"\'burbank\'"', '"\'toronto\'"', '"\'orlando\'"', '"\'houston\'"', '"\'florida\'"', '"\'%delta%\'"', '"\'indiana\'"', '"\'arizona\'"', '"\'seattle\'"', '"\'oakland\'"', '"\'chicago\'"', '"\'georgia\'"', '"\'memphis\'"', '"\'detroit\'"', '"\'ontario\'"', '"\'atlanta\'"', '"\'tuesday\'"', '"\'boston\'"', '"\'friday\'"', '"\'newark\'"', '"\'canada\'"', '"\'dinner\'"', '"\'denver\'"',
                                '"\'quebec\'"', '"\'dallas\'"', '"\'boeing\'"', '"\'tacoma\'"', '"\'monday\'"', '"\'thrift\'"', '"\'sunday\'"', '"\'%taxi%\'"', '"\'united\'"', '"\'nevada\'"', '"\'miami\'"', '"\'daily\'"', '"\'ap/57\'"', '"\'texas\'"', '"\'ap/58\'"', '"\'coach\'"', '"\'snack\'"', '"\'lunch\'"', '"\'first\'"', '"\'ap/80\'"', '"\'usair\'"', '"\'ap/68\'"', '"\'ap/55\'"', '"\'tampa\'"', '"\'asd\'"', '"\'taxi\'"', '"\'sd/d\'"', '"\'utah\'"', '"\'%s/%\'"', '"\'ohio\'"', '"\'dc10\'"', '"\'767\'"', '"\'jfk\'"', '"\'mke\'"', '"\'pit\'"', '"\'jet\'"', '"\'bos\'"', '"\'ont\'"', '"\'mco\'"', '"\'ewr\'"', '"\'j31\'"', '"\'bwi\'"', '"\'tpa\'"', '"\'iah\'"', '"\'iad\'"', '"\'ord\'"', '"\'yyz\'"', '"\'747\'"', '"\'d/s\'"', '"\'hou\'"', '"\'727\'"', '"\'100\'"', '"\'733\'"', '"\'72s\'"', '"\'atl\'"', '"\'cvg\'"', '"\'dfw\'"', '"\'oak\'"', '"\'757\'"', '"\'f28\'"', '"\'phl\'"', '"\'m80\'"', '"\'737\'"', '"\'den\'"', '"\'mia\'"', '"\'lga\'"', '"\'bur\'"', '"\'73s\'"', '"\'slc\'"', '"\'dtw\'"', '"\'d9s\'"', '"\'lax\'"', '"\'sfo\'"', '"\'dal\'"', '"\'yes\'"', '"\'734\'"', '"\'d10\'"', '"\'bna\'"', '"\'yx\'"', '"\'tw\'"', '"\'tx\'"', '"\'qo\'"', '"\'qx\'"', '"\'hp\'"', '"\'ga\'"', '"\'bh\'"', '"\'wn\'"', '"\'ff\'"', '"\'co\'"', '"\'dl\'"', '"\'qw\'"', '"\'bb\'"', '"\'cp\'"', '"\'nx\'"', '"\'lh\'"', '"\'fn\'"', '"\'yn\'"', '"\'ap\'"', '"\'ls\'"', '"\'ca\'"', '"\'no\'"', '"\'nw\'"', '"\'s/\'"', '"\'dc\'"', '"\'sa\'"', '"\'ea\'"', '"\'ml\'"', '"\'kw\'"', '"\'us\'"', '"\'aa\'"', '"\'as\'"', '"\'ac\'"', '"\'ua\'"', '"\'q\'"', '"\'b\'"', '"\'f\'"', '"\'h\'"', '"\'y\'"', '"\'c\'"', '"\'m\'"', '"\'s\'"']

COPY_TERMINAL_SET = {"non_literal_number", "string"}
