# coding=utf8


import re
import copy


ENTITY_PATTERN = re.compile(r'^[A-Z|a-z|\\|_|\d]+:_([a-z]+)$')


ENTITY_TYPE_MAP = {
    "ac": "aircraft_code",
    "al": "airline_code",
    "ci": "city_name",
    "ap": "airport_code",
    "fn": "flight_number",
    "cl": "class_description",
    "ti": "time",
    "pd": "day_period",
    "mf": "manufacturer",
    "mn": "month",
    "da": "day",
    "i": "integer",
    "yr": "year",
    "dn": "day_number",
    "do": "dollar",
    "hr": "hour",
    "rc": "meal_code",
    "st": "state_name",
    "fb": "fare_basis_code",
    "me": "meal_description",
    "bat": "basis_type",
    "dc": "days_code"
}


FUNCTION_REPLACE_MAP = {
    "_abbrev": [
        {"name": "abbrev", "number_of_argument": 1, "argument_type": ["airline_code"], "return_type": "airline_name"}
    ],
    "_capacity": [
        {"name": "capacity", "number_of_argument": 1, "argument_type": [
            "aircraft_code"], "return_type": "capacity"},
        {"name": "capacity", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "capactiy"}
    ],
    "_flight_number": [
        {"name": "flight_number", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "flight_number"},
        {"name": "is_flight_number", "number_of_argument": 2, "argument_type": [
            "flight_id", "flight_number"], "return_type": "bool"}
    ],
    "_airline_name": [{"name": "airline_name", "number_of_argument": 1, "argument_type": ["flight_id"], "return_type": "airline_name"}],
    "_departure_time": [
        {"name": "departure_time", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "departure_time"},
        {"name": "is_flight_departure_time", "number_of_argument": 2,
            "argument_type": ["flight_id", "time"], "return_type": "bool"}
    ],
    "_miles_distant": [
        {"name": "miles_distant", "number_of_argument": 2, "argument_type": [
            "airport_code", "city_name"], "return_type": "miles_distant"},
        {"name": "miles_distant_between_city", "number_of_argument": 2, "argument_type": [
            "city_name", "city_name"], "return_type": "miles_distant"}
    ],
    "_minimum_connection_time": [
        {"name": "minimum_connection_time", "number_of_argument": 1, "argument_type": [
            "airport_code"], "return_type": "minimum_connection_time"}
    ],
    "_stops": [
        {"name": "get_number_of_stops", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "number_of_stops"},
        {"name": "is_flight_stops_specify_number_of_times", "number_of_argument": 2,
            "argument_type": ["flight_id", "integer"], "return_type": "bool"}
    ],
    "_time_elapsed": [
        {"name": "time_elapsed", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "time_elapsed"},
        {"name": "is_time_elapsed", "number_of_argument": 2,
            "argument_type": ["flight_id", "hour"], "return_type": "bool"}
    ],
    # Binary Predicate
    "is_mf": [
        {"name": "mf", "number_of_argument": 2, "argument_type": [
            "aircraft_code", "manufacturer"], "return_type": "bool"},
    ],
    "_aircraft_basis_type": [
        {"name": "is_aircraft_basis_type", "number_of_argument": 2,
            "argument_type": ["aircraft_code", "basis_type"], "return_type": "bool"},
    ],
    "_manufacturer": [
        {"name": "is_mf", "number_of_argument": 2,
            "argument_type": ["aircraft_code", "manufacturer"], "return_type": "bool"},
        {"name": "is_flight_manufacturer", "number_of_argument": 2,
            "argument_type": ["flight_id", "manufacturer"], "return_type": "bool"}
    ],
    "_services": [
        {"name": "is_services", "number_of_argument": 2, "argument_type": [
            "airline_code", "city_name"], "return_type": "bool"},
        {"name": "is_airline_services", "number_of_argument": 2, "argument_type": [
            "airline_code", "airport_code"], "return_type": "bool"}
    ],
    "_to": [
        {"name": "is_to", "number_of_argument": 2, "argument_type": [
            "flight_id", "airport_code"], "return_type": "bool"},
        {"name": "is_to", "number_of_argument": 2, "argument_type": [
            "flight_id", "city_name"], "return_type": "bool"},
        {"name": "is_to", "number_of_argument": 2, "argument_type": [
            "flight_id", "state_name"], "return_type": "bool"}
    ],
    "_from": [
        {"name": "is_from", "number_of_argument": 2, "argument_type": [
            "flight_id", "airport_code"], "return_type": "bool"},
        {"name": "is_from", "number_of_argument": 2, "argument_type": [
            "flight_id", "city_name"], "return_type": "bool"}
    ],
    "_loc:_t": [
        {"name": "is_loc_t", "number_of_argument": 2, "argument_type": [
            "airport_code", "city_name"], "return_type": "bool"},
        {"name": "is_loc_t_state", "number_of_argument": 2, "argument_type": [
            "airport_code", "state_name"], "return_type": "bool"},
        {"name": "is_loc_t_city_time_zone", "number_of_argument": 2, "argument_type": [
            "city_name", "time_zone_code"], "return_type": "bool"},
    ],
    "_from_airport": [
        {"name": "is_from_airport", "number_of_argument": 2, "argument_type": [
            "transport_type", "airport_code"], "return_type": "bool"},
        {"name": "is_from_airports_of_city", "number_of_argument": 2, "argument_type": [
            "transport_type", "city_name"], "return_type": "bool"},
    ],
    "_to_airport": [
        {"name": "is_to_airport", "number_of_argument": 2, "argument_type": [
            "transport_type", "city_name"], "return_type": "bool"},
    ],
    "_to_city": [
        {"name": "is_to_city", "number_of_argument": 2, "argument_type": [
            "transport_type", "city_name"], "return_type": "bool"},
    ],
    "_airline": [
        {"name": "is_flight_airline", "number_of_argument": 2, "argument_type": [
            "flight_id", "airline_code"], "return_type": "bool"},
        {"name": "is_aircraft_airline", "number_of_argument": 2, "argument_type": [
            "aircraft_code", "airline_code"], "return_type": "bool"},
        {"name": "is_airline_has_booking_class", "number_of_argument": 2, "argument_type": [
            "class_description", "airline_code"], "return_type": "bool"},
        {"name": "is_airline_provide_meal", "number_of_argument": 2, "argument_type": [
            "meal_code", "airline_code"], "return_type": "bool"},
        {"name": "is_airline", "number_of_argument": 1,
            "argument_type": ["airline_code"], "return_type": "bool"}
    ],
    "_airline:_e": [
        {"name": "get_flight_airline_code", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "airline_code"},
    ],
    "_stop": [
        {"name": "is_flight_stop_at_city", "number_of_argument": 2,
            "argument_type": ["flight_id", "city_name"], "return_type": "bool"},
        {"name": "is_flight_stop_at_airport", "number_of_argument": 2,
            "argument_type": ["flight_id", "airport_code"], "return_type": "bool"},
    ],
    "_class_type": [
        {"name": "is_flight_has_class_type", "number_of_argument": 2, "argument_type": [
            "flight_id", "class_description"], "return_type": "bool"},
        {"name": "is_fare_basis_code_class_type", "number_of_argument": 2, "argument_type": [
            "fare_basis_code", "class_description"], "return_type": "bool"},
    ],
    "_after_day": [
        {"name": "is_flight_after_day", "number_of_argument": 2,
            "argument_type": ["flight_id", "day"], "return_type": "bool"}
    ],
    "_approx_arrival_time": [
        {"name": "is_flight_approx_arrival_time", "number_of_argument": 2,
            "argument_type": ["flight_id", "arrival_time"], "return_type": "bool"}
    ],
    "_arrival_time": [
        {"name": "arrival_time", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "arrival_time"},
        {"name": "is_flight_arrival_time", "number_of_argument": 2,
            "argument_type": ["flight_id", "arrival_time"], "return_type": "bool"}
    ],
    "_approx_departure_time": [
        {"name": "is_flight_approx_departure_time", "number_of_argument": 2,
            "argument_type": ["flight_id", "departure_time"], "return_type": "bool"}
    ],
    "_approx_return_time": [
        {"name": "is_flight_approx_return_time", "number_of_argument": 2,
            "argument_type": ["flight_id", "return_time"], "return_type": "bool"}
    ],
    "_during_day": [
        {"name": "is_flight_during_day", "number_of_argument": 2,
            "argument_type": ["flight_id", "day_period"], "return_type": "bool"}
    ],
    "_during_day_arrival": [
        {"name": "is_flight_during_day_arrival", "number_of_argument": 2,
            "argument_type": ["flight_id", "day_period"], "return_type": "bool"}
    ],
    "_day_number": [
        {"name": "is_flight_on_day_number", "number_of_argument": 2,
            "argument_type": ["flight_id", "day_number"], "return_type": "bool"}
    ],
    "_day_arrival": [
        {"name": "is_flight_day_arrival", "number_of_argument": 2,
            "argument_type": ["flight_id", "day"], "return_type": "bool"}
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
        {"name": "is_flight_day_return", "number_of_argument": 2,
            "argument_type": ["flight_id", "day"], "return_type": "bool"}
    ],
    "_day_number_arrival": [
        {"name": "is_flight_day_number_arrival", "number_of_argument": 2,
            "argument_type": ["flight_id", "day_number"], "return_type": "bool"}
    ],
    "_day_number_return": [
        {"name": "is_flight_day_number_return", "number_of_argument": 2,
            "argument_type": ["flight_id", "day_number"], "return_type": "bool"}
    ],
    "_month_arrival": [
        {"name": "is_flight_month_arrival", "number_of_argument": 2,
            "argument_type": ["flight_id", "month"], "return_type": "bool"}
    ],
    "_month_return": [
        {"name": "is_flight_month_return", "number_of_argument": 2,
            "argument_type": ["flight_id", "month"], "return_type": "bool"}
    ],
    "_days_from_today": [
        {"name": "is_flight_days_from_today", "number_of_argument": 2,
            "argument_type": ["flight_id", "integer"], "return_type": "bool"}
    ],
    # Unit Predicate
    "_aircraft": [
        {"name": "is_aircraft", "number_of_argument": 1,
            "argument_type": ["aircraft_code"], "return_type": "bool"},
        {"name": "get_flight_aircraft_code", "number_of_argument": 1,
         "argument_type": ["flight_id"], "return_type": "aircraft_code"},
        {"name": "is_flight_aircraft", "number_of_argument": 2, "argument_type": [
            "flight_id", "aircraft_code"], "return_type": "bool"},
    ],
    "_city": [
        {"name": "is_city", "number_of_argument": 1,
            "argument_type": ["city_name"], "return_type": "bool"}
    ],
    "_airport": [
        {"name": "is_airport", "number_of_argument": 1,
            "argument_type": ["airport_code"], "return_type": "bool"},
        {"name": "is_airport_of_city", "number_of_argument": 2, "argument_type": [
            "city_name", "airport_code"], "return_type": "bool"}
    ],
    "_flight": [
        {"name": "is_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
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
        {"name": "is_daily_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_discounted": [
        {"name": "is_discounted_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_connecting": [
        {"name": "is_connecting_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_oneway": [
        {"name": "is_oneway", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_has_stops": [
        {"name": "is_flight_has_stop", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_nonstop": [
        {"name": "is_non_stop_flight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_meal:_t": [
        {"name": "is_meal", "number_of_argument": 1,
            "argument_type": ["meal_code"], "return_type": "bool"}
    ],
    "_meal": [
        {"name": "get_flight_meal", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "meal_description"},
        {"name": "is_flight_has_specific_meal", "number_of_argument": 2,
            "argument_type": ["flight_id", "meal_description"], "return_type": "bool"}
    ],
    "_meal_code": [
        {"name": "is_meal_code", "number_of_argument": 1,
            "argument_type": ["meal_code"], "return_type": "bool"},
        {"name": "is_flight_meal_code", "number_of_argument": 2,
            "argument_type": ["flight_id", "meal_code"], "return_type": "bool"},
    ],
    "_has_meal": [
        {"name": "is_flight_has_meal", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_tonight": [
        {"name": "is_flight_tonight", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
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
        {"name": "is_class_of_service", "number_of_argument": 1,
            "argument_type": ["class_description"], "return_type": "bool"}
    ],
    "_fare_basis_code": [
        {"name": "is_fare_basis_code", "number_of_argument": 1,
            "argument_type": ["fare_basis_code"], "return_type": "bool"},
        {"name": "is_flight_has_specific_fare_basis_code", "number_of_argument": 2,
            "argument_type": ["flight_id", "fare_basis_code"], "return_type": "bool"},
        {"name": "is_specific_fare_basis_code", "number_of_argument": 2, "argument_type": [
            "fare_basis_code", "fare_basis_code"], "return_type": "bool"}
    ],
    "_economy": [
        {"name": "is_flight_economy", "number_of_argument": 1,
                 "argument_type": ["flight_id"], "return_type": "bool"},
        {"name": "is_economy", "number_of_argument": 1,
            "argument_type": ["fare_basis_code"], "return_type": "bool"},
    ],
    "_fare": [
        {"name": "get_flight_fare", "number_of_argument": 1, "argument_type": [
            "flight_id"], "return_type": "one_direction_cost"},
        {"name": "get_booking_class_fare", "number_of_argument": 1, "argument_type": [
            "class_description"], "return_type": "one_direction_cost"},
        {"name": "is_fare", "number_of_argument": 1,
            "argument_type": ["fare_id"], "return_type": "bool"},
        {"name": "is_flight_cost_fare", "number_of_argument": 2,
            "argument_type": ["flight_id", "dollar"], "return_type": "bool"},
    ],
    "_cost": [
        {"name": "get_flight_cost", "number_of_argument": 1, "argument_type": [
            "flight_id"], "return_type": "round_trip_cost"},
    ],
    "_aircraft_code:t": [
        {"name": "is_aircraft_code_t", "number_of_argument": 1,
            "argument_type": ["aircraft_code"], "return_type": "bool"}
    ],
    "_aircraft_code": [
        {"name": "get_flight_aircraft_code", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "aircraft_code"},
        {"name": "is_flight_with_specific_aircraft", "number_of_argument": 2,
            "argument_type": ["flight_id", "aircraft_code"], "return_type": "bool"}
    ],
    "_ground_transport": [
        {"name": "is_ground_transport", "number_of_argument": 1,
            "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_rental_car": [
        {"name": "is_rental_car", "number_of_argument": 1,
            "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_limousine": [
        {"name": "is_limousine", "number_of_argument": 1,
            "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_rapid_transit": [
        {"name": "is_rapid_transit", "number_of_argument": 1,
            "argument_type": ["transport_type"], "return_type": "bool"}
    ],
    "_taxi": [
        {"name": "is_taxi", "number_of_argument": 1, "argument_type": [
            "transport_type"], "return_type": "bool"}
    ],
    "_air_taxi_operation": [
        {"name": "is_air_taxi_operation", "number_of_argument": 1, "argument_type": [
            "transport_type"], "return_type": "bool"}
    ],
    "_round_trip": [
        {"name": "is_round_trip", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"}
    ],
    "_weekday": [
        {"name": "is_ground_transport_on_weekday", "number_of_argument": 1,
            "argument_type": ["transport_type"], "return_type": "bool"},
        {"name": "is_flight_on_weekday", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"},
    ],
    "_year": [
        {"name": "is_flight_on_year", "number_of_argument": 2,
            "argument_type": ["flight_id", "year"], "return_type": "bool"},
    ],
    "_time_zone_code": [
        {"name": "is_time_zone_code", "number_of_argument": 1,
            "argument_type": ["time_zone_code"], "return_type": "bool"},
    ],
    "_turboprop": [
        {"name": "is_flight_turboprop", "number_of_argument": 1,
            "argument_type": ["flight_id"], "return_type": "bool"},
        {"name": "is_turboprop", "number_of_argument": 1,
            "argument_type": ["aircraft_code"], "return_type": "bool"},
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


def read_data(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            questions.append(splits[0])
            logical_forms.append(splits[1])
    return questions, logical_forms


def split_tokens(lf):
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        lf = lf.replace(a, b)
    return lf


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


def extract_entity(lf):
    tokens = lf.split(":_")
    return tokens


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


def process_entity_string(entity, default=""):
    assert isinstance(entity, str)
    if ":_" in entity:
        splits = entity.split(":_")
        entity_name = splits[0]
        entity_type = ENTITY_TYPE_MAP[splits[1]]
    else:
        entity_type = default
        entity_name = entity
    if '_' in entity_name:
        entity_name = entity_name.replace("_", " ")
    return entity_name, entity_type


def is_variable(var):
    return re.match('[A-Z]', var) is not None


def get_new_variable(global_variables):
    max_value = ord('A')
    for v in global_variables:
        if ord(v) > max_value:
            max_value = ord(v)
    assert max_value < ord('Z')
    return chr(max_value + 1)


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


def is_entity_function(function_name):
    candidates = list()
    for _, funcs in FUNCTION_REPLACE_MAP.items():
        for f in funcs:
            if f['name'] == function_name:
                candidates.append(f['return_type'])
        if len(candidates) > 0:
            break
    if len(candidates) > 0:
        return candidates[0] != 'bool'
    else:
        return False


def rewrite(
    function_name,
    number_of_arguments,
    arguments,
    argument_variable_constraints,
    global_variables,
):
    if function_name not in FUNCTION_REPLACE_MAP:
        assert function_name in ['_minutes_distant',
                                 '_named', '_overnight']
        resultant_lf = "%s(%s)" % (function_name, ','.join(arguments))
        return resultant_lf, dict()

    names = FUNCTION_REPLACE_MAP[function_name]
    rewrite_function_name = function_name
    argument_types = None
    is_meta_function = False
    if len(names) == 1:
        rewrite_function_name = names[0]['name']
        argument_types = names[0]["argument_type"]
        is_meta_function = "is_meta" in names[0] and names[0]['is_meta'] is True
    else:
        # select by arugment number
        feasible_index = []
        for idx, name in enumerate(names):
            if name['number_of_argument'] == number_of_arguments:
                rewrite_function_name = name['name']
                argument_types = name["argument_type"]
                feasible_index.append(idx)
        if len(feasible_index) == 0:
            raise Exception("No feasible functions in Python")
        elif len(feasible_index) == 1:
            idx = feasible_index[0]
            rewrite_function_name = names[idx]['name']
            argument_types = names[idx]['argument_type']
            is_meta_function = "is_meta" in names[idx] and names[idx]['is_meta'] is True
        else:
            # Select by Argument Type
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
                    elif _arg.startswith("argmin_") or _arg.startswith("argmax_"):
                        # argmin, argmax
                        index = _arg.index("(") + 1
                        var = _arg[index:index+1]
                        if var in argument_variable_constraints:
                            et = argument_variable_constraints[var]
                            if et == t:
                                count += 1
                    else:
                        if is_variable(_arg) and _arg in argument_variable_constraints:
                            et = argument_variable_constraints[_arg]
                            if et == t:
                                count += 1
                if count > best_count:
                    best_index = idx
                    best_count = count
            rewrite_function_name = names[best_index]['name']
            argument_types = names[best_index]['argument_type']
            is_meta_function = "is_meta" in names[best_index] and names[best_index]['is_meta'] is True
    # Derive type constraints, Type Inference
    # print(function_name, rewrite_function_name, number_of_arguments, arguments, argument_types)
    variable_constraints = dict()
    assert number_of_arguments == len(argument_types)
    if is_meta_function:
        if rewrite_function_name in ['equals', 'numerical_equals', 'less_than', 'larger_than']:
            if is_variable(arguments[0]):
                arg_variable = arguments[0]
                arg_func = arguments[1]
            elif is_variable(arguments[1]):
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
                    for _var in [" A:", " B:", " C:"]:
                        processed_var = _var.replace(":", "").strip()
                        if _var in arg_func and processed_var in argument_variable_constraints:
                            variable_constraints[arg_variable] = argument_variable_constraints[processed_var]
                            break
                else:
                    arg_func_return_type = get_function_return_type(
                        arg_func[:arg_func.index("(")])
                    if arg_func_return_type is not None and arg_func_return_type not in ['*', 'bool']:
                        variable_constraints[arg_variable] = arg_func_return_type
    else:
        for argument, atype in zip(arguments, argument_types):
            if is_variable(argument):
                variable_constraints[argument] = atype
    
    # Rewrite, all functions/predicates except const, are only allowed to take variables as arguments
    rewrite_arguments = list()
    additional_lf = []
    for argument, atype in zip(arguments, argument_types):
        if is_variable(argument):
            rewrite_arguments.append(argument)
        else:
            match = ENTITY_PATTERN.match(argument.replace('"', ""))
            if match:
                e, et = process_entity_string(argument.replace('"', ""))
                new_variable = get_new_variable(global_variables)
                const_lf = 'const(%s,%s(%s))' % (new_variable, et, e.replace(" ", "_"))
                global_variables.add(new_variable)
                rewrite_arguments.append(new_variable)
            else:
                # TODO
                new_variable = get_new_variable(global_variables)
                const_lf = 'const_expr(%s,%s)' % (new_variable, argument.replace('"', ""))
                global_variables.add(new_variable)
                rewrite_arguments.append(new_variable)
            additional_lf.append(const_lf)
    resultant_lf = "%s(%s)" % (rewrite_function_name,
                               ",".join(rewrite_arguments))
    if len(additional_lf) > 0:
        additional_lf = ','.join(additional_lf)
        resultant_lf = resultant_lf + ',' + additional_lf

    # match pattern like: numerical_equals(D,A),const_expr(D,get_ground_fare(B))
    match = re.match(
        "numerical_equals\(([A-Z]),([A-Z])\),const_expr\(([A-Z]),(.*)\(([A-Z]),([A-Z])\)", resultant_lf)

    # less_than/larger_than
    comparative_pattern_1 = re.compile(
        "(larger_than|less_than)\(([A-Z]),([A-Z])\),const_expr\(([A-Z]),(.*)\(([A-Z]),[A-Z]\)\),const\(([A-Z]),(.*?)\((.*?)\)\)")
    comparative_pattern_match_1 = comparative_pattern_1.match(resultant_lf)

    # less_than/larger_than/equals
    comparative_pattern_2 = re.compile(
        "(larger_than|less_than)\(([A-Z]),([A-Z])\),const_expr\(([A-Z]),(.*)\),const_expr\(([A-Z]),(.*)\)")
    comparative_pattern_match_2 = comparative_pattern_2.match(resultant_lf)

    # equals pattern
    equal_pattern_1 = re.compile(
        "equals\(([A-Z]),([A-Z])\),const_expr\(([A-Z]),(.*)\),const_expr\(([A-Z]),(.*)\)")
    equal_pattern_match_1 = equal_pattern_1.match(resultant_lf)

    equal_pattern_2 = re.compile(
        "equals\(([A-Z]),([A-Z])\),const\(([A-Z]),(.+\(.+\))\),const_expr\(([A-Z]),(.*)\)")
    equal_pattern_match_2 = equal_pattern_2.match(resultant_lf)

    equal_pattern_3 = re.compile(
        "equals\(([A-Z]),([A-Z])\),const_expr\(([A-Z]),(.*)\)")
    equal_pattern_match_3 = equal_pattern_3.match(resultant_lf)

    if match is not None and (match[2] == match[3] or match[1] == match[3]):
        if match[2] == match[3]:
            new_var = match[1]
        else:
            new_var = match[2]
        predicate = match[4].replace("get_", "p_")
        predicate_var = match[5]
        resultant_lf = "%s(%s,%s)" % (predicate, predicate_var, new_var)
    elif comparative_pattern_match_1 and ((comparative_pattern_match_1[2] == comparative_pattern_match_1[4]
        and comparative_pattern_match_1[3] == comparative_pattern_match_1[7]) or \
            (comparative_pattern_match_1[2] == comparative_pattern_match_1[7] and \
                comparative_pattern_match_1[3] == comparative_pattern_match_1[4])):
        match = comparative_pattern_match_1
        entity_function = match[5]
        predicate_name = (match[1] + "_" + entity_function).replace("_get_", "_")
        subject_var = match[6]
        object_var = match[7]
        resultant_lf = "%s(%s,%s),const(%s,%s(%s))" % (predicate_name, subject_var, \
            object_var, object_var, match[8], match[9])
    elif comparative_pattern_match_2:
        print("Comparative Pattern 2")
        assert comparative_pattern_match_2[2] == comparative_pattern_match_2[4] and comparative_pattern_match_2[3] == comparative_pattern_match_2[6]
        first_entity_function = comparative_pattern_match_2[5]
        first_entity_predicate = first_entity_function[:first_entity_function.index('(')]
        assert is_entity_function(first_entity_predicate)
        index_1 = first_entity_function.index(',')
        first_entity_function_var = first_entity_function[index_1-1:index_1]
        first_remain_predicate = first_entity_function[first_entity_function.index(')')+1:]
        if first_remain_predicate.startswith(','):
            first_remain_predicate = first_remain_predicate[1:]

        second_entity_function = comparative_pattern_match_2[7]
        second_entity_predicate = second_entity_function[:second_entity_function.index('(')]
        assert is_entity_function(second_entity_predicate) and first_entity_predicate == second_entity_predicate
        index_2 = second_entity_function.index(',')
        second_entity_function_var = second_entity_function[index_2 - 1:index_2]
        second_remain_predicate = second_entity_function[second_entity_function.index(')') + 1:]
        if second_remain_predicate.startswith(','):
            second_remain_predicate = second_remain_predicate[1:]

        predicate_name = (comparative_pattern_match_2[1] + "_" + second_entity_predicate).replace("_get_", "_")

        resultant_lf = '%s(%s,%s)' % (predicate_name, first_entity_function_var, second_entity_function_var)
        if len(first_remain_predicate):
            resultant_lf += ',%s' % first_remain_predicate
        if len(second_remain_predicate):
            resultant_lf += ',%s' % second_remain_predicate

    elif equal_pattern_match_1:
        print("Equal Pattern 1")
        assert equal_pattern_match_1[1] == equal_pattern_match_1[3] \
               and equal_pattern_match_1[2] == equal_pattern_match_1[5]
        first_entity_function = equal_pattern_match_1[4]
        first_entity_predicate = first_entity_function[:first_entity_function.index('(')]
        assert is_entity_function(first_entity_predicate)
        index_1 = first_entity_function.index(',')
        first_entity_function_var = first_entity_function[index_1-1:index_1]
        first_remain_predicate = first_entity_function[first_entity_function.index(')')+1:]
        if first_remain_predicate.startswith(','):
            first_remain_predicate = first_remain_predicate[1:]

        second_entity_function = equal_pattern_match_1[6]
        second_entity_predicate = second_entity_function[:second_entity_function.index('(')]
        assert is_entity_function(second_entity_predicate) and first_entity_predicate == second_entity_predicate
        index_2 = second_entity_function.index(',')
        second_entity_function_var = second_entity_function[index_2 - 1:index_2]
        second_remain_predicate = second_entity_function[second_entity_function.index(')') + 1:]
        if second_remain_predicate.startswith(','):
            second_remain_predicate = second_remain_predicate[1:]

        predicate_name = ("equals_" + second_entity_predicate).replace("_get_", "_")

        resultant_lf = '%s(%s,%s)' % (predicate_name, first_entity_function_var, second_entity_function_var)
        if len(first_remain_predicate):
            resultant_lf += ',%s' % first_remain_predicate
        if len(second_remain_predicate):
            resultant_lf += ',%s' % second_remain_predicate

    elif equal_pattern_match_2:
        print("Equal Pattern 2")
        # Or the predicate
        assert equal_pattern_match_2[1] == equal_pattern_match_2[3] \
               and equal_pattern_match_2[2] == equal_pattern_match_2[5]

        second_entity_function = equal_pattern_match_2[6]
        second_entity_predicate = second_entity_function[:second_entity_function.index('(')]
        # assert is_entity_function(second_entity_predicate) or second_entity_predicate.startswith("argmin") \
        #         or second_entity_predicate.startswith("argmax")
        if is_entity_function(second_entity_predicate):
            index_2 = second_entity_function.index(',')
            second_entity_function_var = second_entity_function[index_2 - 1:index_2]
            second_remain_predicate = second_entity_function[second_entity_function.index(')') + 1:]
            if second_remain_predicate.startswith(','):
                second_remain_predicate = second_remain_predicate[1:]
        elif second_entity_predicate.startswith("argmin") \
                or second_entity_predicate.startswith("argmax"):
            index_2 = second_entity_function.index('(') + 1
            second_entity_function_var = second_entity_function[index_2:index_2 + 1]
            second_remain_predicate = second_entity_function
        else:
            # predicate
            # The first predicate is prediction function
            # TODO: to be more systematic
            # Assume that the first variable should be the primary variable
            lindex = second_entity_function.index('(')
            rindex = second_entity_function.index(')')
            predicate_arguments = second_entity_function[lindex:rindex].split(",")
            second_entity_function_var = predicate_arguments[0]
            for a in predicate_arguments:
                if is_variable(a):
                    second_entity_function_var = a
                    break
            second_remain_predicate = second_entity_function

        resultant_lf = 'equals(%s,%s),const(%s,%s)' % (equal_pattern_match_2[1],second_entity_function_var,
                                                       equal_pattern_match_2[3], equal_pattern_match_2[4])

        if len(second_remain_predicate) > 0:
            resultant_lf += ",%s" % second_remain_predicate

    elif equal_pattern_match_3:

        print("Equal Pattern 3")
        assert equal_pattern_match_3[2] == equal_pattern_match_3[3]
        entity_function = equal_pattern_match_3[4]
        entity_predicate = entity_function[:entity_function.index('(')]
        assert is_entity_function(entity_predicate) or entity_predicate.startswith("argmin") \
               or entity_predicate.startswith("argmax")
        if is_entity_function(entity_predicate):
            index_2 = entity_predicate.index(',')
            entity_function_var = entity_predicate[index_2 - 1:index_2]
            remain_predicate = entity_predicate[entity_predicate.index(')') + 1:]
            if remain_predicate.startswith(','):
                remain_predicate = remain_predicate[1:]
        else:
            index_2 = entity_function.index('(') + 1
            entity_function_var = entity_function[index_2:index_2 + 1]
            remain_predicate = entity_function

        resultant_lf = 'equals(%s,%s)' % (equal_pattern_match_3[1],entity_function_var)
        if len(remain_predicate) > 0:
            resultant_lf += ",%s" % remain_predicate

    elif is_entity_function(rewrite_function_name) and number_of_arguments == 1:
        print("Entity Function")
        # Entity Function
        # Check if it is entity_function
        pattern = re.compile("%s\(([A-Z])\),const_expr\(([A-Z]),(.*)\)" % rewrite_function_name)
        pattern_1_match = pattern.match(resultant_lf)
        pattern_2 = re.compile(
            "%s\(([A-Z])\),const\(([A-Z]),(.*)\)" % rewrite_function_name)
        pattern_2_match = pattern_2.match(resultant_lf)
        pattern_3 = re.compile(
            "%s\(([A-Z])\)" % rewrite_function_name)
        pattern_3_match = pattern_3.match(resultant_lf)
        if pattern_1_match is not None and pattern_1_match[1] == pattern_1_match[2]:
            print("Match Pattern 1")
            match = pattern_1_match
            entity_variable, predicate_function = match[1], match[3]
            if predicate_function.startswith('(') and predicate_function.endswith(')'):
                predicate_function = predicate_function[1:-1]
            first_predicate = predicate_function[:predicate_function.index("(")]
            print(first_predicate, is_entity_function(first_predicate))
            if is_entity_function(first_predicate):
                rindex = predicate_function.index(')')
                ref_variable = predicate_function[rindex - 1:rindex]
                new_var = get_new_variable(global_variables)
                resultant_lf = '%s(%s,%s),%s' % (
                    rewrite_function_name, ref_variable, new_var, predicate_function)
                global_variables.add(new_var)
            elif first_predicate.startswith("argmin") or first_predicate.startswith("argmax"):
                index = len(first_predicate)
                ref_variable = predicate_function[index + 1:index + 2]
                new_var = get_new_variable(global_variables)
                resultant_lf = '%s(%s,%s),%s' % (
                    rewrite_function_name, ref_variable, new_var, predicate_function)
                global_variables.add(new_var)
            else:
                # The first predicate is prediction function
                # TODO: to be more systematic
                # Assume that the first variable should be the primary variable
                rindex = predicate_function.index('(')
                ref_variable = predicate_function[rindex + 1:rindex+2]
                new_var = get_new_variable(global_variables)
                resultant_lf = '%s(%s,%s),%s' % (
                    rewrite_function_name, ref_variable, new_var, predicate_function)
                print("Match Predicate")
                print(resultant_lf, ref_variable)
                global_variables.add(new_var)
        elif pattern_2_match is not None and pattern_2_match[1] == pattern_2_match[2]:
            print("Match Pattern 2")
            match = pattern_2_match
            # Simple Entity function
            new_var = get_new_variable(global_variables)
            index = resultant_lf.index(')')
            resultant_lf = resultant_lf[:index] + ",%s" % new_var + resultant_lf[index:]
            global_variables.add(new_var)
        else:
            assert pattern_3_match is not None
            print("Match Pattern 3")
            # Simple Entity function
            new_var = get_new_variable(global_variables)
            index = resultant_lf.index(')')
            resultant_lf = resultant_lf[:index] + ",%s" % new_var + resultant_lf[index:]
            global_variables.add(new_var)

    return resultant_lf, variable_constraints


class Node:
    def __init__(self, lf, lidx, ridx, variable_type_constraints):
        self.lf = lf
        self.lidx = lidx
        self.ridx = ridx
        self.variable_type_constraints = variable_type_constraints


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
    normalized_lf = normalized_lf.replace('$v0:e ', 'A ')
    normalized_lf = normalized_lf.replace('$v1:e ', 'B ')
    normalized_lf = normalized_lf.replace('$v2:e ', 'C ')
    normalized_lf = normalized_lf.replace('$v3:e ', 'D ')
    normalized_lf = normalized_lf.replace('$v0:i ', 'A ')
    normalized_lf = normalized_lf.replace('$v1:i ', 'B ')
    normalized_lf = normalized_lf.replace('$v2:i ', 'C ')
    normalized_lf = normalized_lf.replace('$v3:i ', 'D ')
    normalized_lf = normalized_lf.replace('$v0', 'A')
    normalized_lf = normalized_lf.replace('$v1', 'B')
    normalized_lf = normalized_lf.replace('$v2', 'C')
    normalized_lf = normalized_lf.replace('$v3', 'D')
    normalized_lf = re.sub(' +', ' ', normalized_lf)

    # Translate
    if normalized_lf.count('(') == 0:
        # Simple Cases, A single entity
        entity_name, entity_type = extract_entity(normalized_lf)
        prolog = 'answer(A,(const(A,%s(%s))))' % (
            ENTITY_TYPE_MAP[entity_type], entity_name)
    else:
        left_brackets = list()
        # original_lf = copy.deepcopy(python_lf)
        tokens = tokenize_logical_form(normalized_lf)
        global_variable_set = {token for token in tokens if token in {'A', 'B', 'C', 'D'}}
        global_variable_constraints = dict()
        answer_variable_set = set()

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

                # Rewrite
                # Prolog has a very plat structure
                if len(children_nodes) == 0:
                    sub_tokens = tokens[pidx + 1:tidx]
                    function_name = sub_tokens[0]
                    number_of_arguments = len(sub_tokens[1:])
                    rewritten_lf, node_variable_type_constraints = rewrite(function_name, number_of_arguments,
                                                                           sub_tokens[1:], global_variable_constraints,
                                                                           global_variable_set)
                else:
                    # Has children
                    sub_tokens = tokens[pidx + 1:tidx]
                    function_name = sub_tokens[0]
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
                        node_variable_type_constraints = copy.deepcopy(
                            child_node.variable_type_constraints)
                        answer_variable_set.add(variable)
                        rewritten_lf = child_node.lf
                    elif function_name in ['_argmin', '_argmax', '_sum']:
                        assert len(other_children) == 1 and len(
                            children_nodes) == 2
                        variable = other_children.pop(0)
                        node_1, node_2 = children_nodes.pop(
                            0), children_nodes.pop(0)
                        update_variable_type_constraints(node_variable_type_constraints, node_1.variable_type_constraints)
                        update_variable_type_constraints(node_variable_type_constraints, node_2.variable_type_constraints)
                        # Arg max/min entity function
                        entity_function = node_2.lf[:node_2.lf.index('(')]
                        predicate_name = "%s_%s" % (function_name[1:], entity_function)
                        rewritten_lf = "%s(%s,%s)" % (
                            predicate_name, variable, node_1.lf)
                    elif function_name == '_count':
                        assert len(other_children) == 1 and len(children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        update_variable_type_constraints(
                            node_variable_type_constraints, child_node.variable_type_constraints)
                        # print(node_variable_type_constraints, variable)
                        new_variable = get_new_variable(global_variable_set)
                        rewritten_lf = "count(%s,(%s),%s)" % (
                            variable, child_node.lf, new_variable)
                        global_variable_set.add(new_variable)
                    elif function_name in ['_exists', '_the']:
                        assert len(other_children) == 1 and len(
                            children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        update_variable_type_constraints(
                            node_variable_type_constraints, child_node.variable_type_constraints)
                        rewritten_lf = "%s" % child_node.lf
                    elif function_name in ['_max', '_min']:
                        assert len(other_children) == 1 and len(
                            children_nodes) == 1
                        variable = other_children.pop(0)
                        child_node = children_nodes.pop(0)
                        update_variable_type_constraints(
                            node_variable_type_constraints, child_node.variable_type_constraints)

                        child_lf = child_node.lf
                        # replace
                        # pattern = '(numerical_equals\((.*?),%s\),const_expr\((.*?),(.*?\))\))' % variable
                        # results = re.findall(pattern, child_lf)
                        # assert len(results) == 1
                        # results = results[0]
                        # assert results[1] == results[2]

                        # child_lf = child_lf.replace(results[0], "true")
                        # entity_function = results[3][:results[3].index('(')]
                        # predicate_name = "%s_%s" % (
                        #     function_name[1:], entity_function)
                        # # numerical_function = "%s(%s,(%s))" % (
                        # #     predicate_name, variable, child_lf)

                        rewritten_lf = "%s(%s,%s)" % (
                            function_name, variable, child_lf)
                    elif function_name in ['_and', '_or']:
                        for position in children_position:
                            if position == 'bracket':
                                n = children_nodes.pop(0)
                                string.append(n.lf)
                                update_variable_type_constraints(
                                    node_variable_type_constraints, n.variable_type_constraints)
                            else:
                                sub_token = other_children.pop(0)
                                string.append(sub_token)
                        if function_name == '_and':
                            rewritten_lf = "(%s)" % (','.join(string))
                        else:
                            rewritten_lf = "or(%s)" % (','.join(string))
                    elif function_name == '_not':
                        for position in children_position:
                            if position == 'bracket':
                                n = children_nodes.pop(0)
                                string.append(n.lf)
                                update_variable_type_constraints(
                                    node_variable_type_constraints, n.variable_type_constraints)
                            else:
                                sub_token = other_children.pop(0)
                                string.append(sub_token)
                        rewritten_lf = "not(%s)" % (','.join(string))
                    else:
                        for position in children_position:
                            if position == 'bracket':
                                n = children_nodes.pop(0)
                                string.append(n.lf)
                                update_variable_type_constraints(node_variable_type_constraints, n.variable_type_constraints)
                            else:
                                sub_token = other_children.pop(0)
                                string.append(sub_token)
                        rewritten_lf, variable_type_constraints = rewrite(
                            function_name, children_num, string,
                            global_variable_constraints, global_variable_set)
                        # Update variable constraints
                        update_variable_type_constraints(node_variable_type_constraints, variable_type_constraints)
                new_node = Node(
                    rewritten_lf, pidx, tidx, node_variable_type_constraints)
                global_variable_constraints.update(node_variable_type_constraints)
                # print(node_variable_type_constraints)
                nodes.append(new_node)
            else:
                if tidx > 0 and (not tokens[tidx - 1] == '(') and ":_" in token:
                    # token is not function name
                    tokens[tidx] = '"%s"' % tokens[tidx]
        assert len(nodes) == 1
        prolog_variable_type_constraints = nodes[0].variable_type_constraints
        prolog = nodes[0].lf

        if len(answer_variable_set) > 0:
            prefix = "%s" % len(answer_variable_set)
            prolog = "answer_%s(%s,%s)" % (prefix,
                                           ','.join(sorted(answer_variable_set)), prolog)
        elif is_entity_function(prolog[:prolog.index('(')]):
            index = prolog.index(')')
            answer_var = prolog[index - 1:index]
            prolog = "answer_1(%s,(%s))" % (answer_var,prolog)
        elif prolog.startswith('argmin') or prolog.startswith('argmax') \
                or prolog.startswith('_min') or prolog.startswith('_max'):
            index = prolog.index('(') + 1
            answer_var = prolog[index:index+1]
            prolog = "answer_1(%s,(%s))" % (answer_var, prolog)
        elif prolog.startswith('count'):
            index = prolog.rindex(')')
            answer_var = prolog[index-1:index]
            prolog = "answer_1(%s,(%s))" % (answer_var, prolog)
        else:
            print("Fail to translate to prolog")

    return prolog


if __name__ == '__main__':
    questions, logical_forms = read_data(
        './atis_lambda_test.tsv')

    sorted_logical_forms = sorted([(q,lf,) for q, lf in zip(questions, logical_forms)], key=lambda x: len(x[1]))
    # with open("atis_prolog_test.log", "w") as f:
    for lidx, (question, lf) in enumerate(sorted_logical_forms):
        print(lidx)
        print(question)
        print(lf)
        normalized_lf = transform_lambda_calculus(lf)
        print(normalized_lf)
        print("===\n\n")
        # f.write("%s\n%s\n%s\n===\n\n" % (question, lf, normalized_lf))


