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
    '(subject wsp "between" wsp time_value wsp "and" wsp time_value)',
    '(subject wsp "not" wsp "between" wsp time_value wsp "and" wsp time_value)',
    '(subject wsp "is" wsp "not" wsp "null")',
    '(subject wsp "not" wsp "in" wsp "(" ws mquery ws ")")',
    '(subject wsp "in" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "all" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "any" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "(" ws mquery ws ")")',
    '(concrete_value_expr)',
    '(subject ws binaryop ws col_ref)',
]

GRAMMAR_DICTIONARY["value"] = ['col_ref']
GRAMMAR_DICTIONARY["subject"] = ['function', 'col_ref']
GRAMMAR_DICTIONARY["col_ref"] = ['table_columns', '"*"']

GRAMMAR_DICTIONARY["function"] = ['(fname ws "(" ws "distinct" ws col_ref ws ")")',
                                  '(fname ws "(" ws col_ref ws ")")']
GRAMMAR_DICTIONARY["fname"] = ['"count"', '"sum"', '"max"', '"min"']

# TODO(MARK): This is not tight enough. AND/OR are strictly boolean value operators.
GRAMMAR_DICTIONARY["binaryop"] = ['"="', '"!="', '"<>"',
                                  '">="', '"<="', '">"', '"<"', '"like"', '"not like"']

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY['wsp'] = ['~"\s+"i']

GRAMMAR_DICTIONARY["table_name"] = ['"aircraft"', '"airline"', '"airport_base"', '"airport_service"', '"fare_basis"',
                                    '"city"', '"class_of_service"','"date_day"', '"days"', '"equipment_sequence"', '"fare_base"',
                                    '"flight_base"', '"flight_fare"', '"flight_leg"',
                                    '"flight_stop"', '"food_service"', '"ground_service"', '"restriction"', '"state"',]

GRAMMAR_DICTIONARY["table_alias"] = [
    'aircraft_alias', '"airline_1"', 'airport_base_alias', 'airport_service_alias', 'fare_basis_alias',
    'city_alias', '"class_of_service_1"', 'date_day_alias', 'days_alias', 'equipment_sequence_alias',
    'fare_base_alias', 'flight_base_alias', 'flight_fare_alias', 'flight_leg_alias',
    '"restriction_1"', 'state_alias', 'flight_stop_alias', 'food_service_alias', '"ground_service_1"'
]

GRAMMAR_DICTIONARY['aircraft_alias'] = [
    '"aircraft_4"', '"aircraft_1"', '"aircraft_2"', '"aircraft_3"',
]
GRAMMAR_DICTIONARY['airline_alias'] = ['"airline_1"']
GRAMMAR_DICTIONARY['airport_base_alias'] = ['"airport_4"', '"airport_1"', '"airport_2"', '"airport_3"', ]
GRAMMAR_DICTIONARY['airport_service_alias'] = ['"airport_service_6"', '"airport_service_1"', '"airport_service_2"',
                                         '"airport_service_3"', '"airport_service_4"', '"airport_service_5"',]
GRAMMAR_DICTIONARY['city_alias'] = [
    '"city_6"', '"city_1"', '"city_2"', '"city_3"', '"city_4"', '"city_5"',
]
GRAMMAR_DICTIONARY['class_of_service_alias'] = ['"class_of_service_1"']
GRAMMAR_DICTIONARY['date_day_alias'] = [
    '"date_day_5"', '"date_day_1"', '"date_day_2"',
    '"date_day_3"', '"date_day_4"',
]
GRAMMAR_DICTIONARY['days_alias'] = [
    '"days_10"', '"days_1"', '"days_2"',
    '"days_3"', '"days_4"', '"days_5"', '"days_6"', '"days_7"', '"days_8"',
    '"days_9"',
]
GRAMMAR_DICTIONARY['equipment_sequence_alias'] = [
    '"equipment_sequence_3"', '"equipment_sequence_1"',
    '"equipment_sequence_2"',
]
GRAMMAR_DICTIONARY['fare_base_alias'] = [
    '"fare_5"', '"fare_1"',
    '"fare_2"', '"fare_3"', '"fare_4"',
]
GRAMMAR_DICTIONARY['fare_basis_alias'] = [
    '"fare_basis_6"', '"fare_basis_1"', '"fare_basis_2"',
    '"fare_basis_3"', '"fare_basis_4"', '"fare_basis_5"',
]
GRAMMAR_DICTIONARY['flight_base_alias'] = [
    '"flight_1"', '"flight_2"', '"flight_3"', '"flight_4"',
]
GRAMMAR_DICTIONARY['flight_fare_alias'] = [
    '"flight_fare_5"', '"flight_fare_2"', '"flight_fare_3"', '"flight_fare_4"', '"flight_fare_1"'
]
GRAMMAR_DICTIONARY['flight_leg_alias'] = [
    '"flight_leg_2"', '"flight_leg_1"'
]
GRAMMAR_DICTIONARY['flight_stop_alias'] = [
    '"flight_stop_2"', '"flight_stop_1"',
]
GRAMMAR_DICTIONARY['food_service_alias'] = [
    '"food_service_2"', '"food_service_1"'
]
# GRAMMAR_DICTIONARY['ground_service_alias'] = ['"ground_service_1"']
GRAMMAR_DICTIONARY['state_alias'] = [
    '"state_4"', '"state_1"', '"state_2"', '"state_3"'
]
GRAMMAR_DICTIONARY['restriction_alias'] = ['"restriction_1"']

# Column Name
GRAMMAR_DICTIONARY['table_columns'] = [
    '(aircraft_alias ws "." ws aircraft_columns)',
    '("airline_1" ws "." ws airline_columns)',
    '(airport_base_alias ws "." ws airport_base_columns)',
    '(airport_service_alias ws "." ws airport_service_columns)',
    '(city_alias ws "." ws city_columns)',
    '("class_of_service_1" ws "." ws class_of_service_columns)',
    '(date_day_alias ws "." ws date_day_columns)',
    '(days_alias ws "." ws days_columns)',
    '(equipment_sequence_alias ws "." ws equipment_sequence_columns)',
    '(fare_base_alias ws "." ws fare_base_columns)',
    '(fare_basis_alias ws "." ws fare_basis_columns)',
    '(flight_base_alias ws "." ws flight_base_columns)',
    '(flight_fare_alias ws "." ws flight_fare_columns)',
    '(flight_leg_alias ws "." ws flight_leg_columns)',
    '(flight_stop_alias ws "." ws flight_stop_columns)',
    '(food_service_alias ws "." ws food_service_columns)',
    '("ground_service_1" ws "." ws ground_service_columns)',
    '(state_alias ws "." ws state_colums)',
    '("restriction_1" ws "." ws restriction_columns)',
]

GRAMMAR_DICTIONARY['aircraft_columns'] = [
    '"capacity"', '"manufacturer"', '"basic_type"', '"propulsion"', '"aircraft_code_base"']
GRAMMAR_DICTIONARY['airline_columns'] = [
    '"airline_name"', '"airline_code"', '"note"']
GRAMMAR_DICTIONARY['airport_base_columns'] = ['"state_code"', '"airport_code"', '"airport_location"', '"minimum_connect_time"', '"time_zone_code"', '"country_name"', '"airport_name"']
GRAMMAR_DICTIONARY['airport_service_columns'] = [
    '"miles_distant"', '"minutes_distant"', '"airport_code"', '"city_code"']
GRAMMAR_DICTIONARY['city_columns'] = ['"city_code"', '"time_zone_code"', '"country_name"', '"city_name"', '"state_code"']
GRAMMAR_DICTIONARY['class_of_service_columns'] = ['"rank"', '"class_description"', '"booking_class"']
GRAMMAR_DICTIONARY['date_day_columns'] = [
    '"day_name"', '"day_number"', '"month_number"', '"year"']
GRAMMAR_DICTIONARY['days_columns'] = ['"days_code"', '"day_name"']
GRAMMAR_DICTIONARY['equipment_sequence_columns'] = [
    '"aircraft_code_base"', '"aircraft_code_sequence"']
GRAMMAR_DICTIONARY['flight_base_columns'] = ['"connections"', '"meal_code"', '"flight_days"', '"flight_id"', '"from_airport"', '"flight_number"',
                                             '"airline_code"', '"to_airport"', '"departure_time"', '"aircraft_code_sequence"', '"time_elapsed"', '"stops"', '"arrival_time"']
GRAMMAR_DICTIONARY['fare_base_columns'] = ['"restriction_code"', '"fare_id"', '"from_airport"', '"flight_id"',
                                           '"fare_airline"', '"fare_basis_code"', '"to_airport"', '"one_direction_cost"', '"round_trip_required"', '"round_trip_cost"']
GRAMMAR_DICTIONARY['fare_basis_columns'] = ['"booking_class"', '"economy"',
                                            '"basis_days"', '"fare_basis_code"', '"class_type"', '"discounted"']
GRAMMAR_DICTIONARY['flight_fare_columns'] = ['"fare_id"', '"flight_id"']
GRAMMAR_DICTIONARY['flight_leg_columns'] = ['"leg_flight"', '"flight_id"']
GRAMMAR_DICTIONARY['flight_stop_columns'] = [
    '"arrival_time"', '"flight_id"', '"stop_number"', '"stop_airport"']
GRAMMAR_DICTIONARY['food_service_columns'] = ['"meal_code"',
                                              '"meal_description"', '"meal_number"', '"compartment"']
GRAMMAR_DICTIONARY['ground_service_columns'] = [
    '"ground_fare"', '"airport_code"', '"transport_type"', '"city_code"']
GRAMMAR_DICTIONARY['state_colums'] = ['"state_code"', '"state_name"']
GRAMMAR_DICTIONARY['restriction_columns'] = ['"advance_purchase"', '"stopovers"', '"minimum_stay"',
                                             '"application"', '"maximum_stay"', '"saturday_stay_required"', '"restriction_code"', '"no_discounts"']

# Column Values
GRAMMAR_DICTIONARY['concrete_value_expr'] = [
    '(days_alias ws "." ws "days_code" ws binaryop ws days_code_value)',
    '(days_alias ws "." ws "day_name" ws binaryop ws  day_name_value)',
    '(fare_basis_alias ws "." ws "fare_basis_code" ws binaryop ws fare_basis_code_value)',
    '(fare_basis_alias ws "." ws "class_type" ws binaryop ws class_type_value)',
    '(fare_basis_alias ws "." ws "economy" ws binaryop ws economy_value)',
    '(fare_basis_alias ws "." ws "discounted" ws binaryop ws discounted_value)',
    '(fare_basis_alias ws "." ws "booking_class" ws binaryop ws booking_class_value)',
    '(fare_base_alias ws "." ws "round_trip_required" ws binaryop ws round_trip_required_value)',
    '(fare_base_alias ws "." ws "fare_basis_code" ws binaryop ws fare_basis_code_value)',
    '(aircraft_alias ws "." ws "manufacturer" ws binaryop ws manufacturer_value)',
    '(aircraft_alias ws "." ws "basic_type" ws binaryop ws basic_type_value)',
    '(aircraft_alias ws "." ws "aircraft_code_base" ws binaryop ws aircraft_code_value)',
    '(aircraft_alias ws "." ws "propulsion" ws binaryop ws propulsion_value)',
    '(airport_base_alias ws "." ws "airport_code" ws binaryop ws airport_code_value)',
    '(airport_base_alias ws "." ws "airport_name" ws binaryop ws airport_name_value)',
    '(city_alias ws "." ws "city_name" ws binaryop ws city_name_value)',
    '(city_alias ws "." ws "country_name" ws binaryop ws country_name_value)',
    '(city_alias ws "." ws "state_code" ws binaryop ws state_code_value)',
    '(state_alias ws "." ws "state_code" ws binaryop ws state_code_value)',
    '(state_alias ws "." ws "state_name" ws binaryop ws state_name_value)',
    '(flight_base_alias ws "." ws "airline_code" ws binaryop ws airline_code_value)',
    '(flight_base_alias ws "." ws "flight_days" ws binaryop ws flight_days_value)',
    '(flight_base_alias ws "." ws "meal_code" ws binaryop ws meal_code_value)',
    '("airline_1" ws "." ws "airline_code" ws binaryop ws airline_code_value)',
    '("airline_1" ws "." ws "airline_name" ws binaryop ws airline_name_value)',
    '("ground_service_1" ws "." ws "transport_type" ws binaryop ws transport_type_value)',
    '(food_service_alias ws "." ws "meal_description" ws binaryop ws meal_description_value)',
    '(food_service_alias ws "." ws "meal_code" ws binaryop ws meal_code_value)',
    '(airport_service_alias ws "." ws "airport_code" ws binaryop ws airport_code_value)',
    '("restriction_1" ws "." ws "restriction_code" ws binaryop ws restriction_code_value)',
    '("class_of_service_1" ws "." ws "booking_class" ws binaryop ws booking_class_value)',
    # Numerical
    '(date_day_alias ws "." ws "year" ws binaryop ws year_value)',
    '(date_day_alias ws "." ws "month_number" ws binaryop ws month_number_value)',
    '(date_day_alias ws "." ws "day_number" ws binaryop ws day_number_value)',
    '(flight_stop_alias ws "." ws "arrival_time" ws binaryop ws time_value)',
    '(flight_base_alias ws "." ws "flight_number" ws binaryop ws flight_number_value)',
    '(flight_base_alias ws "." ws "connections" ws binaryop ws connections_value)',
    '(flight_base_alias ws "." ws "arrival_time" ws binaryop ws time_value)',
    '(flight_base_alias ws "." ws "departure_time" ws binaryop ws time_value)',
    '(flight_base_alias ws "." ws "stops" ws binaryop ws stops_value)',
    '(flight_base_alias ws "." ws "time_elapsed" ws binaryop ws time_elapsed_value)',
    '(fare_base_alias ws "." ws "one_direction_cost" ws binaryop ws one_direction_cost_value)',
    '(fare_base_alias ws "." ws "round_trip_cost" ws binaryop ws round_trip_cost_value)',
]

GRAMMAR_DICTIONARY['airport_code_value'] = ['"\'iah\'"', '"\'sfo\'"', '"\'tpa\'"', '"\'jfk\'"', '"\'cvg\'"', '"\'dfw\'"', '"\'mco\'"', '"\'phl\'"', '"\'lga\'"', '"\'lax\'"', '"\'yyz\'"', '"\'bwi\'"', '"\'oak\'"',
                                            '"\'slc\'"', '"\'ont\'"', '"\'pit\'"', '"\'hou\'"', '"\'mia\'"', '"\'den\'"', '"\'bur\'"', '"\'ord\'"', '"\'dtw\'"', '"\'mke\'"', '"\'bna\'"', '"\'iad\'"', '"\'bos\'"', '"\'atl\'"', '"\'ewr\'"', '"\'dal\'"']
GRAMMAR_DICTIONARY['city_name_value'] = ['"\'salt lake city\'"', '"\'san jose\'"', '"\'newark\'"', '"\'montreal\'"', '"\'st. paul\'"', '"\'ontario\'"', '"\'orlando\'"', '"\'minneapolis\'"', '"\'westchester county\'"', '"\'memphis\'"', '"\'chicago\'"', '"\'tampa\'"', '"\'pittsburgh\'"', '"\'toronto\'"', '"\'houston\'"', '"\'detroit\'"', '"\'new york\'"', '"\'cleveland\'"', '"\'columbus\'"', '"\'nashville\'"', '"\'tacoma\'"', '"\'philadelphia\'"',
                                         '"\'las vegas\'"', '"\'denver\'"', '"\'san diego\'"', '"\'miami\'"', '"\'indianapolis\'"', '"\'burbank\'"', '"\'cincinnati\'"', '"\'fort worth\'"', '"\'milwaukee\'"', '"\'boston\'"', '"\'baltimore\'"', '"\'dallas\'"', '"\'seattle\'"', '"\'atlanta\'"', '"\'kansas city\'"', '"\'los angeles\'"', '"\'phoenix\'"', '"\'oakland\'"', '"\'san francisco\'"', '"\'washington\'"', '"\'st. louis\'"', '"\'charlotte\'"', '"\'st. petersburg\'"', '"\'long beach\'"']
GRAMMAR_DICTIONARY['round_trip_required_value'] = ['"\'no\'"', '"\'yes\'"']
GRAMMAR_DICTIONARY['airline_code_value'] = ['"\'ua\'"', '"\'cp\'"', '"\'ea\'"', '"\'ac\'"', '"\'ml\'"', '"\'as\'"', '"\'lh\'"', '"\'dl\'"',
                                            '"\'nw\'"', '"\'us\'"', '"\'yx\'"', '"\'tw\'"', '"\'wn\'"', '"\'ff\'"', '"\'nx\'"', '"\'kw\'"', '"\'co\'"', '"\'hp\'"', '"\'aa\'"']
GRAMMAR_DICTIONARY['day_name_value'] = ['"\'monday\'"', '"\'friday\'"', '"\'tuesday\'"',
                                        '"\'thursday\'"', '"\'sunday\'"', '"\'saturday\'"', '"\'wednesday\'"']
GRAMMAR_DICTIONARY['aircraft_code_value'] = ['"\'757\'"', '"\'m80\'"', '"\'733\'"', '"\'j31\'"',
                                             '"\'73s\'"', '"\'72s\'"', '"\'734\'"', '"\'d9s\'"', '"\'f28\'"', '"\'100\'"', '"\'d10\'"']
GRAMMAR_DICTIONARY['meal_code_value'] = ['"\'%s/%\'"', '"\'s\'"',
                                         '"\'bb\'"', '"\'b\'"', '"\'s/\'"', '"\'sd/d\'"', '"\'ls\'"', '"\'d/s\'"']
GRAMMAR_DICTIONARY['state_name_value'] = ['"\'nevada\'"', '"\'ohio\'"', '"\'michigan\'"', '"\'minnesota\'"', '"\'new jersey\'"', '"\'colorado\'"', '"\'indiana\'"', '"\'california\'"',
                                          '"\'washington\'"', '"\'georgia\'"', '"\'north carolina\'"', '"\'texas\'"', '"\'new york\'"', '"\'quebec\'"', '"\'utah\'"', '"\'missouri\'"', '"\'arizona\'"', '"\'florida\'"', '"\'tennessee\'"']
GRAMMAR_DICTIONARY['class_type_value'] = ['"\'first\'"',
                                          '"\'coach\'"', '"\'business\'"', '"\'thrift\'"']
GRAMMAR_DICTIONARY['transport_type_value'] = ['"\'rapid transit\'"',
                                              '"\'rental car\'"', '"\'air taxi operation\'"', '"\'taxi\'"', '"\'limousine\'"',
                                              '"\'%limousine%\'"', '"\'%taxi%\'"']
GRAMMAR_DICTIONARY['state_code_value'] = ['"\'tx\'"',
                                          '"\'ca\'"', '"\'asd\'"', '"\'dc\'"', '"\'ga\'"']
GRAMMAR_DICTIONARY['economy_value'] = ['"\'yes\'"', '"\'no\'"']
GRAMMAR_DICTIONARY['fare_basis_code_value'] = ['"\'b\'"', '"\'bh\'"', '"\'m\'"', '"\'c\'"', '"\'qx\'"',
                                               '"\'h\'"', '"\'qw\'"', '"\'y\'"', '"\'q\'"', '"\'qo\'"', '"\'fn\'"', '"\'f\'"', '"\'yn\'"']
GRAMMAR_DICTIONARY['booking_class_value'] = [
    '"\'c\'"', '"\'b\'"', '"\'h\'"', '"\'y\'"', '"\'q\'"', '"\'f\'"', '"\'yn\'"']
GRAMMAR_DICTIONARY['meal_description_value'] = [
    '"\'lunch\'"', '"\'breakfast\'"', '"\'snack\'"', '"\'dinner\'"']
GRAMMAR_DICTIONARY['basic_type_value'] = ['"\'757\'"', '"\'747\'"',
                                          '"\'767\'"', '"\'727\'"', '"\'dc10\'"', '"\'f28\'"', '"\'737\'"']
GRAMMAR_DICTIONARY['manufacturer_value'] = ['"\'boeing\'"']
GRAMMAR_DICTIONARY['days_code_value'] = ['"\'sa\'"', '"\'su\'"']
GRAMMAR_DICTIONARY['restriction_code_value'] = [
    '"\'ap/80\'"', '"\'ap/68\'"', '"\'ap/57\'"', '"\'ap/55\'"', '"\'ap/58\'"', '"\'ap\'"']
GRAMMAR_DICTIONARY['flight_days_value'] = ['"\'daily\'"']
GRAMMAR_DICTIONARY['country_name_value'] = ['"\'canada\'"', '"\'usa\'"']
GRAMMAR_DICTIONARY['airline_name_value'] = [
    '"\'united\'"', '"\'continental airlines\'"', '"\'%canadian airlines international%\'"', '"\'%canadian airlines%\'"', '"\'%delta%\'"', '"\'usair\'"']
GRAMMAR_DICTIONARY['propulsion_value'] = ['"\'jet\'"', '"\'turboprop\'"']
GRAMMAR_DICTIONARY['airport_name_value'] = [
    '"\'general mitchell international\'"', '"\'%canadian airlines international%\'"', '"\'stapleton international\'"', '"\'%pearson%\'"', '"\'%lester%\'"', '"\'%stapleton%\'"']
GRAMMAR_DICTIONARY['discounted_value'] = ['"\'yes\'"', '"\'no\'"']

# Numerical Value
GRAMMAR_DICTIONARY['year_value'] = [
    '"1991"', '"1993"', '"1994"', '"1990"', '"1992"']
GRAMMAR_DICTIONARY['time_value'] = ['"1619"', '"815"', '"2220"', '"2010"', '"1524"', '"1205"', '"1159"', '"1220"', '"1620"', '"705"', '"2330"', '"1045"', '"1401"', '"1024"', '"400"', '"755"', '"838"', '"823"', '"1430"', '"1017"', '"930"', 
                                    '"1000"', '"2159"', '"301"', '"2134"', '"645"', '"718"', '"1310"', '"1330"', '"1425"', '"1940"', '"1923"', '"1628"', '"1745"', '"1845"','"830"','"730"','"720"', 
                                    '"555"','"500"', '"1505"', '"2226"', '"1759"', '"300"', '"1800"', '"650"', '"601"', '"600"', '"845"', '"819"', '"1200"', '"2200"', '"2400"', '"1930"', '"430"', '"530"', '"41"', 
                                    '"2230"', '"2358"', '"2359"', '"2300"', '"1900"', '"1615"', '"1530"', '"1630"', '"2000"', '"1830"', '"630"', '"2100"', '"2030"', '"1130"', '"1715"',
                                    '"1110"', '"1645"', '"800"', '"1230"', '"1730"', '"1700"', '"1030"', '"1850"', '"1500"', '"1600"', '"1400"', '"1300"', '"0"', '"200"', '"2130"', '"1115"', 
                                    '"1245"', '"1145"', '"1100"', '"900"', '"1410"', '"700"', '"100"', '"230"', '"30"', '"1"']
GRAMMAR_DICTIONARY['month_number_value'] = ['"12"', '"4"', '"6"',
                                            '"9"', '"8"', '"11"', '"10"', '"1"', '"3"', '"7"', '"5"', '"2"']
GRAMMAR_DICTIONARY['day_number_value'] = ['"26"', '"28"', '"23"', '"24"', '"27"', '"25"', '"29"', '"22"', '"21"', '"20"', '"2"',
                                          '"16"', '"11"','"13"', '"12"', '"14"', '"17"', '"15"', '"19"', '"18"', '"10"', '"1"', 
                                          '"31"', '"30"', '"3"', '"4"', '"8"', '"7"', '"5"', '"6"', '"9"']
GRAMMAR_DICTIONARY['stops_value'] = ['"0"', '"3"', '"1"']
GRAMMAR_DICTIONARY['flight_number_value'] = ['"297"', '"271"', '"2153"', '"229"', '"269"', '"270"', '"1222"', '"766"', '"505"', '"402"', '"343"', '"19"', '"417"', '"137338"', '"71"', '"324"', '"139"', '"1039"', '"771"', '"3724"', '"746"', '"217"', '"210"', '"212"', '"21"',  '"852"', '"459"',
                                             '"1291"', '"296"', '"311"', '"323"', '"1765"', '"279"', '"315"', '"497"', '"163"', '"1083"', '"1209"', '"98"', '"345"', '"928"', '"106"', '"825"', '"82"', '"4400"', '"352"', '"415"', '"3357"', '"838"', '"539"', '"281"', '"813"', '"257"', '"201"']
GRAMMAR_DICTIONARY['round_trip_cost_value'] = [
    '"466"', '"300"', '"932"', '"1288"', '"1100"', '"1500"', '"1000"', '"100"']
GRAMMAR_DICTIONARY['connections_value'] = ['"0"', '"1"']
GRAMMAR_DICTIONARY['one_direction_cost_value'] = [
    '"466"', '"400"', '"329"', '"300"', '"150"', '"200"', '"416"', '"500"']
GRAMMAR_DICTIONARY['time_elapsed_value'] = ['"60"', '"540"']

COPY_TERMINAL_SET = {'year_value', 'time_value', 'month_number_value', 'day_number_value', 'stops_value', 'flight_number_value', 'round_trip_cost_value',
                     'connections_value', 'one_direction_cost_value', 'time_elapsed_value', 'airport_code_value', 'city_name_value', 'round_trip_required_value',
                     'airline_code_value', 'day_name_value', 'aircraft_code_value', 'meal_code_value', 'state_name_value', 'class_type_value', 'transport_type_value',
                     'state_code_value', 'economy_value', 'fare_basis_code_value', 'booking_class_value', 'meal_description_value', 'basic_type_value', 'manufacturer_value',
                     'days_code_value', 'restriction_code_value', 'flight_days_value', 'country_name_value', 'airline_name_value', 'propulsion_value', 'airport_name_value',
                     'discounted_value'}
