# coding=utf8

"""
FunQL Grammar for ATIS
"""

ROOT_RULE = 'statement -> [answer]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['(answer ws)']
GRAMMAR_DICTIONARY['answer'] = ['("answer" ws "(" ws predicate ws ")" )']

GRAMMAR_DICTIONARY['predicate'] = [
    'meta', 'object', 'collection', 'relation',
    '("intersection" ws "(" ws predicate ws "," conjunction ")")',
    '("or" ws "(" ws predicate ws "," conjunction ws ")")',
    '("not" ws "(" predicate ")")'
]
GRAMMAR_DICTIONARY['conjunction'] = [
    '(predicate ws "," ws conjunction)',
    '(predicate)'
]

GRAMMAR_DICTIONARY['relation'] = [
    # Airline
    '(_abbrev)', '(_airline_1)', '(_airline_2)', '(_airline_name)', '(_airline)',
    # Aircraft
    '(_aircraft)', '(_aircraft_1)', '(_aircraft_2)', '(_aircraft_basis_type_2)',
    '(_capacity)', '(_jet)', '(_manufacturer_2)', '(_turboprop)',
    # Airport
    '(_airport)', '(_airport_1)',
    # Flight Property
    '(_connecting)', '(_discounted)', '(_economy)', '(_flight_number)', '(_flight_number_2)', '(_flight)',
    '(_from_1)', '(_from_2)', '(_has_meal)', '(_has_stops)', '(_nonstop)', '(_oneway)',
    '(_round_trip)', '(_to_1)', '(_to_2)',
    # Flight Time
    '(_after_day_2)', '(_approx_arrival_time_2)', '(_approx_departure_time_2)',
    '(_approx_return_time_2)', '(_arrival_time)', '(_arrival_time_2)', '(_before_day_2)',
    '(_daily)', '(_day_2)', '(_day_after_tomorrow)', '(_day_arrival_2)', '(_day_number_2)',
    '(_day_number_arrival_2)', '(_day_number_return_2)', '(_day_return_2)',
    '(_days_from_today_2)', '(_departure_time)', '(_departure_time_2)',
    '(_during_day_2)', '(_during_day_arrival_2)',
    '(_month_2)', '(_month_arrival_2)', '(_month_return_2)',
    '(_next_days_2)', '(_overnight)', '(_today)', '(_tomorrow)',
    '(_tomorrow_arrival)', '(_tonight)',
    # Flight Fare
    '(_fare)', '(_fare_2)', '(_fare_basis_code)', '(_fare_basis_code_2)',
    '(_fare_time)',
    # Flight Stop
    '(_stop_1)', '(_stop_2)', '(_stop_arrival_time)',
    '(_stops)', '(_stops_2)',
    # Booking Class
    '(_booking_class_1)', '(_booking_class_2)', '(_class_of_service)', '(_class_type_2)',
    # Ground Transport
    '(_air_taxi_operation)', '(_from_airport_2)', '(_ground_fare)', '(_ground_transport)',
    '(_limousine)', '(_rapid_transit)', '(_rental_car)', '(_to_city_2)',  '(_taxi)',
    # City
    '(_city)',
    # Meal
    '(_meal)', '(_meal_2)', '(_meal_code)', '(_meal_code_2)',
    # Service
    '(_services_1)', '(_services_2)', '(_services)',
    # Other
    '(_flight_aircraft)', '(_flight_airline)',
    '(_flight_fare)', '(_loc_1)', '(_loc_2)',
    '(_miles_distant)', '(_minimum_connection_time)', '(_minutes_distant)',
    '(_named_1)', '(_restriction_code)',
    '(_time_elapsed)', '(_time_elapsed_2)',
    '(_time_zone_code)', '(_weekday)', '(_year_2)',
]
GRAMMAR_DICTIONARY['_abbrev'] = ['("_abbrev(" predicate ")")']
GRAMMAR_DICTIONARY['_after_day_2'] = ['("_after_day_2(" predicate ")")']
GRAMMAR_DICTIONARY['_air_taxi_operation'] = ['("_air_taxi_operation(" predicate ")")']
GRAMMAR_DICTIONARY['_aircraft'] = ['("_aircraft(" predicate ")")']
GRAMMAR_DICTIONARY['_aircraft_1'] = ['("_aircraft_1(" predicate ")")']
GRAMMAR_DICTIONARY['_aircraft_2'] = ['("_aircraft_2(" predicate ")")']
GRAMMAR_DICTIONARY['_aircraft_basis_type_2'] = ['("_aircraft_basis_type_2(" predicate ")")']
GRAMMAR_DICTIONARY['_airline'] = ['("_airline(" predicate ")")']
GRAMMAR_DICTIONARY['_airline_1'] = ['("_airline_1(" predicate ")")']
GRAMMAR_DICTIONARY['_airline_2'] = ['("_airline_2(" predicate ")")']
GRAMMAR_DICTIONARY['_airline_name'] = ['("_airline_name(" predicate ")")']
GRAMMAR_DICTIONARY['_airport'] = ['("_airport(" predicate ")")']
GRAMMAR_DICTIONARY['_airport_1'] = ['("_airport_1(" predicate ")")']
GRAMMAR_DICTIONARY['_approx_arrival_time_2'] = ['("_approx_arrival_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_approx_departure_time_2'] = ['("_approx_departure_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_approx_return_time_2'] = ['("_approx_return_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_arrival_time'] = ['("_arrival_time(" predicate ")")']
GRAMMAR_DICTIONARY['_arrival_time_2'] = ['("_arrival_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_before_day_2'] = ['("_before_day_2(" predicate ")")']
GRAMMAR_DICTIONARY['_booking_class_1'] = ['("_booking_class_1(" predicate ")")']
GRAMMAR_DICTIONARY['_booking_class_2'] = ['("_booking_class_2(" predicate ")")']
GRAMMAR_DICTIONARY['_capacity'] = ['("_capacity(" predicate ")")']
GRAMMAR_DICTIONARY['_city'] = ['("_city(" predicate ")")']
GRAMMAR_DICTIONARY['_class_of_service'] = ['("_class_of_service(" predicate ")")']
GRAMMAR_DICTIONARY['_class_type_2'] = ['("_class_type_2(" predicate ")")']
GRAMMAR_DICTIONARY['_connecting'] = ['("_connecting(" predicate ")")']
GRAMMAR_DICTIONARY['_daily'] = ['("_daily(" predicate ")")']
GRAMMAR_DICTIONARY['_day_2'] = ['("_day_2(" predicate ")")']
GRAMMAR_DICTIONARY['_day_after_tomorrow'] = ['("_day_after_tomorrow(" predicate ")")']
GRAMMAR_DICTIONARY['_day_arrival_2'] = ['("_day_arrival_2(" predicate ")")']
GRAMMAR_DICTIONARY['_day_number_2'] = ['("_day_number_2(" predicate ")")']
GRAMMAR_DICTIONARY['_day_number_arrival_2'] = ['("_day_number_arrival_2(" predicate ")")']
GRAMMAR_DICTIONARY['_day_number_return_2'] = ['("_day_number_return_2(" predicate ")")']
GRAMMAR_DICTIONARY['_day_return_2'] = ['("_day_return_2(" predicate ")")']
GRAMMAR_DICTIONARY['_days_from_today_2'] = ['("_days_from_today_2(" predicate ")")']
GRAMMAR_DICTIONARY['_departure_time'] = ['("_departure_time(" predicate ")")']
GRAMMAR_DICTIONARY['_departure_time_2'] = ['("_departure_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_discounted'] = ['("_discounted(" predicate ")")']
GRAMMAR_DICTIONARY['_during_day_2'] = ['("_during_day_2(" predicate ")")']
GRAMMAR_DICTIONARY['_during_day_arrival_2'] = ['("_during_day_arrival_2(" predicate ")")']
GRAMMAR_DICTIONARY['_economy'] = ['("_economy(" predicate ")")']
GRAMMAR_DICTIONARY['_fare'] = ['("_fare(" predicate ")")']
GRAMMAR_DICTIONARY['_fare_2'] = ['("_fare_2(" predicate ")")']
GRAMMAR_DICTIONARY['_fare_basis_code'] = ['("_fare_basis_code(" predicate ")")']
GRAMMAR_DICTIONARY['_fare_basis_code_2'] = ['("_fare_basis_code_2(" predicate ")")']
GRAMMAR_DICTIONARY['_fare_time'] = ['("_fare_time(" predicate ")")']
GRAMMAR_DICTIONARY['_flight'] = ['("_flight(" predicate ")")']
GRAMMAR_DICTIONARY['_flight_aircraft'] = ['("_flight_aircraft(" predicate ")")']
GRAMMAR_DICTIONARY['_flight_airline'] = ['("_flight_airline(" predicate ")")']
GRAMMAR_DICTIONARY['_flight_fare'] = ['("_flight_fare(" predicate ")")']
GRAMMAR_DICTIONARY['_flight_number'] = ['("_flight_number(" predicate ")")']
GRAMMAR_DICTIONARY['_flight_number_2'] = ['("_flight_number_2(" predicate ")")']
GRAMMAR_DICTIONARY['_from_1'] = ['("_from_1(" predicate ")")']
GRAMMAR_DICTIONARY['_from_2'] = ['("_from_2(" predicate ")")']
GRAMMAR_DICTIONARY['_from_airport_2'] = ['("_from_airport_2(" predicate ")")']
GRAMMAR_DICTIONARY['_ground_fare'] = ['("_ground_fare(" predicate ")")']
GRAMMAR_DICTIONARY['_ground_transport'] = ['("_ground_transport(" predicate ")")']
GRAMMAR_DICTIONARY['_has_meal'] = ['("_has_meal(" predicate ")")']
GRAMMAR_DICTIONARY['_has_stops'] = ['("_has_stops(" predicate ")")']
GRAMMAR_DICTIONARY['_jet'] = ['("_jet(" predicate ")")']
GRAMMAR_DICTIONARY['_limousine'] = ['("_limousine(" predicate ")")']
GRAMMAR_DICTIONARY['_loc_1'] = ['("_loc:_t_1(" predicate ")")']
GRAMMAR_DICTIONARY['_loc_2'] = ['("_loc:_t_2(" predicate ")")']
GRAMMAR_DICTIONARY['_manufacturer_2'] = ['("_manufacturer_2(" predicate ")")']
GRAMMAR_DICTIONARY['_max'] = ['("_max(" predicate ")")']
GRAMMAR_DICTIONARY['_meal'] = ['("_meal(" predicate ")")']
GRAMMAR_DICTIONARY['_meal_2'] = ['("_meal_2(" predicate ")")']
GRAMMAR_DICTIONARY['_meal_code'] = ['("_meal_code(" predicate ")")']
GRAMMAR_DICTIONARY['_meal_code_2'] = ['("_meal_code_2(" predicate ")")']
GRAMMAR_DICTIONARY['_miles_distant'] = ['("_miles_distant(" ws predicate ws "," ws predicate ws ")")']
GRAMMAR_DICTIONARY['_min'] = ['("_min(" predicate ")")']
GRAMMAR_DICTIONARY['_minimum_connection_time'] = ['("_minimum_connection_time(" predicate ")")']
GRAMMAR_DICTIONARY['_minutes_distant'] = ['("_minutes_distant(" predicate ")")']
GRAMMAR_DICTIONARY['_month_2'] = ['("_month_2(" predicate ")")']
GRAMMAR_DICTIONARY['_month_arrival_2'] = ['("_month_arrival_2(" predicate ")")']
GRAMMAR_DICTIONARY['_month_return_2'] = ['("_month_return_2(" predicate ")")']
GRAMMAR_DICTIONARY['_named_1'] = ['("_named_1(" predicate ")")']
GRAMMAR_DICTIONARY['_next_days_2'] = ['("_next_days_2(" predicate ")")']
GRAMMAR_DICTIONARY['_nonstop'] = ['("_nonstop(" predicate ")")']
GRAMMAR_DICTIONARY['_oneway'] = ['("_oneway(" predicate ")")']
GRAMMAR_DICTIONARY['_overnight'] = ['("_overnight(" predicate ")")']
GRAMMAR_DICTIONARY['_rapid_transit'] = ['("_rapid_transit(" predicate ")")']
GRAMMAR_DICTIONARY['_rental_car'] = ['("_rental_car(" predicate ")")']
GRAMMAR_DICTIONARY['_restriction_code'] = ['("_restriction_code(" predicate ")")']
GRAMMAR_DICTIONARY['_round_trip'] = ['("_round_trip(" predicate ")")']
GRAMMAR_DICTIONARY['_services'] = ['("_services(" ws predicate ws "," ws predicate ws ")")']
GRAMMAR_DICTIONARY['_services_1'] = ['("_services_1(" predicate ")")']
GRAMMAR_DICTIONARY['_services_2'] = ['("_services_2(" predicate ")")']
GRAMMAR_DICTIONARY['_stop_1'] = ['("_stop_1(" predicate ")")']
GRAMMAR_DICTIONARY['_stop_2'] = ['("_stop_2(" predicate ")")']
GRAMMAR_DICTIONARY['_stop_arrival_time'] = ['("_stop_arrival_time(" predicate ")")']
GRAMMAR_DICTIONARY['_stops'] = ['("_stops(" predicate ")")']
GRAMMAR_DICTIONARY['_stops_2'] = ['("_stops_2(" predicate ")")']
GRAMMAR_DICTIONARY['_taxi'] = ['("_taxi(" predicate ")")']
GRAMMAR_DICTIONARY['_time_elapsed'] = ['("_time_elapsed(" predicate ")")']
GRAMMAR_DICTIONARY['_time_elapsed_2'] = ['("_time_elapsed_2(" predicate ")")']
GRAMMAR_DICTIONARY['_time_zone_code'] = ['("_time_zone_code(" predicate ")")']
GRAMMAR_DICTIONARY['_to_1'] = ['("_to_1(" predicate ")")']
GRAMMAR_DICTIONARY['_to_2'] = ['("_to_2(" predicate ")")']
GRAMMAR_DICTIONARY['_to_city_2'] = ['("_to_city_2(" predicate ")")']
GRAMMAR_DICTIONARY['_today'] = ['("_today(" predicate ")")']
GRAMMAR_DICTIONARY['_tomorrow'] = ['("_tomorrow(" predicate ")")']
GRAMMAR_DICTIONARY['_tomorrow_arrival'] = ['("_tomorrow_arrival(" predicate ")")']
GRAMMAR_DICTIONARY['_tonight'] = ['("_tonight(" predicate ")")']
GRAMMAR_DICTIONARY['_turboprop'] = ['("_turboprop(" predicate ")")']
GRAMMAR_DICTIONARY['_weekday'] = ['("_weekday(" predicate ")")']
GRAMMAR_DICTIONARY['_year_2'] = ['("_year_2(" predicate ")")']

# Meta-Predicates
GRAMMAR_DICTIONARY['meta'] = [
    '(_less_than_arrival_time_2)', '(_less_than_departure_time_2)', '(_less_than_fare_2)',
    '(_larger_than_arrival_time_2)', '(_larger_than_capacity_2)', '(_larger_than_departure_time_2)',
    '(_larger_than_stops_2)', '(_equals)',
    '(argmax_arrival_time)', '(argmax_capacity)', '(argmax_count)',
    '(argmax_departure_time)', '(argmax_fare)', '(argmax_stops)',
    '(argmin_arrival_time)', '(argmin_capacity)', '(argmin_departure_time)',
    '(argmin_fare)', '(argmin_miles_distant_2)', '(argmin_stops)',
    '(argmin_time_elapsed)', '(count)', '(sum_capacity)', '(sum_stops)',
    '(_max)', '(_min)',
]
GRAMMAR_DICTIONARY['_less_than_arrival_time_2'] = ['("_<_arrival_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_less_than_departure_time_2'] = ['("_<_departure_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_less_than_fare_2'] = ['("_<_fare_2(" predicate ")")']
GRAMMAR_DICTIONARY['_larger_than_arrival_time_2'] = ['("_>_arrival_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_larger_than_capacity_2'] = ['("_>_capacity_2(" predicate ")")']
GRAMMAR_DICTIONARY['_larger_than_departure_time_2'] = ['("_>_departure_time_2(" predicate ")")']
GRAMMAR_DICTIONARY['_larger_than_stops_2'] = ['("_>_stops_2(" predicate ")")']
GRAMMAR_DICTIONARY['_equals'] = ['("_equals(" ws predicate ws "," predicate ws ")")']
GRAMMAR_DICTIONARY['argmax_arrival_time'] = ['("argmax_arrival_time(" predicate ")")']
GRAMMAR_DICTIONARY['argmax_capacity'] = ['("argmax_capacity(" predicate ")")']
GRAMMAR_DICTIONARY['argmax_count'] = ['("argmax_count(" predicate ")")']
GRAMMAR_DICTIONARY['argmax_departure_time'] = ['("argmax_departure_time(" predicate ")")']
GRAMMAR_DICTIONARY['argmax_fare'] = ['("argmax_fare(" predicate ")")']
GRAMMAR_DICTIONARY['argmax_stops'] = ['("argmax_stops(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_arrival_time'] = ['("argmin_arrival_time(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_capacity'] = ['("argmin_capacity(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_departure_time'] = ['("argmin_departure_time(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_fare'] = ['("argmin_fare(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_miles_distant_2'] = ['("argmin_miles_distant_2(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_stops'] = ['("argmin_stops(" predicate ")")']
GRAMMAR_DICTIONARY['argmin_time_elapsed'] = ['("argmin_time_elapsed(" predicate ")")']
GRAMMAR_DICTIONARY['count'] = ['("count(" predicate ")")']
GRAMMAR_DICTIONARY['sum_capacity'] = ['("sum_capacity(" predicate ")")']
GRAMMAR_DICTIONARY['sum_stops'] = ['("sum_stops(" predicate ")")']
GRAMMAR_DICTIONARY['_max'] = ['("_max(" predicate ")")']
GRAMMAR_DICTIONARY['_min'] = ['("_min(" predicate ")")']

# Collection
GRAMMAR_DICTIONARY['collection'] = [
    '(all_flights)', '(all_booking_classes)', '(all_aircrafts)',
    '(all_airlines)', '(all_airports)', '(all_class_of_service)',
    '(all_fare_basis_codes)', '(all_ground_transports)', '(all_meal_codes)',
    '(all_cities)',
]
GRAMMAR_DICTIONARY['all_flights'] = ['"_flight" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_cities'] = ['"_city" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_booking_classes'] = ['"_booking_class:_t" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_aircrafts'] = ['"_aircraft" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_airlines'] = ['"_airline" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_airports'] = ['"_airport" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_class_of_service'] = ['"_class_of_service" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_fare_basis_codes'] = ['"_fare_basis_code" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_ground_transports'] = ['"_ground_transport" ws "(" ws "all" ws ")"']
GRAMMAR_DICTIONARY['all_meal_codes'] = ['"_meal_code" ws "(" ws "all" ws ")"']

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
    'class_description_value', 'day_period_value', 'state_name_value',
    'day_number_value', 'month_value', 'day_value', 'dollar_value', 'meal_description_value',
    'integer_value', 'basis_type_value', 'year_value',
}