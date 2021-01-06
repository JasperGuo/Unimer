# coding=utf8

"""
Prolog Grammar of ATIS
"""

GRAMMAR_DICTIONARY = {}

ROOT_RULE = 'statement -> [answer]'

GRAMMAR_DICTIONARY['statement'] = ['(answer ws)']

GRAMMAR_DICTIONARY['answer'] = [
    '("answer_1(" var "," goal ")")',
    '("answer_2(" var "," var "," goal ")")',
    '("answer_3(" var "," var "," var "," goal ")")',
    '("answer_4(" var "," var "," var "," var "," goal ")")',
]

# Goal
GRAMMAR_DICTIONARY['goal'] = [
    '(declaration)',
    '(unit_relation)',
    '(binary_relation)',
    '(triplet_relation)',
    '(meta)',
    '("(" goal conjunction ")")',
    '("or(" goal conjunction ")")',
    '("not(" goal conjunction ")")'
]
GRAMMAR_DICTIONARY['conjunction'] = [
    '("," goal conjunction)',
    '""'
]

# Variable
GRAMMAR_DICTIONARY['var'] = ['"%s"' % chr(97+i) for i in range(26)]

# Declaration
GRAMMAR_DICTIONARY['declaration'] = [
    '("const(" var "," object ")")']

# Object
GRAMMAR_DICTIONARY['object'] = [
    '(fare_basis_code)', '(meal_code)', '(airport_code)', '(airline_code)',
    '(aircraft_code_object)', '(city_name)', '(time)', '(flight_number_object)',
    '(class_description)', '(day_period)', '(state_name)',
    '(day_number)', '(month)', '(day)', '(dollar)', '(meal_description)',
    '("hour(9)")', '(integer)', '(basis_type)', '(year)',
    '("days_code(sa)")', '("manufacturer(boeing)")'
]
GRAMMAR_DICTIONARY['fare_basis_code'] = ['("fare_basis_code(" fare_basis_code_value ")")']
GRAMMAR_DICTIONARY['fare_basis_code_value'] = ['"_qx"', '"_qw"', '"_qo"', '"_fn"', '"_yn"', '"_bh"', '"_k"', '"_b"', '"_h"', '"_f"', '"_q"', '"_c"', '"_y"', '"_m"',]
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

# Unit Relation
GRAMMAR_DICTIONARY['unit_relation'] = [
    # Flight
    '(is_flight)', '(is_oneway)', '(is_round_trip)', '(is_daily_flight)',
    '(is_flight_has_stop)', '(is_non_stop_flight)', '(is_flight_economy)',
    '(is_flight_has_meal)', '(is_economy)', '(is_discounted_flight)',
    '(is_flight_overnight)', '(is_connecting_flight)',
    # Meal
    '(is_meal)', '(is_meal_code)',
    # Airline
    '(is_airline)',
    # Transport way
    '(is_rapid_transit)', '(is_taxi)', '(is_air_taxi_operation)', '(is_ground_transport_on_weekday)',
    '(is_ground_transport)', '(is_limousine)', '(is_rental_car)',
    # Aircraft
    '(is_flight_turboprop)', '(is_turboprop)', '(aircraft_code)', '(is_aircraft)', '(is_flight_jet)',
    # Time
    '(is_day_after_tomorrow_flight)', '(is_flight_tonight)', '(is_today_flight)',
    '(is_tomorrow_flight)', '(is_flight_on_weekday)', '(is_tomorrow_arrival_flight)',
    # Other
    '(is_time_zone_code)', '(is_class_of_service)', '(is_city)',
    '(is_airport)', '(is_fare_basis_code)', '(is_booking_class_t)',
]
GRAMMAR_DICTIONARY['is_discounted_flight'] = ['("is_discounted_flight(" var ")")']
GRAMMAR_DICTIONARY['is_taxi'] = ['("is_taxi(" var ")")']
GRAMMAR_DICTIONARY['is_economy'] = ['("is_economy(" var ")")']
GRAMMAR_DICTIONARY['is_flight_on_weekday'] = ['("is_flight_on_weekday(" var ")")']
GRAMMAR_DICTIONARY['is_time_zone_code'] = ['("is_time_zone_code(" var ")")']
GRAMMAR_DICTIONARY['is_air_taxi_operation'] = ['("is_air_taxi_operation(" var ")")']
GRAMMAR_DICTIONARY['is_fare_basis_code'] = ['("is_fare_basis_code(" var ")")']
GRAMMAR_DICTIONARY['is_meal_code'] = ['("is_meal_code(" var ")")']
GRAMMAR_DICTIONARY['is_limousine'] = ['("is_limousine(" var ")")']
GRAMMAR_DICTIONARY['is_flight_tonight'] = ['("is_flight_tonight(" var ")")']
GRAMMAR_DICTIONARY['is_tomorrow_arrival_flight'] = ['("is_tomorrow_arrival_flight(" var ")")']
GRAMMAR_DICTIONARY['is_tomorrow_flight'] = ['("is_tomorrow_flight(" var ")")']
GRAMMAR_DICTIONARY['is_daily_flight'] = ['("is_daily_flight(" var ")")']
GRAMMAR_DICTIONARY['_minutes_distant'] = ['("_minutes_distant(" var ")")']
GRAMMAR_DICTIONARY['is_flight'] = ['("is_flight(" var ")")']
GRAMMAR_DICTIONARY['is_city'] = ['("is_city(" var ")")']
GRAMMAR_DICTIONARY['is_booking_class_t'] = ['("is_booking_class_t(" var ")")']
GRAMMAR_DICTIONARY['is_rapid_transit'] = ['("is_rapid_transit(" var ")")']
GRAMMAR_DICTIONARY['is_oneway'] = ['("is_oneway(" var ")")']
GRAMMAR_DICTIONARY['is_airport'] = ['("is_airport(" var ")")']
GRAMMAR_DICTIONARY['is_flight_has_stop'] = ['("is_flight_has_stop(" var ")")']
GRAMMAR_DICTIONARY['aircraft_code'] = ['("aircraft_code(" var ")")']
GRAMMAR_DICTIONARY['is_day_after_tomorrow_flight'] = ['("is_day_after_tomorrow_flight(" var ")")']
GRAMMAR_DICTIONARY['is_airline'] = ['("is_airline(" var ")")']
GRAMMAR_DICTIONARY['is_flight_economy'] = ['("is_flight_economy(" var ")")']
GRAMMAR_DICTIONARY['is_class_of_service'] = ['("is_class_of_service(" var ")")']
GRAMMAR_DICTIONARY['is_aircraft'] = ['("is_aircraft(" var ")")']
GRAMMAR_DICTIONARY['is_today_flight'] = ['("is_today_flight(" var ")")']
GRAMMAR_DICTIONARY['is_flight_has_meal'] = ['("is_flight_has_meal(" var ")")']
GRAMMAR_DICTIONARY['is_ground_transport'] = ['("is_ground_transport(" var ")")']
GRAMMAR_DICTIONARY['is_non_stop_flight'] = ['("is_non_stop_flight(" var ")")']
GRAMMAR_DICTIONARY['is_flight_turboprop'] = ['("is_flight_turboprop(" var ")")']
GRAMMAR_DICTIONARY['is_meal'] = ['("is_meal(" var ")")']
GRAMMAR_DICTIONARY['is_round_trip'] = ['("is_round_trip(" var ")")']
GRAMMAR_DICTIONARY['is_ground_transport_on_weekday'] = ['("is_ground_transport_on_weekday(" var ")")']
GRAMMAR_DICTIONARY['is_turboprop'] = ['("is_turboprop(" var ")")']
GRAMMAR_DICTIONARY['is_rental_car'] = ['("is_rental_car(" var ")")']
GRAMMAR_DICTIONARY['is_connecting_flight'] = ['("is_connecting_flight(" var ")")']
GRAMMAR_DICTIONARY['is_flight_jet'] = ['("is_flight_jet(" var ")")']
GRAMMAR_DICTIONARY['is_flight_overnight'] = ['("is_flight_overnight(" var ")")']


# Binary Predicate
GRAMMAR_DICTIONARY['binary_relation'] = [
    # General
    '(_named)',
    # Flight property
    '(is_flight_has_specific_fare_basis_code)', '(is_flight_has_booking_class)',
    '(is_flight_stop_at_city)', '(is_flight_on_year)', '(is_flight_during_day)',
    '(is_flight_stops_specify_number_of_times)', '(is_flight_meal_code)',
    '(is_from)', '(is_flight_day_return)', '(is_flight_day_number_return)',
    '(is_flight_departure_time)', '(is_flight_month_return)',
    '(is_flight_month_arrival)', '(is_flight_approx_return_time)',
    '(is_flight_before_day)', '(is_flight_approx_arrival_time)',
    '(is_flight_day_number_arrival)',
    '(is_flight_arrival_time)', '(is_flight_with_specific_aircraft)',
    '(is_flight_on_day_number)', '(is_flight_on_day)', '(is_flight_manufacturer)',
    '(is_flight_aircraft)', '(is_flight_stop_at_airport)',
    '(is_flight_during_day_arrival)', '(is_flight_days_from_today)',
    '(is_fare_basis_code_class_type)', '(is_flight_after_day)',
    '(is_flight_day_arrival)', '(is_flight_approx_departure_time)',
    '(is_flight_has_specific_meal)', '(is_next_days_flight)',
    '(is_flight_has_class_type)', '(is_to)', '(is_flight_airline)',
    '(p_flight_fare)', '(is_flight_number)',
    # Airport
    '(is_airport_of_city)', '(is_airline_services)', '(is_services)', '(is_from_airports_of_city)',
    # Ground Transport
    '(is_from_airport)', '(is_to_city)', '(is_loc_t_state)',
    # Aircraft
    '(is_mf)', '(is_loc_t)', '(is_aircraft_basis_type)', '(is_aircraft_airline)',
    # Other
    '(is_flight_cost_fare)',
    '(is_loc_t_city_time_zone)',
    '(is_airline_provide_meal)',
    '(is_airline_has_booking_class)',
    # Entity
    '(minimum_connection_time)', '(p_flight_stop_arrival_time)',
    '(p_ground_fare)', '(p_booking_class_fare)',
    '(airline_name)', '(abbrev)', '(capacity)', '(minutes_distant)', '(is_time_elapsed)',
    '(p_flight_restriction_code)'
]
GRAMMAR_DICTIONARY['airline_name'] = ['("airline_name(" var "," var ")")']
GRAMMAR_DICTIONARY['_named'] = ['("_named(" var "," var ")")']
GRAMMAR_DICTIONARY['is_time_elapsed'] = ['("is_time_elapsed(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_has_specific_fare_basis_code'] = ['("is_flight_has_specific_fare_basis_code(" var "," var ")")']
GRAMMAR_DICTIONARY['abbrev'] = ['("abbrev(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_during_day'] = ['("is_flight_during_day(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_has_booking_class'] = ['("is_flight_has_booking_class(" var "," var ")")']
GRAMMAR_DICTIONARY['is_airline_has_booking_class'] = ['("is_airline_has_booking_class(" var "," var ")")']
GRAMMAR_DICTIONARY['capacity'] = ['("capacity(" var "," var ")")']
GRAMMAR_DICTIONARY['get_flight_airline_code'] = ['("get_flight_airline_code(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_stop_at_city'] = ['("is_flight_stop_at_city(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_on_year'] = ['("is_flight_on_year(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_stops_specify_number_of_times'] = ['("is_flight_stops_specify_number_of_times(" var "," var ")")']
GRAMMAR_DICTIONARY['is_from_airport'] = ['("is_from_airport(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_meal_code'] = ['("is_flight_meal_code(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_airline_code'] = ['("p_flight_airline_code(" var "," var ")")']
GRAMMAR_DICTIONARY['is_from'] = ['("is_from(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_day_return'] = ['("is_flight_day_return(" var "," var ")")']
GRAMMAR_DICTIONARY['get_flight_fare'] = ['("get_flight_fare(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_day_number_return'] = ['("is_flight_day_number_return(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_departure_time'] = ['("is_flight_departure_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_month_return'] = ['("is_flight_month_return(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_month_arrival'] = ['("is_flight_month_arrival(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_number'] = ['("is_flight_number(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_cost_fare'] = ['("is_flight_cost_fare(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_approx_return_time'] = ['("is_flight_approx_return_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_before_day'] = ['("is_flight_before_day(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_approx_arrival_time'] = ['("is_flight_approx_arrival_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_airport_of_city'] = ['("is_airport_of_city(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_day_number_arrival'] = ['("is_flight_day_number_arrival(" var "," var ")")']
GRAMMAR_DICTIONARY['is_airline_services'] = ['("is_airline_services(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_airline'] = ['("is_flight_airline(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_arrival_time'] = ['("is_flight_arrival_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_with_specific_aircraft'] = ['("is_flight_with_specific_aircraft(" var "," var ")")']
GRAMMAR_DICTIONARY['is_mf'] = ['("is_mf(" var "," var ")")']
GRAMMAR_DICTIONARY['get_flight_aircraft_code'] = ['("get_flight_aircraft_code(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_on_day_number'] = ['("is_flight_on_day_number(" var "," var ")")']
GRAMMAR_DICTIONARY['is_loc_t'] = ['("is_loc_t(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_on_day'] = ['("is_flight_on_day(" var "," var ")")']
GRAMMAR_DICTIONARY['get_flight_restriction_code'] = ['("get_flight_restriction_code(" var "," var ")")']
GRAMMAR_DICTIONARY['is_to_city'] = ['("is_to_city(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_manufacturer'] = ['("is_flight_manufacturer(" var "," var ")")']
GRAMMAR_DICTIONARY['minutes_distant'] = ['("minutes_distant(" var "," var ")")']
GRAMMAR_DICTIONARY['is_services'] = ['("is_services(" var "," var ")")']
GRAMMAR_DICTIONARY['p_booking_class_fare'] = ['("p_booking_class_fare(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_aircraft_code'] = ['("p_flight_aircraft_code(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_restriction_code'] = ['("p_flight_restriction_code(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_aircraft'] = ['("is_flight_aircraft(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_stop_at_airport'] = ['("is_flight_stop_at_airport(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_during_day_arrival'] = ['("is_flight_during_day_arrival(" var "," var ")")']
GRAMMAR_DICTIONARY['departure_time'] = ['("departure_time(" var "," var ")")']
GRAMMAR_DICTIONARY['arrival_time'] = ['("arrival_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_fare_basis_code_class_type'] = ['("is_fare_basis_code_class_type(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_after_day'] = ['("is_flight_after_day(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_booking_class'] = ['("p_flight_booking_class(" var "," var ")")']
GRAMMAR_DICTIONARY['get_number_of_stops'] = ['("get_number_of_stops(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_days_from_today'] = ['("is_flight_days_from_today(" var "," var ")")']
GRAMMAR_DICTIONARY['minimum_connection_time'] = ['("minimum_connection_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_aircraft_basis_type'] = ['("is_aircraft_basis_type(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_day_arrival'] = ['("is_flight_day_arrival(" var "," var ")")']
GRAMMAR_DICTIONARY['is_loc_t_state'] = ['("is_loc_t_state(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_approx_departure_time'] = ['("is_flight_approx_departure_time(" var "," var ")")']
GRAMMAR_DICTIONARY['is_from_airports_of_city'] = ['("is_from_airports_of_city(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_has_specific_meal'] = ['("is_flight_has_specific_meal(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_fare'] = ['("p_flight_fare(" var "," var ")")']
GRAMMAR_DICTIONARY['is_next_days_flight'] = ['("is_next_days_flight(" var "," var ")")']
GRAMMAR_DICTIONARY['is_flight_has_class_type'] = ['("is_flight_has_class_type(" var "," var ")")']
GRAMMAR_DICTIONARY['time_elapsed'] = ['("time_elapsed(" var "," var ")")']
GRAMMAR_DICTIONARY['is_to'] = ['("is_to(" var "," var ")")']
GRAMMAR_DICTIONARY['is_loc_t_city_time_zone'] = ['("is_loc_t_city_time_zone(" var "," var ")")']
GRAMMAR_DICTIONARY['is_aircraft_airline'] = ['("is_aircraft_airline(" var "," var ")")']
GRAMMAR_DICTIONARY['p_ground_fare'] = ['("p_ground_fare(" var "," var ")")']
GRAMMAR_DICTIONARY['is_airline_provide_meal'] = ['("is_airline_provide_meal(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_meal'] = ['("p_flight_meal(" var "," var ")")']
GRAMMAR_DICTIONARY['p_flight_stop_arrival_time'] = ['("p_flight_stop_arrival_time(" var "," var ")")']

# Triplet Relations
GRAMMAR_DICTIONARY['triplet_relation'] = ['(miles_distant_between_city)', '(miles_distant)']
GRAMMAR_DICTIONARY['miles_distant_between_city'] = ['("miles_distant_between_city(" var "," var "," var ")")']
GRAMMAR_DICTIONARY['miles_distant'] = ['("miles_distant(" var "," var "," var ")")']

# Meta Predicates
GRAMMAR_DICTIONARY['meta'] = [
    '(equals)', '(equals_arrival_time)',
    '(larger_than_arrival_time)', '(larger_than_capacity)', '(larger_than_departure_time)',
    '(larger_than_number_of_stops)', '(less_than_flight_cost)', '(less_than_departure_time)',
    '(less_than_flight_fare)', '(less_than_arrival_time)', '(count)', '(argmax_capacity)',
    '(argmax_arrival_time)', '(argmax_departure_time)', '(argmax_get_number_of_stops)',
    '(argmax_get_flight_fare)', '(argmax_count)', '(argmin_time_elapsed)',
    '(argmin_get_number_of_stops)', '(argmin_time_elapsed)', '(argmin_arrival_time)',
    '(argmin_capacity)', '(argmin_departure_time)', '(argmin_get_flight_fare)',
    '(argmin_miles_distant)', '(max)', '(min)', '(sum_capacity)', '(sum_get_number_of_stops)'
]
GRAMMAR_DICTIONARY['equals'] = ['("equals(" var "," var ")")']
GRAMMAR_DICTIONARY['equals_arrival_time'] = ['("equals_arrival_time(" var "," var ")")']
GRAMMAR_DICTIONARY['larger_than_arrival_time'] = ['("larger_than_arrival_time(" var "," var ")")']
GRAMMAR_DICTIONARY['larger_than_capacity'] = ['("larger_than_capacity(" var "," var ")")']
GRAMMAR_DICTIONARY['larger_than_departure_time'] = ['("larger_than_departure_time(" var "," var ")")']
GRAMMAR_DICTIONARY['larger_than_number_of_stops'] = ['("larger_than_number_of_stops(" var "," var ")")']
GRAMMAR_DICTIONARY['less_than_flight_cost'] = ['("less_than_flight_cost(" var "," var ")")']
GRAMMAR_DICTIONARY['less_than_departure_time'] = ['("less_than_departure_time(" var "," var ")")']
GRAMMAR_DICTIONARY['less_than_flight_fare'] = ['("less_than_flight_fare(" var "," var ")")']
GRAMMAR_DICTIONARY['less_than_arrival_time'] = ['("less_than_arrival_time(" var "," var ")")']
GRAMMAR_DICTIONARY['count'] = ['("count(" var "," goal "," var ")")']
GRAMMAR_DICTIONARY['max'] = ['("_max(" var "," goal ")")']
GRAMMAR_DICTIONARY['min'] = ['("_min(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmax_capacity'] = ['("argmax_capacity(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmax_arrival_time'] = ['("argmax_arrival_time(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmax_departure_time'] = ['("argmax_departure_time(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmax_get_number_of_stops'] = ['("argmax_get_number_of_stops(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmax_get_flight_fare'] = ['("argmax_get_flight_fare(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmax_count'] = ['("argmax_count(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_arrival_time'] = ['("argmin_arrival_time(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_capacity'] = ['("argmin_capacity(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_departure_time'] = ['("argmin_departure_time(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_get_number_of_stops'] = ['("argmin_get_number_of_stops(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_get_flight_fare'] = ['("argmin_get_flight_fare(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_miles_distant'] = ['("argmin_miles_distant(" var "," goal ")")']
GRAMMAR_DICTIONARY['argmin_time_elapsed'] = ['("argmin_time_elapsed(" var "," goal ")")']
GRAMMAR_DICTIONARY['sum_capacity'] = ['("sum_capacity(" var "," goal "," var  ")")']
GRAMMAR_DICTIONARY['sum_get_number_of_stops'] = ['("sum_get_number_of_stops(" var "," goal "," var  ")")']

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY["wsp"] = ['~"\s+"i']

COPY_TERMINAL_SET = {
    'fare_basis_code_value', 'meal_code_value', 'airport_code_value', 'airline_code_value',
    'aircraft_code_value', 'city_name_value', 'time_value', 'flight_number_value',
    'class_description_value', 'day_period_value', 'state_name_value',
    'day_number_value', 'month_value', 'day_value', 'dollar_value', 'meal_description_value',
    'integer_value', 'basis_type_value', 'year_value',
}