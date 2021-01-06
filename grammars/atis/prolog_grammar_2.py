# coding=utf8

"""
Prolog Grammar of ATIS
"""

GRAMMAR_DICTIONARY = {}

ROOT_RULE = 'statement -> [answer]'

GRAMMAR_DICTIONARY['statement'] = ['(answer ws)']

GRAMMAR_DICTIONARY['answer'] = [
    '("answer_1(" var "," Form ")")',
    '("answer_2(" var "," var "," Form ")")',
    '("answer_3(" var "," var "," var "," Form ")")',
    '("answer_4(" var "," var "," var "," var "," Form ")")',
]

GRAMMAR_DICTIONARY['Form'] = [
    '("(" Form conjunction ")")',
    '("or(" Form conjunction ")")',
    '("not(" Form conjunction ")")',
    '("is_flight(" var ")")',
    '("is_oneway(" var ")")',
    '("is_round_trip(" var ")")',
    '("is_daily_flight(" var ")")',
    '("is_flight_has_stop(" var ")")',
    '("is_non_stop_flight(" var ")")',
    '("is_flight_economy(" var ")")',
    '("is_flight_has_meal(" var ")")',
    '("is_economy(" var ")")',
    '("is_discounted_flight(" var ")")',
    '("is_flight_overnight(" var ")")',
    '("is_connecting_flight(" var ")")',
    '("is_meal(" var ")")',
    '("is_meal_code(" var ")")',
    '("is_airline(" var ")")',
    '("is_rapid_transit(" var ")")',
    '("is_taxi(" var ")")',
    '("is_air_taxi_operation(" var ")")',
    '("is_ground_transport_on_weekday(" var ")")',
    '("is_ground_transport(" var ")")',
    '("is_limousine(" var ")")',
    '("is_rental_car(" var ")")',
    '("is_flight_turboprop(" var ")")',
    '("is_turboprop(" var ")")',
    '("aircraft_code(" var ")")',
    '("is_aircraft(" var ")")',
    '("is_flight_jet(" var ")")',
    '("is_day_after_tomorrow_flight(" var ")")',
    '("is_flight_tonight(" var ")")',
    '("is_today_flight(" var ")")',
    '("is_tomorrow_flight(" var ")")',
    '("is_flight_on_weekday(" var ")")',
    '("is_tomorrow_arrival_flight(" var ")")',
    '("is_time_zone_code(" var ")")',
    '("is_class_of_service(" var ")")',
    '("is_city(" var ")")',
    '("is_airport(" var ")")',
    '("is_fare_basis_code(" var ")")',
    '("is_booking_class_t(" var ")")',
    '("_named(" var "," var ")")',
    '("is_flight_has_specific_fare_basis_code(" var "," var ")")',
    '("is_flight_has_booking_class(" var "," var ")")',
    '("is_flight_stop_at_city(" var "," var ")")',
    '("is_flight_on_year(" var "," var ")")',
    '("is_flight_during_day(" var "," var ")")',
    '("is_flight_stops_specify_number_of_times(" var "," var ")")',
    '("is_flight_meal_code(" var "," var ")")',
    '("is_from(" var "," var ")")',
    '("is_flight_day_return(" var "," var ")")',
    '("is_flight_day_number_return(" var "," var ")")',
    '("is_flight_departure_time(" var "," var ")")',
    '("is_flight_month_return(" var "," var ")")',
    '("is_flight_month_arrival(" var "," var ")")',
    '("is_flight_approx_return_time(" var "," var ")")',
    '("is_flight_before_day(" var "," var ")")',
    '("is_flight_approx_arrival_time(" var "," var ")")',
    '("is_flight_day_number_arrival(" var "," var ")")',
    '("is_flight_arrival_time(" var "," var ")")',
    '("is_flight_with_specific_aircraft(" var "," var ")")',
    '("is_flight_on_day_number(" var "," var ")")',
    '("is_flight_on_day(" var "," var ")")',
    '("is_flight_manufacturer(" var "," var ")")',
    '("is_flight_aircraft(" var "," var ")")',
    '("is_flight_stop_at_airport(" var "," var ")")',
    '("is_flight_during_day_arrival(" var "," var ")")',
    '("is_flight_days_from_today(" var "," var ")")',
    '("is_fare_basis_code_class_type(" var "," var ")")',
    '("is_flight_after_day(" var "," var ")")',
    '("is_flight_day_arrival(" var "," var ")")',
    '("is_flight_approx_departure_time(" var "," var ")")',
    '("is_flight_has_specific_meal(" var "," var ")")',
    '("is_next_days_flight(" var "," var ")")',
    '("is_flight_has_class_type(" var "," var ")")',
    '("is_to(" var "," var ")")',
    '("is_flight_airline(" var "," var ")")',
    '("p_flight_fare(" var "," var ")")',
    '("is_flight_number(" var "," var ")")',
    '("is_airport_of_city(" var "," var ")")',
    '("is_airline_services(" var "," var ")")',
    '("is_services(" var "," var ")")',
    '("is_from_airports_of_city(" var "," var ")")',
    '("is_from_airport(" var "," var ")")',
    '("is_to_city(" var "," var ")")',
    '("is_loc_t_state(" var "," var ")")',
    '("is_mf(" var "," var ")")',
    '("is_loc_t(" var "," var ")")',
    '("is_aircraft_basis_type(" var "," var ")")',
    '("is_aircraft_airline(" var "," var ")")',
    '("is_flight_cost_fare(" var "," var ")")',
    '("is_loc_t_city_time_zone(" var "," var ")")',
    '("is_airline_provide_meal(" var "," var ")")',
    '("is_airline_has_booking_class(" var "," var ")")',
    '("minimum_connection_time(" var "," var ")")',
    '("p_flight_stop_arrival_time(" var "," var ")")',
    '("p_ground_fare(" var "," var ")")',
    '("p_booking_class_fare(" var "," var ")")',
    '("airline_name(" var "," var ")")',
    '("abbrev(" var "," var ")")',
    '("capacity(" var "," var ")")',
    '("minutes_distant(" var "," var ")")',
    '("is_time_elapsed(" var "," var ")")',
    '("p_flight_restriction_code(" var "," var ")")',
    '("equals(" var "," var ")")',
    '("equals_arrival_time(" var "," var ")")',
    '("larger_than_arrival_time(" var "," var ")")',
    '("larger_than_capacity(" var "," var ")")',
    '("larger_than_departure_time(" var "," var ")")',
    '("larger_than_number_of_stops(" var "," var ")")',
    '("less_than_flight_cost(" var "," var ")")',
    '("less_than_departure_time(" var "," var ")")',
    '("less_than_flight_fare(" var "," var ")")',
    '("less_than_arrival_time(" var "," var ")")',
    '("count(" var "," Form "," var ")")',
    '("argmax_capacity(" var "," Form ")")',
    '("argmax_arrival_time(" var "," Form ")")',
    '("argmax_departure_time(" var "," Form ")")',
    '("argmax_get_number_of_stops(" var "," Form ")")',
    '("argmax_get_flight_fare(" var "," Form ")")',
    '("argmax_count(" var "," Form ")")',
    '("argmin_time_elapsed(" var "," Form ")")',
    '("argmin_get_number_of_stops(" var "," Form ")")',
    '("argmin_time_elapsed(" var "," Form ")")',
    '("argmin_arrival_time(" var "," Form ")")',
    '("argmin_capacity(" var "," Form ")")',
    '("argmin_departure_time(" var "," Form ")")',
    '("argmin_get_flight_fare(" var "," Form ")")',
    '("argmin_miles_distant(" var "," Form ")")',
    '("_max(" var "," Form ")")',
    '("_min(" var "," Form ")")',
    '("sum_capacity(" var "," Form "," var  ")")',
    '("sum_get_number_of_stops(" var "," Form "," var  ")")',
    '("miles_distant_between_city(" var "," var "," var ")")',
    '("miles_distant(" var "," var "," var ")")',
    '("const(" var "," fare_basis_code ")")',
    '("const(" var "," meal_code ")")',
    '("const(" var "," airport_code ")")',
    '("const(" var "," airline_code ")")',
    '("const(" var "," aircraft_code_object ")")',
    '("const(" var "," city_name ")")',
    '("const(" var "," time ")")',
    '("const(" var "," flight_number_object ")")',
    '("const(" var "," class_description ")")',
    '("const(" var "," day_period ")")',
    '("const(" var "," state_name ")")',
    '("const(" var "," day_number ")")',
    '("const(" var "," month ")")',
    '("const(" var "," day ")")',
    '("const(" var "," dollar ")")',
    '("const(" var "," meal_description ")")',
    '("const(" var "," "hour(9)" ")")',
    '("const(" var "," integer ")")',
    '("const(" var "," basis_type ")")',
    '("const(" var "," year ")")',
    '("const(" var "," "days_code(sa)" ")")',
    '("const(" var "," "manufacturer(boeing)" ")")'
]
GRAMMAR_DICTIONARY['conjunction'] = [
    '("," Form conjunction)',
    '""'
]

# Variable
GRAMMAR_DICTIONARY['var'] = ['"%s"' % chr(97+i) for i in range(26)]

GRAMMAR_DICTIONARY['fare_basis_code'] = ['("fare_basis_code(" fare_basis_code_value ")")']
GRAMMAR_DICTIONARY['fare_basis_code_value'] = ['"qx"', '"qw"', '"qo"', '"fn"', '"yn"', '"bh"', '"k"', '"b"', '"h"', '"f"', '"q"', '"c"', '"y"', '"m"',]
GRAMMAR_DICTIONARY['meal_code'] = ['("meal_code(" meal_code_value ")")']
GRAMMAR_DICTIONARY['meal_code_value'] = ['"ap_58"', '"ap_57"', '"d_s"', '"b"', '"ap_55"', '"s_"', '"sd_d"', '"ls"', '"ap_68"', '"ap_80"', '"ap"', '"s"', ]
GRAMMAR_DICTIONARY['airline_code'] = ['("airline_code(" airline_code_value ")")']
GRAMMAR_DICTIONARY['airline_code_value'] = ['"usair"', '"co"', '"ua"', '"delta"', '"as"', '"ff"', '"canadian_airlines_international"', '"us"', '"nx"', '"hp"', '"aa"', '"kw"', '"ml"', '"nw"', '"ac"', '"tw"', '"yx"', '"ea"', '"dl"', '"wn"', '"lh"', '"cp"']
GRAMMAR_DICTIONARY['airport_code'] = ['("airport_code(" airport_code_value ")")']
GRAMMAR_DICTIONARY['airport_code_value'] = ['"dallas"', '"ont"', '"stapelton"', '"bna"', '"bwi"', '"iad"', '"sfo"', '"phl"', '"pit"', '"slc"', '"phx"', '"lax"', '"bur"', '"ind"', '"iah"', '"dtw"', '"las"', '"dal"', '"den"', '"atl"', '"ewr"', '"bos"', '"tpa"', '"jfk"', '"mke"', '"oak"', '"yyz"', '"dfw"', '"cvg"', '"hou"', '"lga"', '"ord"', '"mia"', '"mco"']
GRAMMAR_DICTIONARY['aircraft_code_object'] = ['("aircraft_code(" aircraft_code_value ")")']
GRAMMAR_DICTIONARY['aircraft_code_value'] = ['"m80"', '"dc10"', '"727"', '"d9s"', '"f28"', '"j31"', '"767"', '"734"', '"73s"', '"747"', '"737"', '"733"', '"d10"', '"100"', '"757"', '"72s"']
GRAMMAR_DICTIONARY['city_name'] = ['("city_name(" city_name_value ")")']
GRAMMAR_DICTIONARY['city_name_value'] = ['"cleveland"', '"milwaukee"', '"detroit"', '"los_angeles"', '"miami"', '"salt_lake_city"', '"ontario"', '"tacoma"', '"memphis"', '"denver"', '"san_francisco"', '"new_york"', '"tampa"', '"washington"', '"westchester_county"', '"boston"', '"newark"', '"pittsburgh"', '"charlotte"', '"columbus"', '"atlanta"', '"oakland"', '"kansas_city"', '"st_louis"', '"nashville"', '"chicago"', '"fort_worth"', '"san_jose"', '"dallas"', '"philadelphia"', '"st_petersburg"', '"baltimore"', '"san_diego"', '"cincinnati"', '"long_beach"', '"phoenix"', '"indianapolis"', '"burbank"', '"montreal"', '"seattle"', '"st_paul"', '"minneapolis"', '"houston"', '"orlando"', '"toronto"', '"las_vegas"']
GRAMMAR_DICTIONARY['time'] = ['("time(" time_value ")")']
GRAMMAR_DICTIONARY['time_value'] = [
    '"1850"', '"1110"', '"2000"', '"1815"', '"1024"', '"1500"',
    '"1900"', '"1600"', '"1300"', '"1800"', '"1200"', '"1628"',
    '"1830"', '"823"', '"1245"', '"1524"', '"200"', '"1615"',
    '"1230"', '"705"', '"1045"', '"1700"', '"1115"', '"1645"',
    '"1730"', '"815"', '"0"', '"500"', '"1205"', '"1940"',
    '"1400"', '"1130"', '"2200"', '"645"', '"718"', '"2220"',
    '"600"', '"630"', '"800"', '"838"', '"1330"', '"845"', '"1630"',
    '"1715"', '"2010"', '"1000"', '"1619"', '"2100"', '"1505"',
    '"2400"', '"1923"', '"100"',  '"1145"', '"2300"', '"1620"',
    '"2023"', '"2358"',  '"1425"', '"720"', '"1310"', '"700"', '"650"',
    '"1410"', '"1030"', '"1900"', '"1017"', '"1430"', '"900"', '"1930"',
    '"1133"', '"1220"', '"2226"', '"1100"', '"819"', '"755"', '"2134"', '"555"', '"1"',
]
GRAMMAR_DICTIONARY['flight_number_object'] = ['("flight_number(" flight_number_value ")")']
GRAMMAR_DICTIONARY['flight_number_value'] = [
    '"1291"', '"345"', '"813"', '"71"', '"1059"', '"212"', '"1209"',
    '"281"', '"201"', '"324"', '"19"', '"352"', '"137338"', '"4400"',
    '"323"', '"505"', '"825"', '"82"', '"279"', '"1055"', '"296"', '"315"',
    '"1765"', '"405"', '"771"', '"106"', '"2153"', '"257"', '"402"',
    '"343"', '"98"', '"1039"', '"217"', '"539"', '"459"', '"417"',
    '"1083"', '"3357"', '"311"', '"210"', '"139"', '"852"', '"838"',
    '"415"', '"3724"', '"21"', '"928"', '"269"', '"270"',
    '"297"', '"746"', '"1222"', '"271"'
]
GRAMMAR_DICTIONARY['class_description'] = ['("class_description(" class_description_value ")")']
GRAMMAR_DICTIONARY['class_description_value'] = ['"thrift"', '"coach"', '"first"', '"business"']
GRAMMAR_DICTIONARY['day_period'] = ['("day_period(" day_period_value ")")']
GRAMMAR_DICTIONARY['day_period_value'] = ['"early"', '"afternoon"', '"late_evening"', '"late_night"', '"mealtime"', '"evening"', '"pm"', '"daytime"', '"breakfast"', '"morning"', '"late"']
GRAMMAR_DICTIONARY['state_name'] = ['("state_name(" state_name_value ")")']
GRAMMAR_DICTIONARY['state_name_value'] = ['"minnesota"', '"florida"', '"arizona"', '"nevada"', '"california"']
GRAMMAR_DICTIONARY['day_number'] = ['("day_number(" day_number_value ")")']
GRAMMAR_DICTIONARY['day_number_value'] = ['"13"', '"29"', '"28"', '"22"', '"21"', '"16"', '"30"', '"12"', '"18"', '"19"', '"31"', '"20"', '"27"', '"6"', '"26"', '"17"', '"11"', '"10"', '"15"', '"23"', '"24"', '"25"', '"14"', '"1"',  '"3"',  '"8"', '"5"', '"2"', '"9"', '"4"', '"7"']
GRAMMAR_DICTIONARY['month'] = ['("month(" month_value ")")']
GRAMMAR_DICTIONARY['month_value'] = ['"april"', '"august"', '"may"', '"october"', '"june"', '"november"', '"september"', '"february"', '"december"', '"march"', '"july"', '"january"']
GRAMMAR_DICTIONARY['day'] = ['("day(" day_value ")")']
GRAMMAR_DICTIONARY['day_value'] = ['"monday"', '"wednesday"', '"thursday"', '"tuesday"', '"saturday"', '"friday"', '"sunday"']
GRAMMAR_DICTIONARY['dollar'] = ['("dollar(" dollar_value ")")']
GRAMMAR_DICTIONARY['dollar_value'] = ['"1000"', '"1500"', '"466"', '"1288"', '"300"', '"329"', '"416"', '"124"', '"932"', '"1100"', '"200"', '"500"', '"100"', '"415"', '"150"', '"400"']
GRAMMAR_DICTIONARY['meal_description'] = ['("meal_description(" meal_description_value ")")']
GRAMMAR_DICTIONARY['meal_description_value'] = ['"snack"', '"breakfast"', '"lunch"', '"dinner"']
GRAMMAR_DICTIONARY['integer'] = ['("integer(" integer_value ")")']
GRAMMAR_DICTIONARY['integer_value'] = ['"2"', '"1"', '"3"']
GRAMMAR_DICTIONARY['basis_type'] = ['("basis_type(" basis_type_value ")")']
GRAMMAR_DICTIONARY['basis_type_value'] = ['"737"', '"767"']
GRAMMAR_DICTIONARY['year'] = ['("year(" year_value ")")']
GRAMMAR_DICTIONARY['year_value'] = ['"1991"', '"1993"', '"1992"']

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY["wsp"] = ['~"\s+"i']

COPY_TERMINAL_SET = {
    'fare_basis_code_value', 'meal_code_value', 'airport_code_value', 'airline_code_value',
    'aircraft_code_value', 'city_name_value', 'time_value', 'flight_number_value',
    'class_description', 'day_period_value', 'state_name_value',
    'day_number_value', 'month_value', 'day_value', 'dollar_value', 'meal_description_value',
    'integer_value', 'basis_type_value', 'year_value',
}