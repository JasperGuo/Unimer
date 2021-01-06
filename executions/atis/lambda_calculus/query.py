# coding=utf8

import sys
sys.path += ['..']
import re
import mysql.connector
from pprint import pprint

db = None


def normalize(sql):
    s = re.sub(' +', ' ', sql)
    s = s.replace('MAX (', 'MAX(')
    s = s.replace('MIN (', 'MIN(')
    s = s.replace('AVG (', 'AVG(')
    s = s.replace('COUNT (', 'COUNT(')
    s = s.replace('count (', 'count(')
    s = s.replace('SUM (', 'SUM(')
    s = s.replace('< =', '<=')
    s = s.replace('> =', '>=')
    return s


def format_headers(header):
    s = header.replace("( ", "(").replace(" )", ")").strip().lower()
    return s


def get_connection():
    global db
    if db and db.is_connected():
        return db
    else:
        db = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="123456",
                database="atis",
                auth_plugin='mysql_native_password'
            )
        return db


def close_connection():
    if db is not None and db.is_connected():
        db.close()


def get_result(sql):
    db = get_connection()
    _sql = normalize(sql)
    cursor = db.cursor()
    cursor.execute(_sql)
    # print(cursor.description)
    headers = cursor.description
    results = cursor.fetchall()
    formatted_results = list()
    for x in results:
        r = dict()
        for value, header in zip(x, headers):
            r[format_headers(header[0])] = value
        formatted_results.append(r)
    # pprint(formatted_results)
    return formatted_results


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
    "bat": "basis_type"
}

# Entity Set
def get_all_flight_ids():
    sql = "SELECT distinct flight_id FROM flight"
    return get_result(sql)


def get_all_city_names():
    sql = "SELECT distinct city_name FROM city"
    return get_result(sql)


def get_all_airline_codes():
    sql = "SELECT distinct airline_code FROM airline"
    return get_result(sql)


def get_all_aircraft_codes():
    sql = "SELECT distinct aircraft_code FROM aircraft"
    return get_result(sql)


def get_all_airport_codes():
    sql = "SELECT distinct airport_code FROM airport"
    return get_result(sql)


def get_all_booking_class_descriptions():
    sql = "SELECT distinct class_description FROM class_of_service"
    return get_result(sql)


def get_all_transport_types():
    sql = "SELECT distinct transport_type FROM ground_service"
    return get_result(sql)


def get_all_meal_codes():
    sql = "SELECT distinct meal_code FROM food_service"
    return get_result(sql)


def get_all_meal_descriptions():
    sql = "SELECT distinct meal_description FROM food_service"
    return get_result(sql)


def get_all_fare_basis_codes():
    sql = "SELECT distinct fare_basis_code FROM fare_basis"
    return get_result(sql)


def get_all_time_zone_codes():
    sql = "SELECT distinct time_zone_code FROM time_zone"
    return get_result(sql)


def get_all_one_direction_cost():
    sql = "SELECT distinct one_direction_cost FROM fare"
    return get_result(sql)


def get_all_capacity():
    sql = "SELECT distinct capacity FROM aircraft"
    return get_result(sql)


def get_all_flight_number():
    sql = "SELECT distinct flight_number FROM flight"
    return get_result(sql)


def get_all_departure_time():
    sql = "SELECT distinct departure_time FROM flight"
    return get_result(sql)


def get_all_stop_arrival_time():
    sql = "SELECT distinct arrival_time FROM flight_stop"
    return get_result(sql)


def process_entity_string(entity, default=""):
    if isinstance(entity, str):
        if ":_" in entity:
            splits = entity.split(":_")
            entity_name = splits[0]
            entity_type = ENTITY_TYPE_MAP[splits[1]]
        else:
            entity_type = default
            entity_name = entity
        if '_' in entity_name:
            entity_name = entity_name.replace("_", " ")
    elif isinstance(entity, dict):
        key = list(entity.keys())[0]
        entity_type = key
        entity_name = entity[key]
    elif isinstance(entity, list) and len(entity) > 0:
        # TODO: simply take the first one
        key = list(entity[0].keys())[0]
        entity_type = key
        entity_name = entity[0][key]
    else:
        raise Exception("Invalid Entity Type %s" % str(entity))
    if entity_type == 'city_name':
        if entity_name == 'st louis':
            entity_name = 'st. louis'
        elif entity_name == 'st petersburg':
            entity_name = 'st. petersburg'
        elif entity_name == 'st paul':
            entity_name = 'st. paul'
    return entity_name, entity_type


# Entity
def fb(entity):
    """
    fare basis
    """
    sql = "SELECT DISTINCT fare_basis_1.fare_basis_code FROM fare_basis fare_basis_1 WHERE fare_basis_1.fare_basis_code = '%s'" % (entity)
    return get_result(sql)


def rc(entity):
    """
    Meal code
    """
    sql = "SELECT DISTINCT food_service_1.meal_description FROM food_service food_service_1 WHERE food_service_1.meal_code = '%s'" % (entity)
    return get_result(sql)


def dc(entity):
    """
    day name
    """
    sql = "SELECT DISTINCT days_1.day_name FROM days days_1 WHERE days_1.days_code = '%s'" % (entity)
    return get_result(sql)


def al(entity):
    """
    airline code
    """
    sql = "SELECT DISTINCT airline_1.airline_code FROM airline airline_1 WHERE airline_1.airline_code = '%s'" % (
        entity)
    return get_result(sql)


def ap(entity):
    """
    airport code
    """
    sql = "SELECT DISTINCT airport_1.airport_code FROM airport airport_1 WHERE airport_1.airport_code = '%s'" % (entity)
    return get_result(sql)


def ac(entity):
    """
    aircraft code
    """
    sql = "SELECT DISTINCT aircraft_1.aircraft_code FROM aircraft aircraft_1 WHERE aircraft_1.aircraft_code = '%s'" % (entity)
    return get_result(sql)


def ci(city_name):
    """
    city_name
    return city_code
    """
    entity_name, _ = process_entity_string(city_name)
    sql = "SELECT DISTINCT city_code FROM city WHERE city_name = '%s'" % (
        entity_name)
    return get_result(sql)


def abbrev(entity):
    """
    abbrev of airline_code
    """
    entity_name, entity_type = process_entity_string(entity)
    sql = "SELECT DISTINCT airline_1.airline_code FROM airline airline_1 WHERE airline_1.airline_name like '%" + entity_name + "%'"
    results = get_result(sql)
    print(results)
    if len(results) == 1:
        return results[0]
    return results


def capacity(argument):
    """
    return airline
    """
    if isinstance(argument, str):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        assert isinstance(argument, dict)
        entities = [argument]
    results = list()
    flight_number_template = "SELECT aircraft_1.capacity FROM aircraft as aircraft_1 JOIN flight as flight_1 on aircraft_1.aircraft_code = flight_1.aircraft_code_sequence WHERE flight_1.flight_number = %s;"
    flight_id_template = "SELECT aircraft_1.capacity FROM aircraft as aircraft_1 JOIN flight as flight_1 on aircraft_1.aircraft_code = flight_1.aircraft_code_sequence WHERE flight_1.flight_id = %s;"
    aircraft_code_template = "SELECT DISTINCT aircraft_1.capacity FROM aircraft aircraft_1 WHERE aircraft_1.aircraft_code = '%s'"
    for e in entities:
        entity_name, entity_type = process_entity_string(e, "aircraft_code")
        if entity_type == 'aircraft_code':
            sql = aircraft_code_template % entity_name
        elif entity_type == 'flight_id':
            # flight id
            sql = flight_id_template % entity_name
        else:
            # entity_type == 'flight_number':
            sql = flight_number_template % entity_name
        results += get_result(sql)
    return results


def flight_number(argument):
    """
    Return flight number 
    _flight_number(_argmin((lambda x: _and(_flight(x),_from(x,"boston:_ci"),_to(x,"washington:_ci"))),(lambda x: _departure_time(x))))
    """
    if isinstance(argument, str):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        assert isinstance(argument, dict)
        entities = [argument]
    results = list()
    sql_template = "SELECT flight_number FROM flight WHERE flight_id = %s"
    for e in entities:
        entity_name, _ = process_entity_string(e, "flight_id")
        sql = sql_template % entity_name
        results += get_result(sql)
    return results


def get_flight_destination(flight_id):
    """
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT to_airport FROM flight WHERE flight_id = %s" % processed_flight_id
    results = get_result(sql)
    return results


def get_flight_fare(flight_id):
    """
    _fare $1
    :entity_type: flight_id
    """
    if flight_id is None or (isinstance(flight_id, list) and len(flight_id) == 0):
        return None
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = "SELECT fare.one_direction_cost FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE flight.flight_id = %s" % (processed_flight_id)
    results = get_result(sql)
    return results


def get_flight_cost(flight_id):
    """
    _cost $1
    :entity_type: flight_id
    """
    if flight_id is None or (isinstance(flight_id, list) and len(flight_id) == 0):
        return None
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = "SELECT fare.round_trip_cost FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE flight.flight_id = %s" % (processed_flight_id)
    results = get_result(sql)
    return results


def get_booking_class_fare(class_description):
    """
    _fare $1
    :entity_type: flight_id
    """
    processed_class_description, entity_type = process_entity_string(
        class_description, "class_description")
    sql = "SELECT fare.one_direction_cost FROM fare JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE class_of_service.class_description = '%s'" % (
        processed_class_description)
    results = get_result(sql)
    return results


def airline_name(argument):
    """
    _airline_name
    """
    if isinstance(argument, str):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        assert isinstance(argument, dict)
        entities = [argument]
    sql_tempalte = "SELECT airline_name FROM flight JOIN airline ON flight.airline_code = airline.airline_code WHERE flight.flight_id = %s"
    results = list()
    for e in entities:
        entity_name, entity_type = process_entity_string(e, "aircraft_code")
        sql = sql_tempalte % entity_name
        results += get_result(sql)
    return results


def departure_time(argument):
    """
    _departure_time
    """
    if argument is None:
        return None
    if isinstance(argument, str):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        assert isinstance(argument, dict)
        entities = [argument]
    sql_tempalte = "SELECT departure_time FROM flight WHERE flight_id = %s"
    results = list()
    for e in entities:
        entity_name, entity_type = process_entity_string(e, "flight_id")
        sql = sql_tempalte % entity_name
        results += get_result(sql)
    return results


def arrival_time(argument):
    """
    _arrival_time
    """
    if isinstance(argument, str):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        assert isinstance(argument, dict)
        entities = [argument]
    sql_tempalte = "SELECT arrival_time FROM flight WHERE flight_id = %s"
    results = list()
    for e in entities:
        entity_name, entity_type = process_entity_string(e, "flight_id")
        sql = sql_tempalte % entity_name
        results += get_result(sql)
    return results


def miles_distant(airport_code, city_name):
    """
    _miles_distant
    :entity_type: (airport_code, city_name)
    """
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    sql = "SELECT airport_service.miles_distant FROM airport_service JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = '%s' AND airport_service.airport_code = '%s'" % (
        processed_city_name, processed_airport_code)
    return get_result(sql)


def miles_distant_between_city(city_name_1, city_name_2):
    """
    _miles_distant
    :entity_type: (city_name, city_name)
    """
    processed_city_name_1, _ = process_entity_string(
        city_name_1, "city_name")
    processed_city_name_2, _ = process_entity_string(
        city_name_2, "city_name_2")
    sql = "SELECT distinct airport_service.miles_distant FROM airport_service JOIN city ON airport_service.city_code = city.city_code WHERE city.city_name = '%s' AND airport_service.airport_code IN (SELECT T1.airport_code FROM airport_service AS T1 JOIN city AS T2 ON T1.city_code = T2.city_code WHERE T2.city_name = '%s');" % (
        processed_city_name_1, processed_city_name_2)
    return get_result(sql)


def minimum_connection_time(airport_code):
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT DISTINCT airport_1.minimum_connect_time FROM airport airport_1 WHERE airport_1.airport_code = '%s'" % (processed_airport_code)
    return get_result(sql)


def get_number_of_stops(flight_id):
    """
    _stops(x)
    :entity_type flight_id
    """
    if isinstance(flight_id, list) and len(flight_id) == 0:
        return list()
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = "SELECT stops FROM flight WHERE flight.flight_id = %s" % (
        processed_flight_id)
    return get_result(sql)


def time_elapsed(flight_id):
    """
    _time_elapsed(x)
    :entity_type flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT time_elapsed FROM flight WHERE flight_id = %s" % processed_flight_id
    return get_result(sql)


def get_flight_aircraft_code(flight_id):
    """
    _aircraft_code $1
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = "SELECT aircraft_code FROM flight JOIN equipment_sequence AS T ON flight.aircraft_code_sequence = T.aircraft_code_sequence WHERE flight.flight_id = %s" % processed_flight_id
    return get_result(sql)


def get_flight_airline_code(flight_id):
    """
    _airline:_e $1
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = "SELECT airline_code FROM flight WHERE flight.flight_id = %s" % processed_flight_id
    return get_result(sql)


def get_flight_booking_class(flight_id):
    """
    _booking_class $1
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT class_of_service.class_description FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE flight_fare.flight_id = %s" % processed_flight_id
    return get_result(sql)


def get_flight_meal(flight_id):
    """
    _meal $1
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT food_service.meal_description FROM flight JOIN food_service ON flight.meal_code = food_service.meal_code WHERE flight_id = %s" % (
        processed_flight_id)
    return get_result(sql)


def get_flight_stop_airport(flight_id):
    """
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight_stop.stop_airport FROM flight_stop WHERE flight_stop.flight_id = %s" % (
        processed_flight_id)
    return get_result(sql)


def get_ground_fare(transport_type):
    """
    _ground_fare $1
    :entity_type (transport_type)
    """
    processed_transport_type, _ = process_entity_string(
        transport_type, "transport_type")
    sql = "SELECT ground_fare FROM ground_service WHERE transport_type = '%s'" % (
        processed_transport_type)
    return get_result(sql)


def get_ground_fare_1(city_name, transport_type):
    """
    _ground_fare $1
    :entity_type (city_name, transport_type)
    """
    processed_transport_type, _ = process_entity_string(
        transport_type, "transport_type")
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    sql = "SELECT ground_fare FROM ground_service JOIN city ON ground_service.city_code = city.city_code WHERE city.city_name = '%s' AND transport_type = '%s'" % (
        processed_city_name, processed_transport_type)
    return get_result(sql)


def get_ground_fare_2(airport_code, transport_type):
    """
    _ground_fare $1
    :entity_type (airport_code, transport_type)
    """
    processed_transport_type, _ = process_entity_string(
        transport_type, "transport_type")
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT ground_fare FROM ground_service WHERE airport_code = '%s' AND transport_type = '%s'" % (
        processed_airport_code, processed_transport_type)
    return get_result(sql)


def get_ground_fare_3(city_name, airport_code, transport_type):
    """
    _ground_fare $1
    :entity_type (city_name, airport_code, transport_type)
    """
    processed_transport_type, _ = process_entity_string(
        transport_type, "transport_type")
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT ground_fare FROM ground_service JOIN city ON ground_service.city_code = city.city_code WHERE city.city_name = '%s' AND airport_code = '%s' AND transport_type = '%s'" % (
        processed_city_name, processed_airport_code, processed_transport_type)
    return get_result(sql)


def get_minutes_distant_1(city_name):
    """
    :entity_type (city_name)
    """
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    sql = "SELECT minutes_distant FROM airport_service JOIN city ON airport_service.city_code = city.city_code WHERE city.city_name = '%s'" % (
        processed_city_name)
    return get_result(sql)


def get_minutes_distant_2(airport_code):
    """
    :entity_type (airport_code)
    """
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT minutes_distant FROM airport_service WHERE airport_code = '%s'" % (
        processed_airport_code)
    return get_result(sql)


def get_minutes_distant_3(city_name, airport_code):
    """
    :entity_type (city_name, airport_code)
    """
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT minutes_distant FROM airport_service JOIN city ON airport_service.city_code = city.city_code WHERE city.city_name = '%s' AND airport_code = '%s'" % (
        processed_city_name, processed_airport_code)
    return get_result(sql)


def get_flight_stop_arrival_time(flight_id):
    """
    _stop_arrival_time $0
    :entity_type flight_id
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    sql = "SELECT flight_stop.arrival_time, city.city_name FROM flight_stop JOIN airport_service ON flight_stop.stop_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE flight_stop.flight_id = %s" % (processed_flight_id)
    return get_result(sql)


def get_flight_restriction_code(flight_id):
    """
    _restriction_code $0
    :entity_type flight_id
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    sql = "SELECT restriction.restriction_code FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN restriction ON fare.restriction_code = restriction.restriction_code WHERE flight_fare.flight_id = %s" % (processed_flight_id)
    return get_result(sql)


# Binary Predicate
def is_mf(entity, manufacturer):
    """
    :_mf
    mf(x,"boeing:_mf")
    """
    return True


def is_flight_manufacturer(flight_id, manufacturer):
    """
    _manufacturer(x,"boeing:_mf")
    :entity_type (flight_id, manufacturer)
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_manufacturer, entity_type = process_entity_string(
        manufacturer, "manufacturer")
    sql = "SELECT flight.flight_id FROM flight JOIN aircraft ON flight.aircraft_code_sequence = aircraft.aircraft_code WHERE aircraft.manufacturer = '%s' AND flight.flight_id = %s" % (processed_manufacturer, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_services(airline_code, city_name):
    """
    _services(x,y)
    """
    processed_airline_code, _ = process_entity_string(airline_code, "airline_code")
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    sql = "SELECT flight_id FROM flight JOIN airport_service ON flight.to_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = '%s' AND flight.airline_code = '%s'" % (
        processed_city_name, processed_airline_code)
    results = get_result(sql)
    return len(results) > 0


def is_airline_services(airline_code, airport_code):
    """
    _services ff:_al $x
    :entity_type: (airline_code, airport_code)
    """
    processed_airline_code, _ = process_entity_string(airline_code, "airline_code")
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT DISTINCT flight.to_airport FROM flight WHERE flight.to_airport = '%s' AND flight.airline_code  =  '%s'" % (
        processed_airport_code, processed_airline_code)
    results = get_result(sql)
    return len(results) > 0


def is_to(flight_id, entity):
    """
    _to(x,"mke:_ap"/"indianapolis:_ci")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    entity, entity_type = process_entity_string(entity, "airport_code")
    if entity_type == 'airport_code':
        sql = "SELECT flight_id FROM flight WHERE flight.flight_id = %s AND flight.to_airport = '%s'" % (
            processed_flight_id, entity)
    elif entity_type == 'city_name':
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.to_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE city_1.city_name = '%s' AND flight_1.flight_id = %s" % (
            entity, processed_flight_id)
    else:
        # entity_type == 'state_name':
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.to_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code JOIN state ON city_1.state_code = state.state_code WHERE state.state_name = '%s' AND flight_1.flight_id = %s" % (
            entity, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_from(flight_id, entity):
    """
    _from(x,"mke:_ap"/"indianapolis:_ci")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    entity, entity_type = process_entity_string(entity, "airport_code")
    if entity_type == 'airport_code':
        sql = "SELECT flight_id FROM flight WHERE flight.flight_id = %s AND flight.from_airport = '%s'" % (
            processed_flight_id, entity)
    else:
        # entity_type == 'city_name'
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.from_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE city_1.city_name = '%s' AND flight_1.flight_id = %s" % (
            entity, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_loc_t(airport_code, city_name):
    """
    _loc:_t(airport_code,city_name)
    :entity_type (airport_code, city_name)
    """
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    processed_city_name, _ = process_entity_string(
        city_name, "city_name")
    sql = "SELECT * FROM airport_service AS T JOIN city ON T.city_code = city.city_code WHERE city.city_name = '%s' AND T.airport_code = '%s';" % (
        processed_city_name, processed_airport_code)
    results = get_result(sql)
    return len(results) > 0


def is_loc_t_state(airport_code, state_name):
    """
    _loc:_t(airport_code,state_name)
    :entity_type (airport_code, state_name)
    """
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    processed_state_name, _ = process_entity_string(
        state_name, "state_name")
    sql = "SELECT * FROM airport_service AS T JOIN city ON T.city_code = city.city_code JOIN state ON city.state_code = state.state_code WHERE state.state_name = '%s' AND T.airport_code = '%s';" % (
        processed_state_name, processed_airport_code)
    results = get_result(sql)
    return len(results) > 0


def is_loc_t_city_time_zone(city_name, time_zone_code):
    """
    _loc:_t(city_name,time_zone_code)
    :entity_type (city_name, time_zone_code)
    """
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    processed_time_zone_code, _ = process_entity_string(
        time_zone_code, "time_zone_code")
    sql = "SELECT city_name FROM city WHERE city_name = '%s' AND time_zone_code = '%s'" % (
        processed_city_name, processed_time_zone_code)
    results = get_result(sql)
    return len(results) > 0


def is_from_airport(transport_way, entity):
    """
    Transport Type
    _from_airport(x,"toronto:_ci"/"pit:_ap")
    """
    processed_transport_way, _ = process_entity_string(transport_way, "transport_type")
    entity_name, entity_type = process_entity_string(entity)
    airport_code_template = "SELECT DISTINCT ground_service_1.transport_type FROM ground_service ground_service_1 WHERE ground_service_1.airport_code = '%s' AND ground_service_1.transport_type = '%s'"
    if entity_type == 'city_name':
        sql = city_name_template % (entity_name, processed_transport_way)
    else:
        # entity_type == 'airport_code'
        sql = airport_code_template % (entity_name, processed_transport_way)
    results = get_result(sql)
    return len(results) > 0


def is_from_airports_of_city(transport_way, city_name):
    """
    Transport Type
    _from_airport(x,"toronto:_ci"/"pit:_ap")
    """
    processed_transport_way, _ = process_entity_string(transport_way, "transport_type")
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    sql = "SELECT DISTINCT T3.transport_type FROM airport_service AS T1 JOIN city AS T2 ON T1.city_code = T2.city_code JOIN ground_service AS T3 ON T1.airport_code = T3.airport_code WHERE T2.city_name = '%s' AND T3.transport_type = '%s'" % (
        processed_city_name, processed_transport_way
    )
    results = get_result(sql)
    return len(results) > 0


def is_to_city(transport_way, city_name):
    """
    Transport Type
    _to_city(x,"boston:_ci")
    """
    processed_transport_way, _ = process_entity_string(
        transport_way, "transport_type")
    entity_name, entity_type = process_entity_string(city_name)
    assert entity_type == 'city_name'
    sql = "SELECT DISTINCT ground_service_1.transport_type FROM ground_service AS ground_service_1 JOIN city AS city_1 ON ground_service_1.city_code = city_1.city_code WHERE city_1.city_name = '%s' AND ground_service_1.transport_type = '%s'" % (
        entity_name, processed_transport_way)
    results = get_result(sql)
    return len(results) > 0


def is_flight_airline(flight_id, airline_code):
    """
    _airline(x,"dl:_al")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_airline_code, _ = process_entity_string(airline_code, "airline_code")
    sql = "SELECT flight_id FROM flight WHERE flight_id = %s AND airline_code = '%s'" % (
        processed_flight_id, processed_airline_code)
    results = get_result(sql)
    return len(results) > 0


def is_aircraft_airline(aircraft_code, airline_code):
    """
    _airline(x,"dl:_al")
    """
    processed_aircraft_code, _ = process_entity_string(
        aircraft_code, "aircraft_code")
    processed_airline_code, _ = process_entity_string(
        airline_code, "airline_code")
    sql = "SELECT aircraft_code_sequence FROM flight WHERE aircraft_code_sequence = '%s' AND airline_code = '%s'" % (
        processed_aircraft_code, processed_airline_code)
    results = get_result(sql)
    return len(results) > 0


def is_aircraft_basis_type(aircraft_code, basis_type):
    """
    _basis_type(x,"737:_bat")
    :entity_type: (aircraft_code, basis_type)
    """
    processed_aircraft_code, _ = process_entity_string(
        aircraft_code, "aircraft_code")
    processed_basis_type, _ = process_entity_string(
        basis_type, "basis_type")
    sql = "SELECT aircraft_code FROM aircraft WHERE aircraft_code = '%s' AND basic_type = '%s'" % (
        processed_aircraft_code, processed_basis_type)
    results = get_result(sql)
    return len(results) > 0


def is_flight_number(flight_id, flight_number):
    """
    _flight_number(x,"201:_fn")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_flight_number, _ = process_entity_string(
        flight_number, "flight_number")
    sql = "SELECT flight_id FROM flight WHERE flight_id = %s AND flight_number = '%s'" % (
        processed_flight_id, processed_flight_number)
    results = get_result(sql)
    return len(results) > 0


def is_flight_stop_at_city(flight_id, city_name):
    """
    _stop(x,"denver:_ci")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_city_name, _ = process_entity_string(
        city_name, "city_name")
    sql = "SELECT flight.flight_id FROM flight JOIN flight_stop ON flight.flight_id = flight_stop.flight_id JOIN airport_service ON flight_stop.stop_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = '%s' AND flight.flight_id = %s" % (
        processed_city_name, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_stop_at_airport(flight_id, airport_code):
    """
    _stop(x,"denver:_ci")
    :entity_type (flight_id, airport_code)
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_airport_code, _ = process_entity_string(
        airport_code, "airport_code")
    sql = "SELECT flight_stop.flight_id FROM flight_stop WHERE flight_stop.stop_airport = '%s' AND flight_stop.flight_id = %s" % (
        processed_airport_code, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_stops_specify_number_of_times(flight_id, integer):
    """
    _stops(x,"a:_i")
    :entity_type: (flight_id, integer)
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_integer, _ = process_entity_string(
        integer, "integer")
    sql = "SELECT flight_id FROM flight WHERE flight_id = %s AND stops = %s" % (processed_flight_id, processed_integer)
    results = get_result(sql)
    return len(results) > 0


def is_flight_has_class_type(flight_id, class_description):
    """
    _class_type(x,"first:_cl")
    :entity_type: (flight_id, class_type)
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_class_description, _ = process_entity_string(
        class_description, "class_description")
    sql = "SELECT flight_fare.flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code WHERE flight_fare.flight_id = %s AND fare_basis.class_type = '%s'" % (
        processed_flight_id, processed_class_description)
    results = get_result(sql)
    return len(results) > 0


def is_fare_basis_code_class_type(fare_basis_code, class_description):
    """
    _class_type(x,"first:_cl")
    :entity_type: (fare_basis_code, class_type)
    """
    processed_fare_basis_code, _ = process_entity_string(
        fare_basis_code, "fare_basis_code")
    processed_class_description, _ = process_entity_string(
        class_description, "class_description")
    sql = "SELECT fare_basis_code FROM fare_basis JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE fare_basis_code = '%s' AND class_description = '%s'" % (
        processed_fare_basis_code, processed_class_description)
    results = get_result(sql)
    return len(results) > 0



def is_flight_after_day(flight_id, day):
    """
    _after_day(x,"wednesday:_da")
    """
    return True


def is_flight_before_day(flight_id, day):
    """
    _before_day(x,"wednesday:_da")
    """
    return True



def is_flight_approx_arrival_time(flight_id, arrival_time):
    """
    _approx_arrival_time()
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_arrival_time, _ = process_entity_string(
        arrival_time, "time")
    if len(processed_arrival_time) == 4:
        if processed_arrival_time[2:] == '00':
            start_time = "%d%d" % (int(processed_arrival_time[:2]) - 1, 30)
            end_time = "%d%d" % (int(processed_arrival_time[:2]), 30)
        elif processed_arrival_time[2:] == '15':
            start_time = "%d%d" % (int(processed_arrival_time[:2]) - 1, 45)
            end_time = "%d%d" % (int(processed_arrival_time[:2]), 45)
        elif processed_arrival_time[2:] == '30':
            start_time = "%d%d" % (int(processed_arrival_time[:2]), 00)
            end_time = "%d%d" % (int(processed_arrival_time[:2]) + 1, 00)
        else:
            assert processed_arrival_time[2:] == '45'
            start_time = "%d%d" % (int(processed_arrival_time[:2]), 15)
            end_time = "%d%d" % (int(processed_arrival_time[:2]) + 1, 15)
    else:
        if processed_arrival_time[1:] == '00':
            start_time = "%d%d" % (int(processed_arrival_time[:1]) - 1, 30)
            end_time = "%d%d" % (int(processed_arrival_time[:1]), 30)
        elif processed_arrival_time[1:] == '15':
            start_time = "%d%d" % (int(processed_arrival_time[:1]) - 1, 45)
            end_time = "%d%d" % (int(processed_arrival_time[:1]), 45)
        elif processed_arrival_time[1:] == '30':
            start_time = "%d%d" % (int(processed_arrival_time[:1]), 00)
            end_time = "%d%d" % (int(processed_arrival_time[:1]) + 1, 00)
        else:
            assert processed_arrival_time[1:] == '45'
            start_time = "%d%d" % (int(processed_arrival_time[:1]), 15)
            end_time = "%d%d" % (int(processed_arrival_time[:1]) + 1, 15)
    sql = "SELECT flight_1.flight_id FROM flight flight_1 WHERE flight_1.arrival_time >= %s AND flight_1.arrival_time <= %s AND flight_1.flight_id = %s" % (
        start_time, end_time, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_arrival_time(flight_id, arrival_time):
    """
    _arrival_time(x,"1700:_ti")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_arrival_time, _ = process_entity_string(
        arrival_time, "time")
    sql = "SELECT flight_1.flight_id FROM flight flight_1 WHERE flight_1.arrival_time = %s AND flight_1.flight_id = %s" % (
        processed_arrival_time, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_departure_time(flight_id, departure_time):
    """
    _departure_time()
    :entity_type: (flight_id, time)
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_departure_time, _ = process_entity_string(
        departure_time, "time")
    sql = "SELECT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time = %s AND flight_1.flight_id = %s" % (
        processed_departure_time, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_approx_departure_time(flight_id, departure_time):
    """
    _approx_departure_time()
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_departure_time, _ = process_entity_string(
        departure_time, "time")
    if len(processed_departure_time) == 4:
        if processed_departure_time[2:] == '00':
            start_time = "%d%d" % (int(processed_departure_time[:2]) - 1, 30)
            end_time = "%d%d" % (int(processed_departure_time[:2]), 30)
        elif processed_departure_time[2:] == '15':
            start_time = "%d%d" % (int(processed_departure_time[:2]) - 1, 45)
            end_time = "%d%d" % (int(processed_departure_time[:2]), 45)
        elif processed_departure_time[2:] == '30':
            start_time = "%d%d" % (int(processed_departure_time[:2]), 00)
            end_time = "%d%d" % (int(processed_departure_time[:2]) + 1, 00)
        else:
            assert processed_departure_time[2:] == '45'
            start_time = "%d%d" % (int(processed_departure_time[:2]), 15)
            end_time = "%d%d" % (int(processed_departure_time[:2]) + 1, 15)
        sql = "SELECT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time >= %s AND flight_1.departure_time <= %s AND flight_1.flight_id = %s" % (
            start_time, end_time, processed_flight_id)
    elif len(processed_departure_time) == 3:
        if processed_departure_time[1:] == '00':
            start_time = "%d%d" % (int(processed_departure_time[:1]) - 1, 30)
            end_time = "%d%d" % (int(processed_departure_time[:1]), 30)
        elif processed_departure_time[1:] == '15':
            start_time = "%d%d" % (int(processed_departure_time[:1]) - 1, 45)
            end_time = "%d%d" % (int(processed_departure_time[:1]), 45)
        elif processed_departure_time[1:] == '30':
            start_time = "%d%d" % (int(processed_departure_time[:1]), 00)
            end_time = "%d%d" % (int(processed_departure_time[:1]) + 1, 00)
        else:
            assert processed_departure_time[1:] == '45'
            start_time = "%d%d" % (int(processed_departure_time[:1]), 15)
            end_time = "%d%d" % (int(processed_departure_time[:1]) + 1, 15)
        sql = "SELECT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time >= %s AND flight_1.departure_time <= %s AND flight_1.flight_id = %s" % (
            start_time, end_time, processed_flight_id)
    elif processed_departure_time == "0":
        start_time = "2330"
        end_time = "30"
        sql = "SELECT flight_1.flight_id FROM flight flight_1 WHERE (flight_1.departure_time >= %s OR flight_1.departure_time <= %s) AND flight_1.flight_id = %s" % (
            start_time, end_time, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_approx_return_time(flight_id, return_time):
    """
    _approx_return_time(x,"1900:_ti")
    """
    return is_flight_approx_arrival_time(flight_id, return_time)


def is_flight_during_day(flight_id, day_period):
    """
    _during_day(x,"evening:_pd")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_day_period, _ = process_entity_string(
        day_period, "day_period")
    period_map = {
        "morning": [0, 1200],
        "afternoon": [1200, 1800],
        "early": [0, 800],
        "evening": [1800, 2200],
        "pm": [1200, 2400],
        "late": [601, 1759],
        "breakfast": [600, 900],
        "late evening": [2000, 2400],
        "late night": [2159, 301],
        "daytime": [600,1800]
    }
    if processed_day_period == 'late night':
        sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days ON flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE flight.flight_id = %s AND date_day.year = 1991 AND date_day.month_number = 3 AND ( (date_day.day_number = 21 AND flight.departure_time > 2159) OR (date_day.day_number = 22 AND flight.departure_time < 301))" % (processed_flight_id)
    else:
        start, end = period_map[processed_day_period]
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.flight_id = %s AND flight_1.departure_time BETWEEN %d AND %d" % (
            processed_flight_id, start, end)
    results = get_result(sql)
    return len(results) > 0


def is_flight_during_day_arrival(flight_id, day_period):
    """
    _during_day(x,"evening:_pd")
    """
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_day_period, _ = process_entity_string(
        day_period, "day_period")
    period_map = {
        "morning": [0, 1200],
        "afternoon": [1200, 1800],
        "early": [0, 800],
        "evening": [1800, 2200],
        "pm": [1200, 2400],
        "late": [601, 1759],
        "breakfast": [600, 900],
        "late evening": [2000, 2400],
        "daytime": [600, 1800],
        "late night": [2159, 301],
        'mealtime': [1700,2000]
    }
    if processed_day_period == 'late night':
        sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days ON flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE flight.flight_id = %s AND date_day.year = 1991 AND date_day.month_number = 3 AND ( (date_day.day_number = 21 AND flight.arrival_time > 2159) OR (date_day.day_number = 22 AND flight.arrival_time < 301))" % (
            processed_flight_id)
    else:
        start, end = period_map[processed_day_period]
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.flight_id = %s AND flight_1.arrival_time BETWEEN %d AND %d" % (
            processed_flight_id, start, end)
    results = get_result(sql)
    return len(results) > 0


def is_flight_on_day_number(flight_id, day_number):
    """
    _day_number(x,"26:_dn")
    :entity_type (flight_id, day_number)
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_day_number, _ = process_entity_string(day_number, "day_number")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.day_number = %s AND flight.flight_id = %s" % (
        processed_day_number, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_on_day(flight_id, day):
    """
    _day $0 monday:_da
    :entity_type: (flight_id, day)
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_day, _ = process_entity_string(day, "day")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code WHERE days.day_name = '%s' AND flight.flight_id = %s" % (
        processed_day, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0



def is_flight_day_arrival(flight_id, day):
    """
    _day_arrival(x, "sunday:_da")
    :entity_type (flight_id, day)
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    processed_day, _ = process_entity_string(day, "day")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code WHERE days.day_name = '%s' AND flight.flight_id = %s" % (
        processed_day, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_day_return(flight_id, day):
    """
    _day_return(x, "tuesday:_da")
    :entity_type (flight_id, day)
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    processed_day, _ = process_entity_string(day, "day")
    sql = "SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN days ON fare_basis.basis_days = days.days_code WHERE flight.flight_id = %s AND days.day_name = '%s'" % (
        processed_flight_id, processed_day)
    results = get_result(sql)
    return len(results) > 0


def is_flight_day_number_arrival(flight_id, day_number):
    """
    _day_number_arrival(x, "14:_dn")
    :entity_type (flight_id, day_number)
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_day_number, _ = process_entity_string(day_number, "day_number")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE flight.flight_id = %s AND date_day.year = 1991 AND ((date_day.day_number = %s AND flight.arrival_time < flight.departure_time) OR (date_day.day_number = %s))" % (
        processed_flight_id, str(int(processed_day_number) - 1), processed_day_number)
    results = get_result(sql)
    return len(results) > 0


def is_flight_day_number_return(flight_id, day_number):
    """
    _day_number_return(x, "14:_dn")
    :entity_type (flight_id, day_number)
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_day_number, _ = process_entity_string(day_number, "day_number")
    sql = "SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN days ON fare_basis.basis_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE flight.flight_id = %s AND date_day.day_number = %s" % (
        processed_flight_id, processed_day_number)
    results = get_result(sql)
    return len(results) > 0


def is_flight_month_arrival(flight_id, month):
    """
    _month_arrival(x, "june:_mn")
    :entity_type (flight_id, month)
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    processed_month, _ = process_entity_string(month, "month")
    month_map = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = %s AND flight.flight_id = %s" % (
        month_map[processed_month], processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_on_month(flight_id, month):
    """
    _month(x, "june:_mn")
    :entity_type (flight_id, month)
    """
    return is_flight_month_arrival(flight_id, month)


def is_flight_month_return(flight_id, month):
    """
    _month_return(x, "june:_mn")
    :entity_type (flight_id, month)
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_month, _ = process_entity_string(month, "month")
    month_map = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }
    sql = "SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN days ON fare_basis.basis_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = %s AND flight.flight_id = %s" % (
        month_map[processed_month], processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_next_days_flight(flight_id, integer):
    """
    _next_days $0 2:_i
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_integer, _ = process_entity_string(integer, "integer")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number BETWEEN 20 and %s AND flight.flight_id = %s" % (
        int(processed_integer) + 20, processed_flight_id, )
    results = get_result(sql)
    return len(results) > 0


def is_overnight_flight(flight_id):
    """
    TODO implementation
    _overnight $0
    :entity_type flight_id
    """
    return True


def is_flight_days_from_today(flight_id, integer):
    """
    _overnight $0
    :entity_type flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    processed_integer, _ = process_entity_string(integer, "integer")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 5 AND date_day.day_number = %s AND flight.flight_id = %s" % (
        int(processed_integer) + 27, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_tomorrow_flight(flight_id):
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number = 20 AND flight.flight_id = %s" % (processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_tomorrow_arrival_flight(flight_id):
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number = 20 AND flight.departure_time > flight.arrival_time AND flight.flight_id = %s" % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_today_flight(flight_id):
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 6 AND date_day.day_number = 22 AND flight.flight_id = %s" % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_day_after_tomorrow_flight(flight_id):
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number = 21 AND flight.flight_id = %s" % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_airport_of_city(city_name, airport_code):
    """
    _airport(washington:_ci,x)
    :entity_type city_name, airport_code
    """
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    processed_airport_code, entity_type = process_entity_string(airport_code, "airport_code")
    sql = 'SELECT airport_code FROM airport_service JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = "%s" AND airport_service.airport_code = "%s"' % (processed_city_name, processed_airport_code)
    results = get_result(sql)
    return len(results) > 0


def is_specific_fare_basis_code(entity, fare_basis_code):
    """
    _fare_basis_code $0 415:_do
    :entity_type: (fare_basis_code, fare_basis_code)
    """
    processed_entity, _ = process_entity_string(entity, "fare_basis_code")
    processed_fare_basis_code, _ = process_entity_string(fare_basis_code, "fare_basis_code")
    return processed_entity.lower() == processed_fare_basis_code.lower()


def is_flight_has_specific_fare_basis_code(flight_id, fare_basis_code):
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_fare_basis_code, _ = process_entity_string(
        fare_basis_code, "fare_basis_code")
    sql = "SELECT flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE flight_id = %s AND fare.fare_basis_code = '%s'" % (processed_flight_id, processed_fare_basis_code)
    results = get_result(sql)
    return len(results) > 0


def is_flight_cost_fare(flight_id, dollar):
    """
    _fare $0 415:_do
    :entity_type: (flight_id, dollar)
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_dollar, _ = process_entity_string(dollar, "dollar")
    sql = "SELECT fare.one_direction_cost FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE flight.flight_id = %s AND fare.one_direction_cost = %s" % (processed_flight_id, processed_dollar)
    results = get_result(sql)
    return len(results) > 0


def is_time_elapsed(flight_id, hour):
    """
    _time_elapsed $0 9:_hr
    :entity_type: (flight_id, hour)
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_hour, _ = process_entity_string(hour, "hour")
    minutes = (int(processed_hour) * 60)
    sql = "SELECT flight_id FROM flight WHERE flight_id = %s AND time_elapsed = %s" % (processed_flight_id, minutes)
    results = get_result(sql)
    return len(results) > 0


def is_flight_meal_code(flight_id, meal_code):
    """
    _meal_code $0 b:_rc
    :entity_type: (flight_id, meal_code)
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_meal_code, _ = process_entity_string(meal_code, "meal_code")
    sql = "SELECT flight_id FROM flight WHERE flight_id = %s AND meal_code = '%s'" % (processed_flight_id, processed_meal_code)
    results = get_result(sql)
    return len(results) > 0


def is_flight_has_specific_meal(flight_id, meal_description):
    """
    _meal $0 dinner:_me
    :entity_type: (flight_id, meal_description)
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_meal_description, _ = process_entity_string(
        meal_description, "meal_description")
    sql = "SELECT flight_id FROM flight JOIN food_service ON flight.meal_code = food_service.meal_code WHERE flight_id = %s AND food_service.meal_description = '%s'" % (
        processed_flight_id, processed_meal_description)
    results = get_result(sql)
    return len(results) > 0


def is_flight_aircraft(flight_id, aircraft_code):
    """
    _meal_code $0 b:_rc
    :entity_type: (flight_id, meal_code)
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_aircraft_code, _ = process_entity_string(aircraft_code, "aircraft_code")
    sql = "SELECT flight_id FROM flight WHERE flight_id = %s AND aircraft_code_sequence = '%s'" % (processed_flight_id, processed_aircraft_code)
    results = get_result(sql)
    return len(results) > 0


def is_airline_has_booking_class(class_description, airline_code):
    """
    _airline(x, us:_al)
    :entity_type: (class_description, airline_code)
    """
    processed_class_description, _ = process_entity_string(
        class_description, "class_description")
    processed_airline_code, _ = process_entity_string(
        airline_code, "airline_code")
    sql = "SELECT class_description FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE class_of_service.class_description = '%s' AND flight.airline_code = '%s'" % (
        processed_class_description, processed_airline_code)
    results = get_result(sql)
    return len(results) > 0


def is_airline_provide_meal(meal_code, airline_code):
    processed_meal_code, _ = process_entity_string(
        meal_code, "meal_code")
    processed_airline_code, _ = process_entity_string(
        airline_code, "airline_code")
    sql = "SELECT meal_code FROM flight WHERE airline_code = '%s' AND meal_code = '%s'" % (processed_airline_code, processed_meal_code)
    results = get_result(sql)
    return len(results) > 0


def is_flight_has_booking_class(flight_id, class_description):
    """
    _booking_class(x, us:_al)
    :entity_type: (flight_id, class_description)
    """
    processed_flight_id, _ = process_entity_string(flight_id, "flight_id")
    processed_class_description, _ = process_entity_string(
        class_description, "class_description")
    sql = "SELECT flight_fare.flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE class_of_service.class_description = '%s' AND flight_fare.flight_id = %s" % (
        processed_class_description, processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_with_specific_aircraft(flight_id, aircraft_code):
    processed_flight_id, _ = process_entity_string(
        flight_id, "flight_id")
    processed_aircraft_code, _ = process_entity_string(
        aircraft_code, "aircraft_code")
    sql = "SELECT flight_id FROM flight JOIN equipment_sequence ON flight.aircraft_code_sequence = equipment_sequence.aircraft_code_sequence WHERE flight.flight_id = %s AND equipment_sequence.aircraft_code = '%s'" % (processed_flight_id, processed_aircraft_code)
    results = get_result(sql)
    return len(results) > 0


# Unit Predicate
def is_aircraft(aircraft_code):
    """
    _aircraft(x)
    :entity_type: aircraft_code
    """
    processed_aircraft_code, _ = process_entity_string(aircraft_code, "aircraft_code")
    sql = "SELECT aircraft_code FROM aircraft WHERE aircraft_code = '%s'" % (
        processed_aircraft_code)
    results = get_result(sql)
    return len(results) > 0


def aircraft_code(aircraft_code):
    """
    _aircraft_code:_t $0
    :entity_type: aircraft_code
    """
    return is_aircraft(aircraft_code)


def is_city(city_name):
    """
    _city(x)
    :entity_type: city_name
    """
    processed_city_name, _ = process_entity_string(city_name, "city_name")
    sql = "SELECT city_name FROM city WHERE city_name = '%s'" % (
        processed_city_name)
    results = get_result(sql)
    return len(results) > 0


def is_airline(entity):
    """
    _airline(x)
    :entity_type airline_code
    """
    # assert isinstance(entity, str)
    entity_name, entity_type = process_entity_string(entity, "airline_code")
    sql = 'SELECT airline_code FROM airline WHERE airline_code = "%s"' % entity_name
    results = get_result(sql)
    return len(results) > 0


def is_airport(entity):
    """
    airport(x)
    :entity_type airport_code
    """
    # assert isinstance(entity, str)
    entity_name, entity_type = process_entity_string(entity, "airport_code")
    sql = 'SELECT airport_code FROM airport WHERE airport_code = "%s"' % entity_name
    results = get_result(sql)
    return len(results) > 0


def is_flight(entity):
    """
    flight(x)
    :entity_type flight_id
    """
    # assert isinstance(entity, str)
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = 'SELECT flight_id FROM flight WHERE flight_id = %s' % entity_name
    results = get_result(sql)
    return len(results) > 0


def is_daily_flight(entity):
    """
    _daily(x)
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = "SELECT flight_id FROM flight WHERE flight_days = 'daily' AND flight_id = %s" % entity_name
    results = get_result(sql)
    return len(results) > 0


def is_discounted_flight(entity):
    """
    _discounted(x)
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = "SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code WHERE fare_basis.discounted = 'YES' AND flight.flight_id = %s" % entity_name
    results = get_result(sql)
    return len(results) > 0


def is_connecting_flight(entity):
    """
    _connecting(x)
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = 'SELECT flight_id FROM flight WHERE flight_id = %s AND connections > 0' % entity_name
    results = get_result(sql)
    return len(results) > 0


def is_oneway(entity):
    """
    oneway(x)
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = 'SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE fare.round_trip_required = "NO" AND flight.flight_id = %s' % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_flight_has_stop(entity):
    """
    _has_stops(x)
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = 'SELECT T1.flight_id FROM flight AS T1 JOIN flight_stop AS T2 ON T1.flight_id = T2.flight_id WHERE T1.flight_id = %s' % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_non_stop_flight(flight_id):
    """
    _nonstop(x)
    :entity_type flight_id
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = 'SELECT flight.flight_id FROM flight WHERE flight.stops = 0 AND flight.flight_id = %s' % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_meal(entity):
    """
    TODO: not sure
    _meal:_t(x)
    :entity_type meal_code
    """
    entity_name, entity_type = process_entity_string(entity, "meal_code")
    sql = "SELECT meal_code FROM food_service WHERE food_service.meal_code = '%s'" % (entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_meal_code(entity):
    """
    _meal_code(x)
    :entity_type meal_code
    """
    entity_name, entity_type = process_entity_string(entity, "meal_code")
    sql = "SELECT meal_code FROM food_service WHERE food_service.meal_code = '%s'" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_flight_has_meal(entity):
    """
    _has_meal(x):
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = "SELECT flight_id FROM flight WHERE meal_code is not NULL AND flight_id = %s" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_flight_tonight(entity):
    """
    _tonight(x)
    :entity_type flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = "SELECT flight_id FROM flight WHERE departure_time BETWEEN %d AND %d AND flight_id = %s" % (
        1800, 2359, entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_booking_class_t(entity):
    """
    _booking_class:_t(x)
    :entity_type: class_description
    """
    entity_name, entity_type = process_entity_string(
        entity, "class_description")
    sql = "SELECT DISTINCT class_description FROM class_of_service WHERE class_description = '%s';" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_class_of_service(entity):
    """
    _class_of_service(x)
    :entity_type: booking_class
    """
    return is_booking_class_t(entity)


def is_fare_basis_code(entity):
    """
    _fare_basis_code(x)
    :entity_type: fare_basis_code
    """
    entity_name, entity_type = process_entity_string(entity, "fare_basis_code")
    sql = "SELECT DISTINCT fare_basis_1.fare_basis_code FROM fare_basis fare_basis_1 WHERE fare_basis_code = '%s'" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_flight_economy(flight_id):
    """
    _economy(x)
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(flight_id, "flight_id")
    sql = "SELECT flight_fare.flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code WHERE fare_basis.economy = 'YES' AND flight_fare.flight_id = %s" % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_economy(entity):
    """
    _economy(x)
    :entity_type: fare_basis_code
    """
    entity_name, entity_type = process_entity_string(entity, "fare_basis_code")
    sql = "SELECT DISTINCT fare_basis_code FROM fare_basis fare_basis_1 WHERE fare_basis_1.economy = 'YES' AND fare_basis_1.fare_basis_code = '%s'" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_fare(entity):
    """
    _fare(x)
    :entity_type: fare_id
    """
    entity_name, entity_type = process_entity_string(entity, "fare_id")
    sql = "SELECT DISTINCT fare_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id WHERE fare_id = %s" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_aircraft_code_t(entity):
    """
    _aircraft_code:t(x)
    :entity_type: aircraft_code
    """
    entity_name, entity_type = process_entity_string(entity, "aircraft_code")
    sql = "SELECT aircraft_code FROM aircraft WHERE aircraft_code = '%s'" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_ground_transport(transport_type):
    """
    _ground_transport(x)
    :entity_type: transport_type
    """
    entity_name, entity_type = process_entity_string(
        transport_type, "transport_type")
    sql = "SELECT DISTINCT ground_service_1.transport_type FROM ground_service ground_service_1 WHERE ground_service_1.transport_type = '%s'" % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_round_trip(entity):
    """
    _round_trip(x)
    :entity_type: flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = 'SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE fare.round_trip_required IS NOT NULL AND flight.flight_id = %s' % (
        entity_name)
    results = get_result(sql)
    return len(results) > 0


def is_rental_car(entity):
    """
    _rental_car(x)
    :entity_type: transport_type
    """
    entity_name, entity_type = process_entity_string(entity, "transport_type")
    return entity_name.lower() == "rental car"


def is_limousine(entity):
    """
    _limousine(x)
    :entity_type: transport_type
    """
    entity_name, entity_type = process_entity_string(entity, "transport_type")
    return entity_name.upper() == "LIMOUSINE"


def is_rapid_transit(entity):
    """
    _rapid_transit(x)
    :entity_type: transport_type
    """
    entity_name, entity_type = process_entity_string(entity, "transport_type")
    return entity_name.upper() == "RAPID TRANSIT"


def is_taxi(entity):
    """
    _taxi(x)
    :entity_type: transport_type
    """
    entity_name, entity_type = process_entity_string(entity, "transport_type")
    return entity_name.upper() == "TAXI"


def is_air_taxi_operation(entity):
    """
    _air_taxi_operation(x)
    :entity_type: transport_type
    """
    entity_name, entity_type = process_entity_string(entity, "transport_type")
    return entity_name.upper() == "AIR TAXI OPERATION"


def is_ground_transport_on_weekday(entity):
    """
    _weekday(x)
    :entity_type: transport_type
    """
    return True


def is_flight_on_year(entity, year):
    """
    _year(x,"1991:_yr")
    :entity_type: flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    processed_year, _ = process_entity_string(year, "year")
    sql = "SELECT flight_id FROM flight JOIN days ON flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE flight_id = %s AND date_day.year = %s" % (entity_name, processed_year)
    results = get_result(sql)
    return len(results) > 0


def is_flight_on_weekday(entity):
    """
    _weekday(x)
    :entity_type: flight_id
    """
    entity_name, entity_type = process_entity_string(entity, "flight_id")
    sql = "SELECT distinct day_name FROM flight JOIN days ON flight.flight_days = days.days_code WHERE flight_id = %s AND day_name IN ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY')" % entity_name
    results = get_result(sql)
    return len(results) == 5


def is_time_zone_code(entity):
    """
    _time_zone_code(x)
    :entity_type: time_zone_code
    """
    entity_name, entity_type = process_entity_string(entity, "time_zone_code")
    return entity_name.upper() in {"CST", "EST", "MST", "PST"}


def is_turboprop(aircraft_code):
    """
    _turboprop(x)
    :entity_type: aircraft_code
    """
    processed_aircraft_code, entity_type = process_entity_string(
        aircraft_code, "aircraft_code")
    sql = "SELECT aircraft_code FROM aircraft WHERE aircraft_code = '%s' AND propulsion = 'TURBOPROP'" % (
        processed_aircraft_code)
    results = get_result(sql)
    return len(results) > 0


def is_flight_turboprop(flight_id):
    """
    _turboprop(x)
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight_id FROM flight JOIN aircraft ON flight.aircraft_code_sequence = aircraft.aircraft_code WHERE propulsion = 'TURBOPROP' AND flight_id = %s" % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


def is_flight_jet(flight_id):
    """
    _jet(x)
    :entity_type: flight_id
    """
    processed_flight_id, entity_type = process_entity_string(
        flight_id, "flight_id")
    sql = "SELECT flight_id FROM flight JOIN aircraft ON flight.aircraft_code_sequence = aircraft.aircraft_code WHERE propulsion = 'JET' AND flight_id = %s" % (
        processed_flight_id)
    results = get_result(sql)
    return len(results) > 0


# Meta Predicate
# TODO implement meta-predicates
def equals(entity_1, entity_2):
    if entity_1 is None or entity_2 is None:
        return False
    processed_entity_1, _ = process_entity_string(entity_1)
    processed_entity_2, _ = process_entity_string(entity_2)
    return str(processed_entity_1).lower() == str(processed_entity_2).lower()


def count(function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    count = 0
    for entity in entity_set_function():
        if function(entity):
            count += 1
    return count


def exists(function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    for e in entity_set_function():
        if function(e):
            return True
    return False


def the(function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    return [entity for entity in entity_set_function() if function(entity)]


def argmax(predicate, target_function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            v = target_function(e)
            if isinstance(v, list):
                for _v in v:
                    assert isinstance(_v, dict)
                    values.append((e, _v[list(_v.keys())[0]],))
            elif isinstance(v, dict):
                values.append((e, v[list(v.keys())[0]],))
            else:
                assert isinstance(v, int) or isinstance(v, float)
                values.append((e, v,))
    max_value, max_indices = 0, list()
    for idx, (e, v) in enumerate(values):
        if v is None:
            continue
        if v > max_value:
            max_value = v
            max_indices = [idx]
        elif v == max_value:
            max_indices.append(idx)
    if len(max_indices) > 0:
        return [values[idx][0] for idx in max_indices]
    return None


def argmin(predicate, target_function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            v = target_function(e)
            if isinstance(v, list):
                for _v in v:
                    assert isinstance(_v, dict)
                    values.append((e, _v[list(_v.keys())[0]],))
            elif isinstance(v, dict):
                values.append((e, v[list(v.keys())[0]],))
            else:
                assert isinstance(v, int) or isinstance(v, float)
                values.append((e, v,))
    min_value, min_indices = 10000000, list()
    for idx, (e, v) in enumerate(values):
        if v is None:
            continue
        if v < min_value:
            min_value = v
            min_indices = [idx]
        elif v == min_value:
            min_indices.append(idx)
    if len(min_indices) > 0:
        return [values[idx][0] for idx in min_indices]
    return None


def sum_predicate(predicate, target_function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            v = target_function(e)
            if isinstance(v, list):
                for _v in v:
                    assert isinstance(_v, dict)
                    values.append((e, _v[list(_v.keys())[0]],))
            elif isinstance(v, dict):
                values.append((e, v[list(v.keys())[0]],))
            else:
                assert isinstance(v, int) or isinstance(v, float)
                values.append((e, v,))
    print(values)
    total = 0
    for e, v in values:
        total += v
    return total


def max_predicate(predicate, target_function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            v = target_function(e)
            if isinstance(v, list):
                for _v in v:
                    assert isinstance(_v, dict)
                    values.append((e, _v[list(_v.keys())[0]],))
            elif isinstance(v, dict):
                values.append((e, v[list(v.keys())[0]],))
            else:
                assert isinstance(v, int) or isinstance(v, float)
                values.append((e, v,))
    if len(values) == 0:
        return None
    max_value = 0
    for e, v in values:
        if v > max_value:
            max_value = v
    return max_value


def min_predicate(predicate, target_function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            v = target_function(e)
            if isinstance(v, list):
                for _v in v:
                    assert isinstance(_v, dict)
                    values.append((e, _v[list(_v.keys())[0]],))
            elif isinstance(v, dict):
                values.append((e, v[list(v.keys())[0]],))
            else:
                assert isinstance(v, int) or isinstance(v, float)
                values.append((e, v,))
    if len(values) == 0:
        return None
    min_value = 100000000
    for e, v in values:
        if v < min_value:
            min_value = v
    return min_value


def get_target_value(predicate, target_function, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            v = target_function(e)
            if isinstance(v, list):
                for _v in v:
                    assert isinstance(_v, dict)
                    v_dict = dict()
                    v_dict.update(e)
                    v_dict[target_function.__name__ + '_0'] = _v[list(_v.keys())[0]]
                    values.append(v_dict)
            elif isinstance(v, dict):
                v_dict = dict()
                v_dict.update(e)
                v_dict[target_function.__name__ + '_0'] = v[list(v.keys())[0]]
                values.append(v_dict)
            else:
                v_dict = dict()
                v_dict.update(e)
                v_dict[target_function.__name__ + '_0'] = v
                values.append(v_dict)
    return values


def get_target_values(predicate, target_functions, entity_set_function):
    if entity_set_function is None:
        entity_set_function = get_all_flight_ids
    values = list()
    for e in entity_set_function():
        if predicate(e):
            _values = list()
            v_dict = dict()
            v_dict.update(e)
            for tf_idx, tf in enumerate(target_functions):
                v = tf(e)
                suffix = "_%d" % tf_idx
                if isinstance(v, list):
                    for _v in v:
                        assert isinstance(_v, dict)
                        v_dict[tf.__name__ + suffix] = _v[list(_v.keys())[0]]
                        # _values.append(_v[list(_v.keys())[0]])
                elif isinstance(v, dict):
                    v_dict[tf.__name__ + suffix] = v[list(v.keys())[0]]
                    # values.append(v[list(v.keys())[0]])
                else:
                    v_dict[tf.__name__ + suffix] = v
                    # values.append(v)
            values.append(v_dict)
    return values


def process_numerical_value(value):
    if isinstance(value, list):
        assert isinstance(value[0], dict)
        _value = float(value[0][list(value[0].keys())[0]])
    elif isinstance(value, dict):
        _value = float(value[list(value.keys())[0]])
    elif isinstance(value, str):
        _value, _ = process_entity_string(value)
        _value = float(_value)
    else:
        _value = float(value)
    return _value


def process_value(value):
    if isinstance(value, list):
        if len(value) == 0:
            return ""
        assert isinstance(value[0], dict)
        _value = value[0][list(value[0].keys())[0]]
    elif isinstance(value, dict):
        _value = value[list(value.keys())[0]]
    elif isinstance(value, str):
        _value, _ = process_entity_string(value)
        _value = value
    else:
        _value = value
    return _value


def less_than(value_1, value_2):
    """
    _<
    """
    _value_1 = process_numerical_value(value_1)
    _value_2 = process_numerical_value(value_2)
    return _value_1 <= _value_2


def larger_than(value_1, value_2):
    """
    _>
    """
    _value_1 = process_numerical_value(value_1)
    _value_2 = process_numerical_value(value_2)
    return _value_1 >= _value_2


def numerical_equals(value_1, value_2):
    """
    _=
    """
    _value_1 = process_value(value_1)
    _value_2 = process_value(value_2)
    return _value_1 == _value_2


if __name__ == '__main__':
    result = [(xe, ye) for xe in get_all_flight_ids() for ye in get_all_aircraft_codes() if (lambda x,y: (is_flight_with_specific_aircraft(x,y) and is_flight_airline(x,"dl:_al") and is_flight(x) and is_from(x,"seattle:_ci") and is_to(x,"salt_lake_city:_ci")))(xe, ye)]
    pprint(result)
