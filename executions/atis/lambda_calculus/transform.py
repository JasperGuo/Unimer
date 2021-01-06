# coding=utf8

import re
import copy
from pprint import pprint
from .query import process_entity_string


ENTITY_PATTERN = re.compile(r'^[A-Z|a-z|\\]+:_([a-z]+)$')


ENTITY_TYPE_SET = set()
FUNCTION_NAME_SET = set()
FUNCTION_REPLACE_MAP = {
    "_abbrev": [{"name": "abbrev", "number_of_argument": 1, "argument_type": ["airline_code"], "return_type": "bool"}],
    "_capacity": [
        {"name": "capacity", "number_of_argument": 1, "argument_type": ["aircraft_code"], "return_type": "capacity"},
        {"name": "capacity", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "capactiy"}
    ],
    "_flight_number": [
        {"name": "flight_number", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "flight_number"},
        {"name": "is_flight_number", "number_of_argument": 2, "argument_type": ["flight_id", "flight_number"], "return_type": "bool"}
    ],
    "_airline_name": [{"name": "airline_name", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "airline_name"}],
    "_departure_time": [
        {"name": "departure_time", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "departure_time"},
        {"name": "is_flight_departure_time", "number_of_argument": 2, "argument_type": ["flight_id", "time"], "return_type": "bool"}
    ],
    "_miles_distant": [
        {"name": "miles_distant", "number_of_argument": 2, "argument_type": ["airport_code", "city_name"], "return_type": "miles_distant"},
        {"name": "miles_distant_between_city", "number_of_argument": 2, "argument_type": [
            "city_name", "city_name"], "return_type": "miles_distant"}
    ],
    "_minimum_connection_time": [
        {"name": "minimum_connection_time", "number_of_argument": 1, "argument_type": ["airport_code"], "return_type": "minimum_connection_time"}
    ],
    "_stops": [
        {"name": "get_number_of_stops", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "number_of_stops"},
        {"name": "is_flight_stops_specify_number_of_times", "number_of_argument": 2, "argument_type": ["flight_id", "integer"], "return_type": "bool"}
    ],
    "_time_elapsed": [
        {"name": "time_elapsed", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "time_elapsed"},
        {"name": "is_time_elapsed", "number_of_argument": 2, "argument_type": ["flight_id", "hour"], "return_type": "bool"}
    ],
    # Binary Predicate
    "is_mf": [
        {"name": "mf", "number_of_argument": 2, "argument_type": ["aircraft_code", "manufacturer"], "return_type": "bool"},
    ],
    "_aircraft_basis_type": [
        {"name": "is_aircraft_basis_type", "number_of_argument": 2,
            "argument_type": ["aircraft_code", "basis_type"], "return_type": "bool"},
    ],
    "_manufacturer": [
        {"name": "is_mf", "number_of_argument": 2,
            "argument_type": ["aircraft_code", "manufacturer"], "return_type": "bool"},
        {"name": "is_flight_manufacturer", "number_of_argument": 2, "argument_type": ["flight_id", "manufacturer"], "return_type": "bool"}
    ],
    "_services": [
        {"name": "is_services", "number_of_argument": 2, "argument_type": ["airline_code", "city_name"], "return_type": "bool"},
        {"name": "is_airline_services", "number_of_argument": 2, "argument_type": [
            "airline_code", "airport_code"], "return_type": "bool"}
    ],
    "_to": [
        {"name": "is_to", "number_of_argument": 2, "argument_type": ["flight_id", "airport_code"], "return_type": "bool"},
        {"name": "is_to", "number_of_argument": 2, "argument_type": ["flight_id", "city_name"], "return_type": "bool"},
        {"name": "is_to", "number_of_argument": 2, "argument_type": ["flight_id", "state_name"], "return_type": "bool"}
    ],
    "_from": [
        {"name": "is_from", "number_of_argument": 2, "argument_type": ["flight_id", "airport_code"], "return_type": "bool"},
        {"name": "is_from", "number_of_argument": 2, "argument_type": ["flight_id", "city_name"], "return_type": "bool"}
    ],
    "_loc:_t": [
        {"name": "is_loc_t", "number_of_argument": 2, "argument_type": ["airport_code", "city_name"], "return_type": "bool"},
        {"name": "is_loc_t_state", "number_of_argument": 2, "argument_type": [
            "airport_code", "state_name"], "return_type": "bool"},
        {"name": "is_loc_t_city_time_zone", "number_of_argument": 2, "argument_type": ["city_name", "time_zone_code"], "return_type": "bool"},
    ],
    "_from_airport": [
        {"name": "is_from_airport", "number_of_argument": 2, "argument_type": ["transport_type", "airport_code"], "return_type": "bool"},
        {"name": "is_from_airports_of_city", "number_of_argument": 2, "argument_type": ["transport_type", "city_name"], "return_type": "bool"},
    ],
    "_to_airport": [
        {"name": "is_to_airport", "number_of_argument": 2, "argument_type": ["transport_type", "city_name"], "return_type": "bool"},
    ],
    "_to_city": [
        {"name": "is_to_city", "number_of_argument": 2, "argument_type": ["transport_type", "city_name"], "return_type": "bool"},
    ],
    "_airline": [
        {"name": "is_flight_airline", "number_of_argument": 2, "argument_type": ["flight_id", "airline_code"], "return_type": "bool"},
        {"name": "is_aircraft_airline", "number_of_argument": 2, "argument_type": ["aircraft_code", "airline_code"], "return_type": "bool"},
        {"name": "is_airline_has_booking_class", "number_of_argument": 2, "argument_type": ["class_description", "airline_code"], "return_type": "bool"},
        {"name": "is_airline_provide_meal", "number_of_argument": 2, "argument_type": [
            "meal_code", "airline_code"], "return_type": "bool"},
        {"name": "is_airline", "number_of_argument": 1, "argument_type": ["airline_code"], "return_type": "bool"}
    ],
    "_airline:_e": [
        {"name": "get_flight_airline_code", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "airline_code"},
    ],
    "_stop": [
        {"name": "is_flight_stop_at_city", "number_of_argument": 2, "argument_type": ["flight_id", "city_name"], "return_type": "bool"},
        {"name": "is_flight_stop_at_airport", "number_of_argument": 2,
            "argument_type": ["flight_id", "airport_code"], "return_type": "bool"},
    ],
    "_class_type": [
        {"name": "is_flight_has_class_type", "number_of_argument": 2, "argument_type": ["flight_id", "class_description"], "return_type": "bool"},
        {"name": "is_fare_basis_code_class_type", "number_of_argument": 2, "argument_type": ["fare_basis_code", "class_description"], "return_type": "bool"},
    ],
    "_after_day": [
        {"name": "is_flight_after_day", "number_of_argument": 2, "argument_type": ["flight_id", "day"], "return_type": "bool"}
    ],
    "_approx_arrival_time": [
        {"name": "is_flight_approx_arrival_time", "number_of_argument": 2, "argument_type": ["flight_id", "arrival_time"], "return_type": "bool"}
    ],
    "_arrival_time": [
        {"name": "arrival_time", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "arrival_time"},
        {"name": "is_flight_arrival_time", "number_of_argument": 2, "argument_type": ["flight_id", "arrival_time"], "return_type": "bool"}
    ],
    "_approx_departure_time": [
        {"name": "is_flight_approx_departure_time", "number_of_argument": 2, "argument_type": ["flight_id", "departure_time"], "return_type": "bool"}
    ],
    "_approx_return_time": [
        {"name": "is_flight_approx_return_time", "number_of_argument": 2, "argument_type": ["flight_id", "return_time"], "return_type": "bool"}
    ],
    "_during_day": [
        {"name": "is_flight_during_day", "number_of_argument": 2, "argument_type": ["flight_id", "day_period"], "return_type": "bool"}
    ],
    "_during_day_arrival": [
        {"name": "is_flight_during_day_arrival", "number_of_argument": 2, "argument_type": ["flight_id", "day_period"], "return_type": "bool"}
    ],
    "_day_number": [
        {"name": "is_flight_on_day_number", "number_of_argument": 2, "argument_type": ["flight_id", "day_number"], "return_type": "bool"}
    ],
    "_day_arrival": [
        {"name": "is_flight_day_arrival", "number_of_argument": 2, "argument_type": ["flight_id", "day"], "return_type": "bool"}
    ],
    "_day": [
        {"name": "is_flight_on_day", "number_of_argument": 2,
            "argument_type": ["flight_id", "day"], "return_type": "bool"}
    ],
    "_month": [
        {"name": "is_flight_month_arrival", "number_of_argument": 2,
            "argument_type": ["flight_id", "month"], "return_type": "bool"}
    ],
    "_day_return": [
        {"name": "is_flight_day_return", "number_of_argument": 2, "argument_type": ["flight_id", "day"], "return_type": "bool"}
    ],
    "_day_number_arrival": [
        {"name": "is_flight_day_number_arrival", "number_of_argument": 2, "argument_type": ["flight_id", "day_number"], "return_type": "bool"}
    ],
    "_day_number_return": [
        {"name": "is_flight_day_number_return", "number_of_argument": 2, "argument_type": ["flight_id", "day_number"], "return_type": "bool"}
    ],
    "_month_arrival": [
        {"name": "is_flight_month_arrival", "number_of_argument": 2, "argument_type": ["flight_id", "month"], "return_type": "bool"}
    ],
    "_month_return": [
        {"name": "is_flight_month_return", "number_of_argument": 2, "argument_type": ["flight_id", "month"], "return_type": "bool"}
    ],
    "_days_from_today": [
        {"name": "is_flight_days_from_today", "number_of_argument": 2,
            "argument_type": ["flight_id", "integer"], "return_type": "bool"}
    ],
    # Unit Predicate
    "_aircraft": [
        {"name": "is_aircraft", "number_of_argument": 1, "argument_type": ["aircraft_code"], "return_type": "bool"},
        {"name": "is_flight_aircraft", "number_of_argument": 2, "argument_type": ["flight_id", "aircraft_code"], "return_type": "bool"},
    ],
    "_city": [
        {"name": "is_city", "number_of_argument": 1, "argument_type": ["city_name"], "return_type": "bool"}
    ],
    "_airport": [
        {"name": "is_airport", "number_of_argument": 1, "argument_type": ["airport_code"], "return_type": "bool"},
        {"name": "is_airport_of_city", "number_of_argument": 2, "argument_type": ["city_name", "airport_code"], "return_type": "bool"}
    ],
    "_flight": [
        {"name": "is_flight", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_tomorrow": [
        {"name": "is_tomorrow_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_before_day": [
        {"name": "is_flight_before_day", "number_of_argument": 2,
            "argument_type": ["flight_id", "month"], "return_type": "bool"}
    ],
    "_tomorrow_arrival": [
        {"name": "is_tomorrow_arrival_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_today": [
        {"name": "is_today_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_next_days": [
        {"name": "is_next_days_flight", "number_of_argument": 2,
            "argument_type": ["flight_id", "integer"], "return_type": "bool"}
    ],
    "_day_after_tomorrow": [
        {"name": "is_day_after_tomorrow_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_daily": [
        {"name": "is_daily_flight", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_discounted": [
        {"name": "is_discounted_flight", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_connecting": [
        {"name": "is_connecting_flight", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_oneway": [
        {"name": "is_oneway", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_has_stops": [
        {"name": "is_flight_has_stop", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_nonstop": [
        {"name": "is_non_stop_flight", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_meal:_t": [
        {"name": "is_meal", "number_of_argument": 1, "argument_type": ["meal_code"], "return_type": "bool"}
    ],
    "_meal": [
        {"name": "get_flight_meal", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "meal_description"},
        {"name": "is_flight_has_specific_meal", "number_of_argument": 2,
            "argument_type": ["flight_id", "meal_description"], "return_type": "bool"}
    ],
    "_meal_code": [
        {"name": "is_meal_code", "number_of_argument": 1, "argument_type": ["meal_code"], "return_type": "bool"},
        {"name": "is_flight_meal_code", "number_of_argument": 2, "argument_type": ["flight_id", "meal_code"], "return_type": "bool"},
    ],
    "_has_meal": [
        {"name": "is_flight_has_meal", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_tonight": [
        {"name": "is_flight_tonight", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_booking_class:_t": [
        {"name": "is_booking_class_t", "number_of_argument": 1,
            "argument_type": ["class_description"], "return_type": "bool"},
    ],
    "_booking_class": [
        {"name": "get_flight_booking_class", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "class_description"},
        {"name": "is_flight_has_booking_class", "number_of_argument": 2,
                 "argument_type": ["flight_id", "class_description"], "return_type": "bool"},
    ],
    "_class_of_service": [
        {"name": "is_class_of_service", "number_of_argument": 1, "argument_type": ["class_description"], "return_type": "bool"}
    ],
    "_fare_basis_code": [
        {"name": "is_fare_basis_code", "number_of_argument": 1, "argument_type": ["fare_basis_code"], "return_type": "bool"},
        {"name": "is_flight_has_specific_fare_basis_code", "number_of_argument": 2,
            "argument_type": ["flight_id", "fare_basis_code"], "return_type": "bool"},
        {"name": "is_specific_fare_basis_code", "number_of_argument": 2, "argument_type": ["fare_basis_code", "fare_basis_code"], "return_type": "bool"}
    ],
    "_economy": [
        {"name": "is_flight_economy", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "bool"},
        {"name": "is_economy", "number_of_argument": 1, "argument_type": ["fare_basis_code"], "return_type": "bool"},
    ],
    "_fare": [
        {"name": "get_flight_fare", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "one_direction_cost"},
        {"name": "get_booking_class_fare", "number_of_argument": 1, "argument_type": ["class_description"], "return_type": "one_direction_cost"},
        {"name": "is_fare", "number_of_argument": 1, "argument_type": ["fare_id"], "return_type": "bool"},
        {"name": "is_flight_cost_fare", "number_of_argument": 2, "argument_type": ["flight_id", "dollar"], "return_type": "bool"},
    ],
    "_cost": [
        {"name": "get_flight_cost", "number_of_argument": 1, "argument_type": [
            "flight_id"], "return_type": "round_trip_cost"},
    ],
    "_aircraft_code:t": [
        {"name": "is_aircraft_code_t", "number_of_argument": 1, "argument_type": ["aircraft_code"], "return_type": "bool"}
    ],
    "_aircraft_code": [
        {"name": "get_flight_aircraft_code", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "aircraft_code"},
        {"name": "is_flight_with_specific_aircraft", "number_of_argument": 2, "argument_type": ["flight_id", "aircraft_code"], "return_type": "bool"}
    ],
    "_ground_transport": [
        {"name": "is_ground_transport", "number_of_argument": 1, "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_rental_car": [
        {"name": "is_rental_car", "number_of_argument": 1, "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_limousine": [
        {"name": "is_limousine", "number_of_argument": 1, "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_rapid_transit": [
        {"name": "is_rapid_transit", "number_of_argument": 1, "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_taxi": [
        {"name": "is_taxi", "number_of_argument": 1, "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_air_taxi_operation": [
        {"name": "is_air_taxi_operation", "number_of_argument": 1, "argument_type": [
            "transport_type"], "return_type": "bool"}
    ],
    "_round_trip": [
        {"name": "is_round_trip", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_weekday": [
        {"name": "is_ground_transport_on_weekday", "number_of_argument": 1, "argument_type": ["transport_type"], "return_type": "bool"},
        {"name": "is_flight_on_weekday", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "bool"},
    ],
    "_year": [
        {"name": "is_flight_on_year", "number_of_argument": 2, "argument_type": ["flight_id", "year"], "return_type": "bool"},
    ],
    "_time_zone_code": [
        {"name": "is_time_zone_code", "number_of_argument": 1, "argument_type": ["time_zone_code"], "return_type": "bool"},
    ],
    "_turboprop": [
        {"name": "is_flight_turboprop", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"},
        {"name": "is_turboprop", "number_of_argument": 1, "argument_type": ["aircraft_code"], "return_type": "bool"},
    ],
    "_jet": [
        {"name": "is_flight_jet", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"},
    ],
    "_aircraft_code:_t": [
        {"name": "aircraft_code", "number_of_argument": 1,
            "argument_type": ["aircraft_code"], "return_type": "bool"},
    ],
    # Meta Predicate
    "_equals": [
        {"name": "equals", "number_of_argument": 2,
            "argument_type": ["*", "*"], "is_meta": True, "return_type": "bool"},
    ],
    "_equals:_t": [
        {"name": "equals", "number_of_argument": 2,
            "argument_type": ["*", "*"], "is_meta": True, "return_type": "bool"},
    ],
    "_<": [
        {"name": "less_than", "number_of_argument": 2,
            "argument_type": ["*", "*"], "is_meta": True, "return_type": "bool"},
    ],
    "_>": [
        {"name": "larger_than", "number_of_argument": 2,
            "argument_type": ["*", "*"], "is_meta": True, "return_type": "bool"},
    ],
    "_=": [
        {"name": "numerical_equals", "number_of_argument": 2,
            "argument_type": ["*", "*"], "is_meta": True, "return_type": "bool"},
    ],
    "the": [
        {"name": "the", "number_of_argument": 1,
            "argument_type": ["*"], "is_meta": True, "return_type": "*"},
    ],
    "_not": [
        {"name": "not", "number_of_argument": 1,
            "argument_type": ["*"], "is_meta": True, "return_type": "bool"},
    ],
    "_ground_fare": [
        {"name": "get_ground_fare", "number_of_argument": 1,
                 "argument_type": ["transport_type"], "return_type": "ground_fare"},
    ],
    "_stop_arrival_time": [
        {"name": "get_flight_stop_arrival_time", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "stop_arrival_time"},
    ],
    "_restriction_code": [
        {"name": "get_flight_restriction_code", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "restriction_code"},
    ]
}

ENTITY_SET_MAP = {
    "flight_id": "get_all_flight_ids",
    "city_name": "get_all_city_names",
    "airline_code": "get_all_airline_codes",
    "aircraft_code": "get_all_aircraft_codes",
    "airport_code": "get_all_airport_codes",
    "class_description": "get_all_booking_class_descriptions",
    "transport_type": "get_all_transport_types",
    "meal_code": "get_all_meal_codes",
    "meal_description": "get_all_meal_descriptions",
    "fare_basis_code": "get_all_fare_basis_codes",
    "time_zone_code": "get_all_time_zone_codes",
    "one_direction_cost": "get_all_one_direction_cost",
    "capacity": "get_all_capacity",
    "flight_number": "get_all_flight_number",
    "departure_time": "get_all_departure_time",
    "stop_arrival_time": "get_all_stop_arrival_time"
}


def read_data(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            questions.append(splits[0])
            logical_forms.append(splits[1])
    return questions, logical_forms


def standardize_lambda_calculus_varnames(ans):
    toks = ans.split(' ')
    varnames = {}
    new_toks = []
    for t in toks:
        if t == 'x' or t.startswith('$'):
            if ':' in t:
                # var definition
                splits = t.split(':')
                name, var_type = splits[0], splits[1]
                assert name not in varnames
                new_name = '$v%d' % len(varnames)
                varnames[name] = new_name
                new_toks.append(new_name + ":" + var_type)
            else:
                # t is a variable name
                if t in varnames:
                    new_toks.append(varnames[t])
                else:
                    new_varname = '$v%d' % len(varnames)
                    varnames[t] = new_varname
                    new_toks.append(new_varname)
        else:
            new_toks.append(t)
    lf = ' '.join(new_toks)
    return lf


def split_tokens(lf):
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        lf = lf.replace(a, b)
    return lf


def normalize_lambda_calculus(logical_form):
    lf = split_tokens(logical_form)
    lf = re.sub(' +', ' ', lf)
    s = standardize_lambda_calculus_varnames(lf)
    variables = ["$v0", "$v1", "$v2", "$v3"]
    for var in variables:
        s = s.replace(var + " e ", "%s:e " % var)
        s = s.replace(var + " i ", "%s:i " % var)
    s = s.replace(' :', ":").replace(
        '\s+', ' ').replace("( ", "(").replace(" )", ")").replace(')\s)', '))').strip().lower()
    s = re.sub(' +', ' ', s)
    return s


def tokenize_logical_form(logical_form):
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        # ("\\+", " \\+ "),
    ]
    normalized_lc = re.sub(' +', ' ', logical_form)
    for a, b in replacements:
        normalized_lc = normalized_lc.replace(a, b)
    tokens = [t for t in normalized_lc.split()]
    return tokens


class Node:
    def __init__(self, lf, lidx, ridx, variable_type_constraints, variable_interactions):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx
        self.variable_type_constraints = variable_type_constraints
        self.variable_interactions = variable_interactions


def extract_entity(lf):
    tokens = lf.split(":_")
    return tokens


def get_function_return_type(function_name):
    candidates = list()
    for _, funcs in FUNCTION_REPLACE_MAP.items():
        for f in funcs:
            if f['name'] == function_name:
                candidates.append(f['return_type'])
        if len(candidates) > 0:
            break
    if len(candidates) > 0:
        for t in candidates:
            if t != 'bool':
                return t
    return None


def add_new_interactions(interaction_set, new_interaction):
    variable_map = {
        "x": 0,
        "y": 1,
        "z": 2,
        "m": 3
    }
    mapped_interaction = tuple(sorted(list(new_interaction), key=lambda x: variable_map[x]))
    interaction_set.add(mapped_interaction)


def get_all_variables_from_interactions(interaction_set):
    variables = set()
    for inter in interaction_set:
        variables.add(inter[0])
        variables.add(inter[1])
    return variables


def replace_function_name(
    function_name,
    number_of_arguments,
    arguments,
    argument_variable_constraints,
    argument_variable_interactions
):
    if function_name not in FUNCTION_REPLACE_MAP:
        assert function_name in ['_minutes_distant',
                                 '_named', '_overnight']
        # print(function_name)
        return function_name, dict(), set()
    names = FUNCTION_REPLACE_MAP[function_name]
    replaced_function_name = function_name
    argument_types = None
    is_meta_function = False
    if len(names) == 1:
        replaced_function_name = names[0]['name']
        argument_types = names[0]["argument_type"]
        is_meta_function = "is_meta" in names[0] and names[0]['is_meta'] is True
    else:
        # select by arugment number
        feasible_index = []
        for idx, name in enumerate(names):
            if name['number_of_argument'] == number_of_arguments:
                replaced_function_name = name['name']
                argument_types = name["argument_type"]
                feasible_index.append(idx)
        if len(feasible_index) == 0:
            raise Exception("No feasible functions in Python")
        elif len(feasible_index) == 1:
            idx = feasible_index[0]
            replaced_function_name = names[idx]['name']
            argument_types = names[idx]['argument_type']
            is_meta_function = "is_meta" in names[idx] and names[idx]['is_meta'] is True
        else:
            best_index = 0
            best_count = 0
            for idx in feasible_index:
                name = names[idx]
                types = names[idx]['argument_type']
                count = 0
                for t, arg in zip(types, arguments):
                    _arg = arg.replace('"', "")
                    match = ENTITY_PATTERN.match(_arg)
                    if match:
                        e, et = process_entity_string(_arg)
                        if et == t:
                            count += 1
                    else:
                        if _arg in ['x', 'y', 'z', 'm'] and _arg in argument_variable_constraints:
                            et = argument_variable_constraints[_arg]
                            if et == t:
                                count += 1
                if count > best_count:
                    best_index = idx
                    best_count = count
            replaced_function_name = names[best_index]['name']
            argument_types = names[best_index]['argument_type']
            is_meta_function = "is_meta" in names[best_index] and names[best_index]['is_meta'] is True
    # Derive type constraints
    # print(function_name, replaced_function_name, number_of_arguments, arguments, argument_types) 
    variable_constraints = dict()
    assert number_of_arguments == len(argument_types)
    if is_meta_function:
        if replaced_function_name in ['equals', 'numerical_equals', 'less_than', 'larger_than']:
            if arguments[0] in ["x", "y", "z", "m"]:
                arg_variable = arguments[0]
                arg_func = arguments[1]
            elif arguments[1] in ["x", "y", "z", "m"]:
                arg_variable = arguments[1]
                arg_func = arguments[0]
            else:
                arg_variable, arg_func = None, None
            if arg_variable is not None and arg_func is not None:
                match = ENTITY_PATTERN.match(arg_func.replace('"', ""))
                if match:
                    e, et = process_entity_string(arg_func.replace('"', ""))
                    variable_constraints[arg_variable] = et
                elif arg_func.startswith("argmin(") or arg_func.startswith("argmax("):
                    for _var in [" y:", " z:", " m:"]:
                        processed_var = _var.replace(":", "").strip()
                        if _var in arg_func and processed_var in argument_variable_constraints:
                            variable_constraints[arg_variable] = argument_variable_constraints[processed_var]
                            break
                else:
                    arg_func_return_type = get_function_return_type(arg_func[:arg_func.index("(")])
                    # print(arg_func)
                    # print(arg_func[:arg_func.index("(")])
                    # print(arg_func_return_type)
                    if arg_func_return_type is not None and arg_func_return_type not in ['*', 'bool']:
                        variable_constraints[arg_variable] = arg_func_return_type
    else:
        for argument, atype in zip(arguments, argument_types):
            if argument in ["x", "y", "z", "m"]:
                variable_constraints[argument] = atype

    # Findout interactions
    interactions = set()
    assert len(arguments) == len(argument_variable_interactions)
    if len(arguments) == 1:
        if len(argument_variable_interactions[0]) > 0:
            interactions = argument_variable_interactions[0]
        else:
            if arguments[0] in ["x", "y", "z", "m"]:
                add_new_interactions(interactions, (arguments[0], arguments[0],))
    else:
        assert len(arguments) == 2
        if len(argument_variable_interactions[0]) == 0 and len(argument_variable_interactions[1]) == 0:
            if arguments[0] in ["x", "y", "z", "m"] and arguments[1] in ["x", "y", "z", "m"]:
                add_new_interactions(
                    interactions, (arguments[0], arguments[1],))
            elif arguments[0] in ["x", "y", "z", "m"]:
                add_new_interactions(
                    interactions, (arguments[0], arguments[0],))
            elif arguments[1] in ["x", "y", "z", "m"]:
                add_new_interactions(
                    interactions, (arguments[1], arguments[1],))
        elif len(argument_variable_interactions[0]) > 0 and len(argument_variable_interactions[1]) > 0:
            variables_0 = get_all_variables_from_interactions(
                argument_variable_interactions[0])
            variables_1 = get_all_variables_from_interactions(
                argument_variable_interactions[1])
            for v0 in variables_0:
                for v1 in variables_1:
                    add_new_interactions(interactions, (v0, v1,))
        elif len(argument_variable_interactions[0]) > 0:
            # len(argument_variable_interactions[1]) == 0
            if arguments[1] in ["x", "y", "z", "m"]:
                variables_0 = get_all_variables_from_interactions(
                    argument_variable_interactions[0])
                for v0 in variables_0:
                    add_new_interactions(interactions, (v0, arguments[1],))
            else:
                interactions = argument_variable_interactions[0]
        elif len(argument_variable_interactions[1]) > 0:
            # len(argument_variable_interactions[0]) == 0
            if arguments[0] in ["x", "y", "z", "m"]:
                variables_1 = get_all_variables_from_interactions(
                    argument_variable_interactions[1])
                for v1 in variables_1:
                    add_new_interactions(interactions, (v1, arguments[0],))
            else:
                interactions = argument_variable_interactions[0]
    return replaced_function_name, variable_constraints, interactions


def update_variable_type_constraints(constarints_1, constraints_2):
    for key, value in constraints_2.items():
        if key not in constarints_1:
            constarints_1[key] = value
        else:
            # print(key, value, constarints_1[key])
            assert constarints_1[key] == value


def transform_lambda_calculus(logical_form):
    normalized_lf = normalize_lambda_calculus(logical_form)
    # Replace Variable
    python_lf = normalized_lf.replace('$v0:e ', 'x ')
    python_lf = python_lf.replace('$v1:e ', 'y ')
    python_lf = python_lf.replace('$v2:e ', 'z ')
    python_lf = python_lf.replace('$v3:e ', 'm ')
    python_lf = python_lf.replace('$v0:i ', 'x ')
    python_lf = python_lf.replace('$v1:i ', 'y ')
    python_lf = python_lf.replace('$v2:i ', 'z ')
    python_lf = python_lf.replace('$v3:i ', 'm ')
    python_lf = python_lf.replace('$v0', 'x')
    python_lf = python_lf.replace('$v1', 'y')
    python_lf = python_lf.replace('$v2', 'z')
    python_lf = python_lf.replace('$v3', 'm')
    python_lf = re.sub(' +', ' ', python_lf)
    python_lf_variable_type_constraints = dict()

    print(python_lf)

    global_variable_constraints = dict()
    free_variables = set()
    python_lf_variable_interactions = set()
    if python_lf.count('(') == 0:
        # Simple Cases, A single entity
        entity_name, entity_type = extract_entity(python_lf)
        ENTITY_TYPE_SET.add(entity_type)
        python_lf = '%s("%s")' % (entity_type, entity_name)
    else:
        left_brackets = list()
        # original_lf = copy.deepcopy(python_lf)
        tokens = tokenize_logical_form(python_lf)
        nodes = list()
        for tidx, token in enumerate(tokens):
            if token == '(':
                left_brackets.append(tidx)
            elif token == ')':
                node_variable_type_constraints = dict()
                pidx = left_brackets.pop()
                children_nodes = list()
                for nidx, node in enumerate(nodes):
                    if pidx < node.lidx and tidx > node.ridx:
                        children_nodes.append(node)
                for n in children_nodes:
                    nodes.remove(n)
                if len(children_nodes) == 0:
                    sub_tokens = tokens[pidx + 1 :tidx]
                    function_name = sub_tokens[0]
                    number_of_arguments = len(sub_tokens[1:])
                    replaced_function_name, node_variable_type_constraints, node_variable_interactions = replace_function_name(
                        function_name, number_of_arguments, sub_tokens[1:], global_variable_constraints, [set() for i in range(number_of_arguments)])
                    _sub_lf = "%s(%s)" % (
                        replaced_function_name, ','.join(sub_tokens[1:]))
                else:
                    # Has children
                    sub_tokens = tokens[pidx + 1:tidx]
                    function_name = sub_tokens[0]
                    # if ":" in function_name:
                    #     function_name = function_name.split(":")[0]

                    _inside_bracket_stack = 0
                    other_children = list()
                    children_num = 0
                    children_position = list()
                    for sub_token in sub_tokens[1:]:
                        if sub_token == '(':
                            _inside_bracket_stack += 1
                            if _inside_bracket_stack == 1:
                                children_num += 1
                                children_position.append('bracket')
                        elif sub_token == ')':
                            _inside_bracket_stack -= 1
                        else:
                            if _inside_bracket_stack == 0:
                                children_num += 1
                                other_children.append(sub_token)
                                children_position.append('token')

                    assert children_num == len(children_position)
                    string = list()
                    if function_name == '_lambda':
                        assert len(other_children) == 1 and len(children_nodes) == 1 
                        child_node = children_nodes.pop(0)
                        variable = other_children.pop(0)
                        node_variable_type_constraints = copy.deepcopy(child_node.variable_type_constraints)
                        node_variable_interactions = copy.deepcopy(child_node.variable_interactions)
                        free_variables.add(variable)
                        _sub_lf = "lambda %s: %s" % (variable, child_node.lf)
                    elif function_name in ['_argmin', '_argmax', '_sum']:
                        assert len(other_children) == 1 and len(children_nodes) == 2
                        variable = other_children.pop(0)
                        node_1, node_2 = children_nodes.pop(0), children_nodes.pop(0)
                        node_variable_interactions = copy.deepcopy(
                            node_1.variable_interactions)
                        update_variable_type_constraints(node_variable_type_constraints, node_1.variable_type_constraints)
                        update_variable_type_constraints(node_variable_type_constraints, node_2.variable_type_constraints)
                        if variable in node_variable_type_constraints:
                            set_function = ENTITY_SET_MAP[node_variable_type_constraints[variable]]
                        else:
                            set_function = "None"
                        if function_name in ['_argmin', '_argmax']:
                            replaced_function_name = function_name[1:]
                        else:
                            replaced_function_name = 'sum_predicate'
                        _sub_lf = "%s(%s,%s,%s)" % (
                            replaced_function_name,
                            ("(lambda %s: %s)" % (variable, node_1.lf)),
                            ("(lambda %s: %s)" % (variable, node_2.lf)),
                            set_function
                        )
                    elif function_name in ['_count', '_exists', '_the']:
                        assert len(other_children) == 1 and len(children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        update_variable_type_constraints(node_variable_type_constraints, child_node.variable_type_constraints)
                        node_variable_interactions = copy.deepcopy(child_node.variable_interactions)
                        # print(node_variable_type_constraints, variable)
                        if variable in node_variable_type_constraints:
                            _sub_lf = "%s((lambda %s: %s), %s)" % (
                                function_name[1:], variable, child_node.lf,
                                ENTITY_SET_MAP[node_variable_type_constraints[variable]])
                        else:
                            _sub_lf = "%s((lambda %s: %s), %s)" % (
                                function_name[1:], variable, child_node.lf, None)
                    elif function_name in ['_max', '_min']:
                        # ad-hoc
                        assert len(other_children) == 1 and len(
                            children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        update_variable_type_constraints(
                            node_variable_type_constraints, child_node.variable_type_constraints)
                        node_variable_interactions = copy.deepcopy(
                            child_node.variable_interactions)

                        assert child_node.lf.startswith('exists(')
                        child_lf = child_node.lf[len('exists('):-1]
                        ridx = child_lf.rindex(",")
                        function_entity_set = child_lf[ridx + 1:].strip()
                        child_lf = child_lf[:ridx]

                        # replace
                        pattern = '(numerical_equals\((.*),%s\))' % variable
                        results = re.findall(pattern, child_lf)
                        assert len(results) == 1
                        results = results[0]
                        child_lf = child_lf.replace(results[0], "True")
                        numerical_function = "lambda %s: %s(%s)" % (
                            variable, results[1][:results[1].index('(')], variable)

                        _sub_lf = "%s_predicate(%s, (%s), %s)" % (
                            function_name[1:], child_lf, numerical_function, function_entity_set)
                    elif function_name in ['_and', '_or']:
                        node_variable_interactions = set()
                        for position in children_position:
                            if position == 'bracket':
                                n = children_nodes.pop(0)
                                string.append(n.lf)
                                update_variable_type_constraints(node_variable_type_constraints, n.variable_type_constraints)
                                node_variable_interactions |= n.variable_interactions
                            else:
                                sub_token = other_children.pop(0)
                                string.append(sub_token)
                        if function_name == '_and':
                            _sub_lf = "(%s)" % (' and '.join(string))
                        else:
                            _sub_lf = "(%s)" % (' or '.join(string))
                    else:
                        argument_variable_interactions = list()
                        for position in children_position:
                            if position == 'bracket':
                                n = children_nodes.pop(0)
                                string.append(n.lf)
                                update_variable_type_constraints(node_variable_type_constraints, n.variable_type_constraints)
                                argument_variable_interactions.append(
                                    n.variable_interactions)
                            else:
                                sub_token = other_children.pop(0)
                                string.append(sub_token)
                                argument_variable_interactions.append(set())
                        replaced_function_name, variable_type_constraints, node_variable_interactions = replace_function_name(
                            function_name, children_num, string, global_variable_constraints, argument_variable_interactions)
                        # Update variable constraints
                        update_variable_type_constraints(node_variable_type_constraints, variable_type_constraints)
                        _sub_lf = "%s(%s)" % (
                            replaced_function_name, ','.join(string))
                FUNCTION_NAME_SET.add(function_name)
                new_node = Node(
                    _sub_lf, pidx, tidx, node_variable_type_constraints, node_variable_interactions)
                global_variable_constraints.update(node_variable_type_constraints)
                # print(node_variable_type_constraints)
                nodes.append(new_node)
            else:
                if tidx > 0 and (not tokens[tidx - 1] == '(') and ":_" in token:
                    # token is not function name
                    tokens[tidx] = '"%s"' % tokens[tidx]
        assert len(nodes) == 1
        python_lf_variable_type_constraints = nodes[0].variable_type_constraints
        python_lf_variable_interactions = nodes[0].variable_interactions
        python_lf = nodes[0].lf

    # Remove unit variable interactions
    for v in ["x", "y", "z", "m"]:
        python_lf_variable_interactions -= {(v, v,)}

    # Optimization
    # 1. Optimize for lambda x: exists(lambda y: )
    if python_lf.startswith("lambda x: exists("):
        child_lf = python_lf[len("lambda x:exists(("):-1].strip()
        ridx = child_lf.rindex(",")
        function_entity_set = child_lf[ridx + 1:].strip()
        child_lf = child_lf[:ridx]
        # print(child_lf)

        # replace
        pattern = '(numerical_equals\((.*),x\))'
        results = re.findall(pattern, child_lf)
        if len(results) > 0:
            assert len(results) == 1
            results = results[0]
            child_lf = child_lf.replace(results[0], "True")
            _numerical_function = results[1][:results[1].index('(')]
            if _numerical_function == 'get_ground_fare':
                to_city_result = re.findall('(is_to_city\(y,(.*?)\))', child_lf)
                from_airport_result = re.findall(
                    '(is_from_airport\(y,(.*?)\))', child_lf)
                to_city, from_airport = None, None
                if len(to_city_result) > 0:
                    assert len(to_city_result) == 1
                    to_city_result = to_city_result[0]
                    to_city = to_city_result[1]
                if len(from_airport_result) > 0:
                    assert len(from_airport_result) == 1
                    from_airport_result = from_airport_result[0]
                    from_airport = from_airport_result[1]
                if to_city is not None and from_airport is not None:
                    numerical_function = "lambda x: get_ground_fare_3(%s,%s,x)" % (to_city, from_airport)
                elif to_city is not None:
                    numerical_function = "lambda x: get_ground_fare_1(%s, x)" % (to_city)
                elif from_airport is not None:
                    # from_airport
                    numerical_function = "lambda x: get_ground_fare_2(%s, x)" % (
                        from_airport)
                else:
                    # All None
                    numerical_function = "lambda x: get_ground_fare(x)"
            elif _numerical_function == '_minutes_distant':
                to_city_result = re.findall('(is_to_city\(y,(.*?)\))', child_lf)
                from_airport_result = re.findall(
                    '(is_from_airport\(y,(.*?)\))', child_lf)
                to_city, from_airport = None, None
                if len(to_city_result) > 0:
                    assert len(to_city_result) == 1
                    to_city_result = to_city_result[0]
                    to_city = to_city_result[1]
                if len(from_airport_result) > 0:
                    assert len(from_airport_result) == 1
                    from_airport_result = from_airport_result[0]
                    from_airport = from_airport_result[1]

                if to_city is not None and from_airport is not None:
                    numerical_function = "lambda x: get_minutes_distant_3(%s,%s)" % (
                        to_city, from_airport)
                elif to_city is not None:
                    numerical_function = "lambda x: get_minutes_distant_1(%s)" % (
                        to_city)
                elif from_airport is not None:
                    # from_airport
                    numerical_function = "lambda x: get_minutes_distant_2(%s)" % (
                        from_airport)
                else:
                    raise Exception("Invalid _minutes_distant")
            else:
                numerical_function = "lambda x: %s(x)" % _numerical_function
        elif len(re.findall('is_to\(y,x\)', child_lf)) == 1:
            # is_to
            child_lf = child_lf.replace("is_to(y,x)", "True")
            numerical_function = "lambda x: get_flight_destination(x)"
        elif len(re.findall('_named\(y,x\)', child_lf)) == 1:
            child_lf = child_lf.replace("_named(y,x)", "True")
            numerical_function = "lambda x: x"
        elif len(re.findall('is_flight_stop_at_city\(y,x\)', child_lf)) == 1:
            child_lf = child_lf.replace("is_flight_stop_at_city(y,x)", "True")
            numerical_function = "lambda x: get_flight_stop_city(x)"
        elif len(re.findall('_minutes_distant\(y,x\)', child_lf)) == 1:
            child_lf = child_lf.replace("_minutes_distant(y,x)", "True")
            numerical_function = "lambda x: get_miniutes_distant(x)"
        else:
            numerical_function = None
        
        if numerical_function is not None:
            free_variables = set()
            python_lf = "get_target_value(%s, (%s), %s)" % (
                child_lf, numerical_function, function_entity_set)
        else:
            raise Exception("Failed to Optimize")

    # 2. Wrap value
    if python_lf.startswith("lambda"):
        # List Comprehension
        # Only on variable
        # if " x:" in python_lf and " y:" not in python_lf and " z:" not in python_lf and " m:" not in python_lf:
        if len(free_variables) == 1:
            # One Free variables
            # print(python_lf)
            free_variables = set()
            assert "x" in python_lf_variable_type_constraints
            variable_type = python_lf_variable_type_constraints['x']
            entity_set_func = ENTITY_SET_MAP[variable_type]
            python_lf = "[e for e in %s() if (%s)(e)]" % (
                entity_set_func, python_lf)
        elif len(free_variables) == 2:
            # Two free variables
            # Try to optimize
            assert python_lf.startswith("lambda x: lambda y:")
            child_lf = python_lf[len("lambda x: lambda y:"):].strip()

            # replace
            pattern = '(numerical_equals\((.*?)\(([x|y])\),([y|x])\))'
            results = re.findall(pattern, child_lf)
            if len(results) > 0:
                # Optimize for simple numerical_equals (e.g., get_flight_fare)
                assert len(results) == 1
                results = results[0]
                child_lf = child_lf.replace(results[0], "True")
                _numerical_function, _numerical_function_variable, _numerical_equals_variable = results[1], results[2], results[3]
                predicate = "(lambda %s: %s)" % (_numerical_function_variable, child_lf)
                numerical_function = "(lambda %s: %s(%s))" % (_numerical_equals_variable, _numerical_function, _numerical_equals_variable)
                assert _numerical_function_variable in python_lf_variable_type_constraints
                variable_type = python_lf_variable_type_constraints[_numerical_function_variable]
                function_entity_set = ENTITY_SET_MAP[variable_type]
                python_lf = "get_target_value(%s, %s, %s)" % (
                    predicate, numerical_function, function_entity_set)
                free_variables = set()
            else:
                # Optimize for numerical_equals of count
                pattern_1 = '(numerical_equals\(([x|y]),(count\(.*,\s*(get_all_.*?)\))\))'
                pattern_2 = '(numerical_equals\((count\(.*,\s*(get_all_.*?)\)),([x|y]))\)'
                results_1 = re.findall(pattern_1, child_lf)
                results_2 = re.findall(pattern_2, child_lf)
                is_valid = False
                if len(results_1) > 0 or len(results_2) > 0:
                    if len(results_1) > 0:
                        results_1 = results_1[0]
                        count_function, count_variable = results_1[2], results_1[1]
                        to_be_replaced = results_1[0]
                    else:
                        results_2 = results_2[0]
                        count_function, count_variable = results_2[1], results_2[2]
                        to_be_replaced = results_1[0]
                    if count_variable == 'x':
                        primary_variable = 'y'
                    else:
                        primary_variable = 'x'
                    if primary_variable in python_lf_variable_type_constraints and count_variable not in python_lf_variable_type_constraints:
                        function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints[primary_variable]]
                        child_lf = child_lf.replace(to_be_replaced, "True")
                        predicate = "(lambda %s: %s)" % (primary_variable, child_lf)
                        numerical_function = "(lambda %s: %s)" % (
                            primary_variable, count_function)
                        python_lf = "get_target_value(%s, %s, %s)" % (
                            predicate, numerical_function, function_entity_set)
                        is_valid = True
                        free_variables = set()

                if not is_valid:
                    if "x" in python_lf_variable_type_constraints and "y" in python_lf_variable_type_constraints:
                        if python_lf_variable_type_constraints["x"] == python_lf_variable_type_constraints["y"]:
                            # No relations between variables
                            # TODO make it systematic
                            # Assume that the expression is only made up of and & predicates
                            child_lf_subfunctions = child_lf[1:-1].split(" and ")
                            python_lf = list()
                            for v in ['x', 'y']:
                                result = list()
                                for lf in child_lf_subfunctions:
                                    _lf = lf.strip()
                                    _lf = _lf.replace("(", " ( ").replace(")", " ) ").replace(",", " , ")
                                    if (" %s " % v) in _lf:
                                        result.append(lf)
                                expression = "[e for e in %s() if (lambda %s: (%s))(e)]" % (
                                    function_entity_set, v, " and ".join(result))
                                python_lf.append(expression)
                            python_lf = " + ".join(python_lf)
                            free_variables = set()
                        else:
                            # fail to optimize
                            x_function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["x"]]
                            y_function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["y"]]
                            python_lf = "[(xe, ye) for xe in %s() for ye in %s() if (lambda x,y: %s)(xe, ye)]" % (x_function_entity_set, y_function_entity_set, child_lf)
                            free_variables = set()

        elif len(free_variables) >= 3:
            # Three free variables
            assert python_lf.startswith("lambda x: lambda y: lambda z: lambda m:") \
                or python_lf.startswith("lambda x: lambda y: lambda z:")
            if python_lf.startswith("lambda x: lambda y: lambda z: lambda m:"):
                child_lf = python_lf[len(
                    "lambda x: lambda y: lambda z: lambda m:"): ].strip()
                variable_list = ['x', 'y', 'z', 'm']
            else:
                child_lf = python_lf[len(
                    "lambda x: lambda y: lambda z:"):].strip()
                variable_list = ['x', 'y', 'z']

            if all([v in python_lf_variable_type_constraints for v in variable_list]):
                sample_variable_type = python_lf_variable_type_constraints["x"]
                if all([python_lf_variable_type_constraints[v] == sample_variable_type for v in variable_list]) and len(python_lf_variable_interactions) == 0:
                    function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["x"]]
                    # No relations between variables
                    # TODO make it systematic
                    # Assume that the expression is only made up of and & predicates
                    child_lf_subfunctions = child_lf[1:-1].split(" and ")
                    python_lf = list()
                    for v in variable_list:
                        result = list()
                        for lf in child_lf_subfunctions:
                            _lf = lf.strip()
                            _lf = _lf.replace("(", " ( ").replace(")", " ) ").replace(",", " , ")
                            if (" %s " % v) in _lf:
                                result.append(lf)
                        expression = "[e for e in %s() if (lambda %s: (%s))(e)]" % (
                            function_entity_set, v, " and ".join(result))
                        python_lf.append(expression)
                    python_lf = " + ".join(python_lf)
                    free_variables = set()
                else:
                    # analyze interactions
                    variable_dependencies = dict()
                    for s, t in python_lf_variable_interactions:
                        if s not in variable_dependencies:
                            variable_dependencies[s] = list()
                        if t not in variable_dependencies:
                            variable_dependencies[t] = list()
                        variable_dependencies[s].append(t)
                        variable_dependencies[t].append(s)

                    if len(variable_dependencies) == len(variable_list):
                        is_single_target_dependency = False
                        number_of_single_target_variable = 0
                        target_variables = set()
                        for v, dependents in variable_dependencies.items():
                            if len(dependents) == 1:
                                target_variables.add(dependents[0])
                                number_of_single_target_variable += 1
                        if number_of_single_target_variable == len(variable_list) - 1 \
                            and len(target_variables) == 1:
                            # Optimize
                            target_variable = list(target_variables)[0]
                            pattern_1 = '(numerical_equals\((.*?)\(%s\),([y|x|z|m])\))' % target_variable
                            pattern_2 = '(numerical_equals\(([y|x|z|m])\),(.*?)\(%s\),)' % target_variable
                            results_1 = re.findall(pattern_1, child_lf)
                            results_2 = re.findall(pattern_2, child_lf)
                            results = results_1 + results_2
                            if len(results) == len(variable_list) - 1:
                                is_single_target_dependency = True
                                predicate = child_lf
                                numerical_functions = list()
                                for r in results:
                                    predicate = predicate.replace(r[0], "True")
                                    numerical_functions.append("(lambda %s: %s(%s))" % (
                                        r[2], r[1], r[2]))
                                predicate = "(lambda %s: %s)" % (
                                    target_variable, predicate)
                                function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints[target_variable]]
                                if len(numerical_functions) == 2:
                                    python_lf = "get_target_values(%s, [%s, %s], %s)" % (
                                        predicate, numerical_functions[0], numerical_functions[1], function_entity_set)
                                else:
                                    assert len(numerical_functions) == 3
                                    python_lf = "get_target_values(%s, [%s,%s,%s,] %s)" % (
                                        predicate, numerical_functions[0], numerical_functions[1], numerical_functions[2], function_entity_set)
                                free_variables = set()

                    if not is_single_target_dependency:
                        # Fail to optimize
                        x_function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["x"]]
                        y_function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["y"]]
                        z_function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["z"]]
                        if len(variable_list) == 4:
                            m_function_entity_set = ENTITY_SET_MAP[python_lf_variable_type_constraints["m"]]
                            python_lf = "[(xe, ye, ze) for xe in %s() for ye in %s() for ze in %s() for me in %s() if (lambda x,y,z,m: %s)(xe, ye,ze,me)]" % \
                                (x_function_entity_set, y_function_entity_set, z_function_entity_set, m_function_entity_set, child_lf)
                        else:
                            python_lf = "[(xe, ye, ze) for xe in %s() for ye in %s() for ze in %s() if (lambda x,y,z: %s)(xe, ye,ze)]" % \
                                (x_function_entity_set, y_function_entity_set, z_function_entity_set, child_lf)
                        free_variables = set()

    return python_lf, python_lf_variable_type_constraints, free_variables, python_lf_variable_interactions


if __name__ == '__main__':
    questions, logical_forms = read_data(
        '../../../data/atis/atis_lambda_test.tsv')

    # sorted_logical_forms = sorted(logical_forms, key=lambda x: len(x))
    sorted_logical_forms = [
        "( _lambda $0 e ( _exists $1 ( _and ( _= ( _minutes_distant $1 ) $0 ) ( _to_city $1 boston:_ci ) ) ) )"]
    for lidx, lf in enumerate(sorted_logical_forms):
        # print(lidx)
        # print(lf)
        python_lf, python_lf_variable_type_constraints, free_variables, python_lf_variable_interactions = transform_lambda_calculus(
            lf)
        # if len(free_variables) > 0:
        print(lidx)
        print(lf)
        print(python_lf)
        print(python_lf_variable_type_constraints)
        print(python_lf_variable_interactions)
        print(free_variables)
        print('==\n\n')

    pprint(FUNCTION_NAME_SET)
