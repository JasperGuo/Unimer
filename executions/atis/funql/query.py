# coding=utf8

import re
import mysql.connector
from pprint import pprint
from .transform import transform

db = None


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


def format_headers(header):
    s = header.replace("( ", "(").replace(" )", ")").strip().lower()
    return s


def get_result(sql):
    db = get_connection()
    _sql = sql
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


"""
Entity Type
"""

def build_entity(entity_type, entity_value):
    return {entity_type: entity_value}


def answer(values):
    return values


def get_entity_value(entity, key=None):
    assert isinstance(entity, dict)
    if key:
        entity_type = key
        entity_value = entity[key]
    else:
        entity_type = list(entity.keys())[0]
        entity_value = entity[entity_type].replace("_", " ")
    if entity_value == 'st louis':
        entity_value = 'st. louis'
    elif entity_value == 'st petersburg':
        entity_value = 'st. petersburg'
    elif entity_value == 'st paul':
        entity_value = 'st. paul'
    return entity_type, entity_value


def meal_code_all():
    sql = "SELECT distinct meal_code FROM food_service"
    return get_result(sql)


def airport_all():
    sql = "SELECT distinct airport_code FROM airport"
    return get_result(sql)


def aircraft_all():
    sql = "SELECT distinct aircraft_code FROM aircraft"
    return get_result(sql)


def city_all():
    sql = "SELECT distinct city_name FROM city"
    return get_result(sql)


def fare_basis_code_all():
    sql = "SELECT distinct fare_basis_code FROM fare_basis"
    return get_result(sql)


def airline_all():
    sql = "SELECT distinct airline_code FROM airline"
    return get_result(sql)


def flight_all():
    sql = 'SELECT DISTINCT flight_id FROM flight'
    return get_result(sql)


def booking_class_t_all():
    sql = "SELECT distinct class_description FROM class_of_service"
    return get_result(sql)


def class_of_service_all():
    sql = 'SELECT DISTINCT class_of_service_1.booking_class FROM class_of_service class_of_service_1'
    return get_result(sql)


def ground_transport_all():
    sql = "SELECT distinct transport_type FROM ground_service"
    return get_result(sql)


def abbrev(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    results = list()
    for e in entities:
        sql = "SELECT DISTINCT airline_1.airline_code FROM airline airline_1 WHERE airline_1.airline_name like '%" + e['airline_code'] + "%'"
        results += get_result(sql)
    return results


def capacity(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    results = list()
    flight_number_template = "SELECT flight_1.flight_number, aircraft_1.capacity FROM aircraft as aircraft_1 JOIN flight as flight_1 on aircraft_1.aircraft_code = flight_1.aircraft_code_sequence WHERE flight_1.flight_number = %s;"
    flight_id_template = "SELECT flight_1.flight_id, aircraft_1.capacity FROM aircraft as aircraft_1 JOIN flight as flight_1 on aircraft_1.aircraft_code = flight_1.aircraft_code_sequence WHERE flight_1.flight_id = %s;"
    aircraft_code_template = "SELECT DISTINCT aircraft_1.aircraft_code, aircraft_1.capacity FROM aircraft aircraft_1 WHERE aircraft_1.aircraft_code = '%s'"
    for e in entities:
        if 'aircraft_code' in e:
            entity_type, entity_name = get_entity_value(e, key='aircraft_code')
            sql = aircraft_code_template % entity_name
        elif 'flight_id' in e:
            entity_type, entity_name = get_entity_value(e, key='flight_id')
            # flight id
            sql = flight_id_template % entity_name
        else:
            # entity_type == 'flight_number':
            entity_type, entity_name = get_entity_value(e, key='flight_number')
            sql = flight_number_template % entity_name
        results += get_result(sql)
    return results


def flight_number(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_number FROM flight WHERE flight_id IN %s" % flight_id
    results = get_result(sql)
    return results


def time_elapsed(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_id, time_elapsed FROM flight WHERE flight_id IN %s" % flight_id
    return get_result(sql)


def time_elapsed_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_id FROM flight WHERE time_elapsed = %s" % entity_value_1
    return get_result(sql)


def minimum_connection_time(airport_code):
    entity_type_1, entity_value_1 = get_entity_value(airport_code)
    sql = "SELECT DISTINCT airport_1.minimum_connect_time FROM airport airport_1 WHERE airport_1.airport_code = '%s'" % (
        entity_value_1)
    return get_result(sql)


def miles_distant(entity_1, entity_2):
    """
    _miles_distant
    :entity_type: (airport_code, city_name)
    :entity_type: (city_name, city_name)
    """
    entity_type_1, entity_value_1 = get_entity_value(entity_1)
    entity_type_2, entity_value_2 = get_entity_value(entity_2)

    if entity_type_1 == 'airport_code' and entity_type_2 == 'city_name':
        sql = "SELECT airport_service.miles_distant FROM airport_service JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = '%s' AND airport_service.airport_code = '%s'" % (
            entity_value_2, entity_value_1)
    else:
        sql = "SELECT distinct airport_service.miles_distant FROM airport_service JOIN city ON airport_service.city_code = city.city_code WHERE city.city_name = '%s' AND airport_service.airport_code IN (SELECT T1.airport_code FROM airport_service AS T1 JOIN city AS T2 ON T1.city_code = T2.city_code WHERE T2.city_name = '%s');" % (
            entity_value_1, entity_value_2)
    return get_result(sql)


def minutes_distant(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()
    
    key = 'city_name' if 'city_name' in entities[0] else 'airport_code'
    values = "(%s)" % ','.join(['"%s"' % e[key] for e in entities])
    if key == 'city_name':
        sql = "SELECT minutes_distant, city_name FROM airport_service JOIN city ON airport_service.city_code = city.city_code WHERE city.city_name IN %s" % (values)
    else:
        # airport_code
        sql = "SELECT minutes_distant FROM airport_service WHERE airport_code IN %s" % values
    results = get_result(sql)
    return results

def services_1(airline_code):
    entity_type_1, entity_value_1 = get_entity_value(airline_code)

    sql = "SELECT city.city_name, flight.to_airport FROM flight JOIN airport_service ON flight.to_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE flight.airline_code = '%s'" % (entity_value_1)
    results = get_result(sql)
    return results


def services_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)

    if entity_type_1 == 'city_name':
        sql = "SELECT flight.airline_code FROM flight JOIN airport_service ON flight.to_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = '%s'" % (
            entity_value_1)

    else:
        assert entity_type_1 == 'airport_code'
        sql = "SELECT DISTINCT flight.airline_code FROM flight WHERE flight.to_airport  =  '%s'" % (
            entity_value_1,)

    results = get_result(sql)
    return results


def services(entity_1, entity_2):
    entity_type_1, entity_value_1 = get_entity_value(entity_1)
    entity_type_2, entity_value_2 = get_entity_value(entity_2)
    if entity_type_2 == 'city_name':
        sql = "SELECT DISTINCT flight.airline_code, city.city_name FROM flight JOIN airport_service ON flight.to_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE flight.airline_code = '%s' AND city.city_name = '%s'" % (
            entity_value_1, entity_value_2)
    else:
        assert entity_type_2 == 'airport_code'
        sql = "SELECT DISTINCT flight.airline_code, flight.to_airport FROM flight WHERE flight.airline_code = '%s' AND flight.to_airport  =  '%s'" % (
            entity_value_1, entity_value_2,)
    results = get_result(sql)
    return results


def airport(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['from_airport', 'to_airport', 'airport_code']:
            if key in entity and entity[key] not in value_set:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def aircraft(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['aircraft_code']:
            if key in entity and entity[key] not in value_set:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results



def airline(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['airline_code']:
            if key in entity and entity[key] not in value_set:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def city(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['city_name']:
            if key in entity and entity[key] not in value_set:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def time_zone_code(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['time_zone_code']:
            if key in entity and entity[key] not in value_set:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def flight(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['flight_id']:
            if key in entity and entity[key] not in value_set:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def taxi(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['transport_type']:
            if key in entity and "TAXI" in entity[key]:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def air_taxi_operation(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['transport_type']:
            if key in entity and "AIR TAXI OPERATION" == entity[key]:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results

def limousine(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['transport_type']:
            if key in entity and "LIMOUSINE" == entity[key]:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def rapid_transit(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['transport_type']:
            if key in entity and "RAPID TRANSIT" == entity[key]:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results



def rental_car(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['transport_type']:
            if key in entity and "RENTAL CAR" == entity[key]:
                results.append({key: entity[key]})
                value_set.add(entity[key])
                break
    return results


def ground_transport(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    value_set = set()
    for entity in entities:
        # Airport code
        for key in ['transport_type']:
            results.append({key: entity[key]})
            value_set.add(entity[key])
            break
    return results


def turboprop(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    et = 'aircraft_code' if 'aircraft_code' in entities[0] else 'flight_id'

    values = "(%s)" % ','.join(['"%s"' % e[et] for e in entities])
    if et == 'aircraft_code':
        sql = "SELECT aircraft_code FROM aircraft WHERE aircraft_code IN %s AND propulsion = 'TURBOPROP'" % values
    else:
        sql = "SELECT flight_id FROM flight JOIN aircraft ON flight.aircraft_code_sequence = aircraft.aircraft_code WHERE propulsion = 'TURBOPROP' AND flight_id IN %s" % values
    results = get_result(sql)
    return results


def jet(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    et = 'aircraft_code' if 'aircraft_code' in entities[0] else 'flight_id'

    values = "(%s)" % ','.join(['"%s"' % e[et] for e in entities])
    if et == 'aircraft_code':
        sql = "SELECT aircraft_code FROM aircraft WHERE aircraft_code IN %s AND propulsion = 'JET'" % values
    else:
        sql = "SELECT flight_id FROM flight JOIN aircraft ON flight.aircraft_code_sequence = aircraft.aircraft_code WHERE propulsion = 'JET' AND flight_id IN %s" % values
    results = get_result(sql)
    return results


def economy(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    sql = "SELECT flight_fare.flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code WHERE fare_basis.economy = 'YES'"
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def connecting(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()
    
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = 'SELECT DISTINCT flight_id FROM flight WHERE connections > 0 AND flight_id IN %s ' % flight_id
    results = get_result(sql)
    return results


def discounted(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code WHERE fare_basis.discounted = 'YES' AND flight.flight_id IN %s" % flight_id
    results = get_result(sql)
    return results


def nonstop(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    sql = 'SELECT flight.flight_id FROM flight WHERE flight.stops = 0'
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def daily(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    sql = "SELECT flight_id FROM flight WHERE flight_days = 'daily'"
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def today(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 6 AND date_day.day_number = 22"
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def after_day_2(entity):
    return flight_all()


def before_day_2(entity):
    return flight_all()


def tomorrow(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number = 20"
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def overnight(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    return entities


def tonight(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_id FROM flight WHERE departure_time BETWEEN %d AND %d AND flight_id IN %s" % (
        1800, 2359, flight_id)
    results = get_result(sql)
    return results


def day_number_return_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN days ON fare_basis.basis_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.day_number = %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def tomorrow_arrival(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number = 20 AND flight.departure_time > flight.arrival_time AND flight.flight_id IN %s" % (
            flight_id)
    results = get_result(sql)
    return results


def day_after_tomorrow(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number = 21"
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def oneway(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    sql = 'SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE fare.round_trip_required = "NO"'
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def round_trip(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    sql = 'SELECT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE fare.round_trip_required IS NOT NULL'
    results = get_result(sql)
    results = intersection(entities, results)
    return results


def weekday(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    results = list()
    for entity in entities:
        if 'flight_id' not in entity:
            assert 'transport_type' in entity
            results.append(entity)
        else:
            sql = "SELECT distinct day_name FROM flight JOIN days ON flight.flight_days = days.days_code WHERE flight_id = %s AND day_name IN ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY')" % entity['flight_id']
            tmp = get_result(sql)
            if len(tmp) == 5:
                results.append(entity)
    return results


def airline_2(airline_code):
    entity_type_1, entity_value_1 = get_entity_value(airline_code)
    sql = "SELECT flight_id FROM flight WHERE airline_code = '%s'" % (
        entity_value_1)
    return get_result(sql)


def aircraft_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN equipment_sequence ON flight.aircraft_code_sequence = equipment_sequence.aircraft_code_sequence WHERE equipment_sequence.aircraft_code = '%s'" % (
        entity_value_1)
    return get_result(sql)


def manufacturer_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT aircraft.aircraft_code , flight.flight_id FROM flight JOIN aircraft ON flight.aircraft_code_sequence = aircraft.aircraft_code WHERE aircraft.manufacturer = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return get_result(sql)


def meal(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    for entity in entities:
        sql = "SELECT food_service.meal_description FROM flight JOIN food_service ON flight.meal_code = food_service.meal_code WHERE flight_id = %s" % (
            entity['flight_id'])
        results += get_result(sql)
    return results


def loc_t_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)

    if entity_type_1 == 'city_name':
        sql = "SELECT T.airport_code FROM airport_service AS T JOIN city ON T.city_code = city.city_code WHERE city.city_name = '%s';" % (
            entity_value_1)
    elif entity_type_1 == 'state_name':
        sql = "SELECT T.airport_code FROM airport_service AS T JOIN city ON T.city_code = city.city_code JOIN state ON city.state_code = state.state_code WHERE state.state_name = '%s';" % (
            entity_value_1)
    else:
        assert entity_type_1 == 'time_zone_code'
        sql = "SELECT city_name FROM city WHERE time_zone_code = '%s'" % (
            entity_value_1)
    return get_result(sql)


def loc_t_1(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    if entity_type_1 == 'airport_code':
        sql = "SELECT city.city_name FROM airport_service AS T JOIN city ON T.city_code = city.city_code WHERE T.airport_code = '%s';" % (
            entity_value_1)
    else:
        assert entity_type_1 == 'city_name'
        sql = "SELECT time_zone_code FROM city WHERE city_name = '%s'" % (
            entity_value_1)
    results = get_result(sql)
    return results



def during_day_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
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
        "daytime": [600, 1800]
    }
    if entity_value_1 == 'late night':
        sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days ON flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 3 AND ( (date_day.day_number = 21 AND flight.departure_time > 2159) OR (date_day.day_number = 22 AND flight.departure_time < 301))"
    else:
        start, end = period_map[entity_value_1]
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time BETWEEN %d AND %d" % (
            start, end)
    results = get_result(sql)
    return results


def during_day_arrival_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    processed_day_period = entity_value_1
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
        'mealtime': [1700, 2000]
    }
    if processed_day_period == 'late night':
        sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days ON flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE flight.flight_id = %s AND date_day.year = 1991 AND date_day.month_number = 3 AND ( (date_day.day_number = 21 AND flight.arrival_time > 2159) OR (date_day.day_number = 22 AND flight.arrival_time < 301))"
    else:
        start, end = period_map[processed_day_period]
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.arrival_time BETWEEN %d AND %d" % (
            start, end)
    results = get_result(sql)
    return results


def day_number_arrival_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND ((date_day.day_number = %s AND flight.arrival_time < flight.departure_time) OR (date_day.day_number = %s))" % (
        str(int(entity_value_1) - 1), entity_value_1)
    results = get_result(sql)
    return results


def flight_number_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_id FROM flight WHERE flight_number = '%s'" % entity_value_1
    results = get_result(sql)
    return results


def aircraft_basis_type_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT aircraft_code FROM aircraft WHERE basic_type = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def from_2(entity):
    if isinstance(entity, dict):
        entity_type_1, entity_value_1 = get_entity_value(entity)

        if entity_type_1 == 'airport_code':
            sql = "SELECT DISTINCT flight_id FROM flight WHERE flight.from_airport = '%s'" % (
                entity_value_1)
        else:
            # entity_type == 'city_name'
            sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.from_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE city_1.city_name = '%s'" % (
                entity_value_1)
        results = get_result(sql)
    else:
        assert isinstance(entity, list)
        if len(entity) == 0:
            return list()
        entity_type_1, entity_value_1 = get_entity_value(entity[0])
        values = "(%s)" % ','.join(
            ['"%s"' % e[entity_type_1] for e in entity])
        if entity_type_1 == 'airport_code':
            sql = "SELECT DISTINCT flight_id FROM flight WHERE flight.from_airport IN %s" % (
                values)
        else:
            # city_name
            sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.from_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE city_1.city_name IN %s" % (
                values)
        results = get_result(sql)
    return results


def from_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight_1.from_airport, city_1.city_name FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.from_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE flight_1.flight_id in %s" % (
        flight_id)
    results = get_result(sql)
    return results


def to_2(entity):
    """
    _to(x,"mke:_ap"/"indianapolis:_ci")
    """
    if isinstance(entity, dict):
        entity_type_1, entity_value_1 = get_entity_value(entity)
        if entity_type_1 == 'airport_code':
            sql = "SELECT DISTINCT flight_id FROM flight WHERE flight.to_airport = '%s'" % (
                entity_value_1)
        elif entity_type_1 == 'city_name':
            sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.to_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE city_1.city_name = '%s'" % (
                entity_value_1)
        else:
            # entity_type == 'state_name':
            sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.to_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code JOIN state ON city_1.state_code = state.state_code WHERE state.state_name = '%s'" % (
                entity_value_1)
        results = get_result(sql)
    else:
        assert isinstance(entity, list)
        if len(entity) == 0:
            return list()
        entity_type_1, entity_value_1 = get_entity_value(entity[0])
        values = "(%s)" % ','.join(
            ['"%s"' % e[entity_type_1] for e in entity])
        if entity_type_1 == 'airport_code':
            sql = "SELECT DISTINCT flight_id FROM flight WHERE flight.to_airport IN %s" % (
                values)
        else:
            # city_name
            sql = "SELECT DISTINCT flight_1.flight_id FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.to_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE city_1.city_name IN %s" % (
                values)
        results = get_result(sql)
    return results


def to_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    if len(entities) == 0:
        return list()

    results = list()
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight_1.to_airport, city_1.city_name FROM flight AS flight_1 JOIN airport_service AS airport_service_1 ON flight_1.to_airport = airport_service_1.airport_code JOIN city AS city_1 ON airport_service_1.city_code = city_1.city_code WHERE flight_1.flight_id in %s" % (
        flight_id)
    results = get_result(sql)
    return results


def airport_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    if len(entities) == 0:
        return list()
    city_names = "(%s)" % ','.join(['"%s"' % e['city_name'] for e in entities])
    sql = 'SELECT airport_service.airport_code FROM airport_service JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name IN %s' % (
        city_names)
    results = get_result(sql)
    return results


def airline_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    if len(entities) == 0:
        return list()
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT airline_code FROM flight WHERE flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def booking_class_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT flight_fare.flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE class_of_service.class_description = '%s'" % entity_value_1
    results = get_result(sql)
    return results


def booking_class_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    if len(entities) == 0:
        return list()
    
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT class_of_service.class_description FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN class_of_service ON fare_basis.booking_class = class_of_service.booking_class WHERE flight_fare.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def from_airport_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)

    if entity_type_1 == 'city_name':
        sql = "SELECT DISTINCT T3.transport_type FROM airport_service AS T1 JOIN city AS T2 ON T1.city_code = T2.city_code JOIN ground_service AS T3 ON T1.airport_code = T3.airport_code WHERE T2.city_name = '%s'" % entity_value_1
    else:
        assert entity_type_1 == 'airport_code'
        sql = "SELECT DISTINCT ground_service_1.transport_type, ground_service_1.airport_code FROM ground_service ground_service_1 WHERE ground_service_1.airport_code = '%s'" % entity_value_1
    results = get_result(sql)
    return results


def to_city_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    assert entity_type_1 == 'city_name'
    sql = "SELECT DISTINCT ground_service_1.transport_type, city_1.city_name FROM ground_service AS ground_service_1 JOIN city AS city_1 ON ground_service_1.city_code = city_1.city_code WHERE city_1.city_name = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def meal_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    if entity_type_1 == 'meal_code':
        sql = "SELECT flight_id FROM flight WHERE meal_code = '%s'" % (entity_value_1)
    else:
        sql = "SELECT flight_id FROM flight JOIN food_service ON flight.meal_code = food_service.meal_code WHERE food_service.meal_description = '%s'" % (
            entity_value_1)
    results = get_result(sql)
    return results


def meal_code_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT flight_id FROM flight WHERE meal_code = '%s'" % (entity_value_1)
    results = get_result(sql)
    return results


def day_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code WHERE days.day_name = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def day_return_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN days ON fare_basis.basis_days = days.days_code WHERE days.day_name = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def year_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_id FROM flight JOIN days ON flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def day_arrival_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code WHERE days.day_name = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def day_number_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.day_number = %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def next_days_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 1 AND date_day.day_number BETWEEN 20 and %s" % (
        int(entity_value_1) + 20 )
    results = get_result(sql)
    return results


def month_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
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
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = %s" % (
        month_map[entity_value_1])
    results = get_result(sql)
    return results


def month_arrival_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
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
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = %s" % (
        month_map[entity_value_1])
    results = get_result(sql)
    return results


def month_return_2(entity):
    """
    _month_return(x, "june:_mn")
    :entity_type (flight_id, month)
    """
    entity_type_1, entity_value_1 = get_entity_value(entity)
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
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code JOIN days ON fare_basis.basis_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = %s" % (
        month_map[entity_value_1])
    results = get_result(sql)
    return results


def days_from_today_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT flight.flight_id FROM flight JOIN days on flight.flight_days = days.days_code JOIN date_day ON days.day_name = date_day.day_name WHERE date_day.year = 1991 AND date_day.month_number = 5 AND date_day.day_number = %s" % (
        int(entity_value_1) + 27)
    results = get_result(sql)
    return results


def stop_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT city.city_name, flight_stop.stop_airport FROM flight JOIN flight_stop ON flight.flight_id = flight_stop.flight_id JOIN airport_service ON flight_stop.stop_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE flight.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def stop_2(entity):

    if isinstance(entity, dict):
        entity_type_1, entity_value_1 = get_entity_value(entity)
        if entity_type_1 == 'city_name':
            sql = "SELECT flight.flight_id FROM flight JOIN flight_stop ON flight.flight_id = flight_stop.flight_id JOIN airport_service ON flight_stop.stop_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name = '%s'" % (
                entity_value_1)
        elif entity_type_1 == 'airport_code':
            sql = "SELECT flight_stop.flight_id FROM flight_stop WHERE flight_stop.stop_airport = '%s'" % (
                entity_value_1)
        results = get_result(sql)
    else:
        assert isinstance(entity, list)
        if len(entity) == 0:
            return list()
        entity_type_1, entity_value_1 = get_entity_value(entity[0])
        values = "(%s)" % ','.join(
            ['"%s"' % e[entity_type_1] for e in entity])

        if entity_type_1 == 'city_name':
            sql = "SELECT flight.flight_id FROM flight JOIN flight_stop ON flight.flight_id = flight_stop.flight_id JOIN airport_service ON flight_stop.stop_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE city.city_name IN %s" % (
                values)
        elif entity_type_1 == 'airport_code':
            sql = "SELECT flight_stop.flight_id FROM flight_stop WHERE flight_stop.stop_airport IN %s" % (
                values)
        results = get_result(sql)

    return results


def stop_arrival_time(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight_stop.arrival_time, city.city_name FROM flight_stop JOIN airport_service ON flight_stop.stop_airport = airport_service.airport_code JOIN city ON city.city_code = airport_service.city_code WHERE flight_stop.flight_id IN %s" % (flight_id)
    return get_result(sql)


def stops(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight_id, stops FROM flight WHERE flight.flight_id IN %s" % (flight_id)
    return get_result(sql)


def stops_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_id FROM flight WHERE stops = %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def class_type_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT flight_fare.flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN fare_basis ON fare.fare_basis_code = fare_basis.fare_basis_code WHERE fare_basis.class_type = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def fare_basis_code_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_id FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE fare.fare_basis_code = '%s'" % (entity_value_1)
    results = get_result(sql)
    return results


def fare_basis_code(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT fare.fare_basis_code FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id WHERE flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def has_meal(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()
    
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight_id FROM flight WHERE meal_code is not NULL AND flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def has_stops(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()
    
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = 'SELECT T1.flight_id FROM flight AS T1 JOIN flight_stop AS T2 ON T1.flight_id = T2.flight_id WHERE T1.flight_id IN %s' % (
        flight_id)
    results = get_result(sql)
    return results


def less_than_fare_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE fare.one_direction_cost < %s" % (entity_value_1)
    results = get_result(sql)
    return results


def fare_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE fare.one_direction_cost = '%s'" % (
        entity_value_1)
    results = get_result(sql)
    return results


def fare(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight.flight_id, fare.one_direction_cost FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE flight.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def fare_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()
    
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT flight.flight_id, fare.one_direction_cost, flight.departure_time FROM flight JOIN flight_fare ON flight.flight_id = flight_fare.flight_id JOIN fare ON fare.fare_id = flight_fare.fare_id WHERE flight.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def ground_fare(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    transport_types = "(%s)" % ','.join(['"%s"' % e['transport_type'] for e in entities])
    sql = "SELECT ground_fare FROM ground_service WHERE transport_type IN %s" % (
        transport_types)
    results = get_result(sql)
    return results


def aircraft_1(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT equipment_sequence.aircraft_code FROM flight JOIN equipment_sequence ON flight.aircraft_code_sequence = equipment_sequence.aircraft_code_sequence WHERE flight.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def flight_aircraft(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight.flight_id, equipment_sequence.aircraft_code FROM flight JOIN equipment_sequence ON flight.aircraft_code_sequence = equipment_sequence.aircraft_code_sequence WHERE flight.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def flight_airline(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    results = list()
    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight.flight_id, airline_code FROM flight WHERE flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def departure_time_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time = %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def departure_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_1.departure_time FROM flight flight_1 WHERE flight_1.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def arrival_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_1.arrival_time FROM flight flight_1 WHERE flight_1.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def arrival_time_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.arrival_time = %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def approx_return_time_2(entity):
    return approx_arrival_time_2(entity)


def approx_arrival_time_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    processed_arrival_time = entity_value_1
    if len(processed_arrival_time) == 4:
        if processed_arrival_time[2:] == '00':
            start_time = "%d%d" % (int(processed_arrival_time[:2]) - 1, 30)
            end_time = "%d%d" % (int(processed_arrival_time[:2]), 30)
        elif processed_arrival_time[2:] == '15':
            start_time = "%d%d" % (int(processed_arrival_time[:2]) - 1, 45)
            end_time = "%d%d" % (int(processed_arrival_time[:2]), 45)
        elif processed_arrival_time[2:] == '30':
            start_time = "%d00" % (int(processed_arrival_time[:2]))
            end_time = "%d00" % (int(processed_arrival_time[:2]) + 1)
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
            start_time = "%d00" % (int(processed_arrival_time[:1]))
            end_time = "%d00" % (int(processed_arrival_time[:1]) + 1)
        else:
            assert processed_arrival_time[1:] == '45'
            start_time = "%d%d" % (int(processed_arrival_time[:1]), 15)
            end_time = "%d%d" % (int(processed_arrival_time[:1]) + 1, 15)
    sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.arrival_time >= %s AND flight_1.arrival_time <= %s" % (
        start_time, end_time)
    results = get_result(sql)
    return results


def airline_name(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    results = list()
    if len(entities) == 0:
        return list()
    flight_id = "(%s)" % ','.join(
            ['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT airline_name FROM flight JOIN airline ON flight.airline_code = airline.airline_code WHERE flight.flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    return results


def flight_fare(argument):
    return fare(argument)


def restriction_code(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(
        ['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT restriction.restriction_code FROM flight_fare JOIN fare ON flight_fare.fare_id = fare.fare_id JOIN restriction ON fare.restriction_code = restriction.restriction_code WHERE flight_fare.flight_id IN %s" % (
        flight_id)
    return get_result(sql)


def approx_departure_time_2(entity):
    """
    _approx_departure_time()
    """
    entity_type_1, entity_value_1 = get_entity_value(entity)
    processed_departure_time = entity_value_1
    if len(processed_departure_time) == 4:
        if processed_departure_time[2:] == '00':
            start_time = "%d%d" % (int(processed_departure_time[:2]) - 1, 30)
            end_time = "%d%d" % (int(processed_departure_time[:2]), 30)
        elif processed_departure_time[2:] == '15':
            start_time = "%d%d" % (int(processed_departure_time[:2]) - 1, 45)
            end_time = "%d%d" % (int(processed_departure_time[:2]), 45)
        elif processed_departure_time[2:] == '30':
            start_time = "%d00" % (int(processed_departure_time[:2]))
            end_time = "%d00" % (int(processed_departure_time[:2]) + 1)
            print(start_time, end_time)
        else:
            assert processed_departure_time[2:] == '45'
            start_time = "%d%d" % (int(processed_departure_time[:2]), 15)
            end_time = "%d%d" % (int(processed_departure_time[:2]) + 1, 15)
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time >= %s AND flight_1.departure_time <= %s" % (
            start_time, end_time)
    elif len(processed_departure_time) == 3:
        if processed_departure_time[1:] == '00':
            start_time = "%d%d" % (int(processed_departure_time[:1]) - 1, 30)
            end_time = "%d%d" % (int(processed_departure_time[:1]), 30)
        elif processed_departure_time[1:] == '15':
            start_time = "%d%d" % (int(processed_departure_time[:1]) - 1, 45)
            end_time = "%d%d" % (int(processed_departure_time[:1]), 45)
        elif processed_departure_time[1:] == '30':
            start_time = "%d00" % (int(processed_departure_time[:1]))
            end_time = "%d00" % (int(processed_departure_time[:1]) + 1)
        else:
            assert processed_departure_time[1:] == '45'
            start_time = "%d%d" % (int(processed_departure_time[:1]), 15)
            end_time = "%d%d" % (int(processed_departure_time[:1]) + 1, 15)
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE flight_1.departure_time >= %s AND flight_1.departure_time <= %s" % (
            start_time, end_time)
    elif processed_departure_time == "0":
        start_time = "2330"
        end_time = "30"
        sql = "SELECT DISTINCT flight_1.flight_id FROM flight flight_1 WHERE (flight_1.departure_time >= %s OR flight_1.departure_time <= %s)" % (
            start_time, end_time)
    results = get_result(sql)
    return results


def larger_than_stops_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight_id FROM flight WHERE stops > %s" % (
        entity_value_1)
    results = get_result(sql)
    return results


def larger_than_arrival_time_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight WHERE arrival_time > %s" % entity_value_1
    results = get_result(sql)
    return results


def less_than_arrival_time_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight WHERE arrival_time < %s" % entity_value_1
    results = get_result(sql)
    return results


def larger_than_departure_time_2(entity):
    if isinstance(entity, dict):
        entity_type_1, entity_value_1 = get_entity_value(entity)
        sql = "SELECT DISTINCT flight.flight_id FROM flight WHERE departure_time > %s" % entity_value_1
        results = get_result(sql)
    else:
        assert isinstance(entity, list)
        flight_ids = "(%s)" % ','.join(
            ['"%s"' % e['flight_id'] for e in entity])
        sql = "SELECT DISTINCT flight.flight_id FROM flight WHERE departure_time > (SELECT MAX(T.departure_time) FROM flight AS T WHERE T.flight_id IN %s)" % flight_ids
        results = get_result(sql)
    return results


def less_than_departure_time_2(entity):
    entity_type_1, entity_value_1 = get_entity_value(entity)
    sql = "SELECT DISTINCT flight.flight_id FROM flight WHERE departure_time < %s" % entity_value_1
    results = get_result(sql)
    return results


def larger_than_capacity_2(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    # flight id
    valid_key = ''
    if 'aircraft_code' in entities[0]:
        valid_key = 'aircraft_code'
    else:
        raise Exception("Invalid key in larger_than_capacity_2")

    values = "(%s)" % ','.join(['"%s"' % e[valid_key] for e in entities])
    
    sql = "SELECT DISTINCT aircraft_1.aircraft_code FROM aircraft aircraft_1 WHERE aircraft_1.capacity > (SELECT MAX(T.capacity) FROM aircraft AS T WHERE T.aircraft_code IN %s)" % values
    results = get_result(sql)
    return results


def intersection(*args):
    keys = {}
    all_entities = list()
    for arg in args:
        if len(arg) == 0:
            return list()
        if isinstance(arg, dict):
            if len(keys) == 0:
                keys = set(arg.keys())
            else:
                keys &= set(arg.keys())
        else:
            assert isinstance(arg, list) and isinstance(arg[0], dict)
            all_entities += arg
            if len(keys) == 0:
                keys = set(arg[0].keys())
            else:
                keys &= set(arg[0].keys())
    if len(keys) == 0:
        return list()
    valid_key = list(keys)[0]

    results = set()
    for aidx, arg in enumerate(args):
        tmp = set()
        if isinstance(arg, list):
            for a in arg:
                tmp.add(a[valid_key])
        else:
            tmp.add(arg[valid_key])
        if aidx == 0:
            results = tmp
        else:
            results &= tmp

    return_results = list()
    for r in results:
        info = {valid_key: r}
        if valid_key == 'transport_type':
            for e in all_entities:
                if valid_key in e and e[valid_key] == r:
                    info.update(e)
        return_results.append(info)

    return return_results


def not_(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    # flight id
    valid_key = ''
    if 'flight_id' in entities[0]:
        valid_key = 'flight_id'
    elif 'airline_code' in entities[0]:
        valid_key = 'airline_code'
    elif 'aircraft_code' in entities[0]:
        valid_key = 'aircraft_code'
    elif 'city_name' in entities[0]:
        valid_key = 'city_name'
    else:
        raise Exception("Invalid key in Not")

    values = "(%s)" % ','.join(['"%s"' % e[valid_key] for e in entities])
    if valid_key == 'flight_id':
        sql = 'SELECT flight_id FROM flight WHERE flight_id NOT IN %s' % values
    elif valid_key == 'airline_code':
        sql = "SELECT distinct airline_code FROM airline WHERE airline_code NOT IN %s" % values
    elif valid_key == 'aircraft_code':
        sql = "SELECT distinct aircraft_code FROM aircraft WHERE aircraft_code NOT IN %s" % values
    elif valid_key == 'city_name':
        sql = "SELECT distinct city_name FROM city WHERE city_name NOT IN %s" % values
    results = get_result(sql)
    return results


def or_(*args):
    keys = {}
    for arg in args:
        if len(arg) == 0:
            return list()
        if isinstance(arg, dict):
            if len(keys) == 0:
                keys = set(arg.keys())
            else:
                keys &= set(arg.keys())
        else:
            assert isinstance(arg, list) and isinstance(arg[0], dict)
            if len(keys) == 0:
                keys = set(arg[0].keys())
            else:
                keys &= set(arg[0].keys())
    if len(keys) == 0:
        return list()
    valid_key = list(keys)[0]

    results = set()
    for aidx, arg in enumerate(args):
        tmp = set()
        if isinstance(arg, list):
            for a in arg:
                tmp.add(a[valid_key])
        else:
            tmp.add(arg[valid_key])
        if aidx == 0:
            results = tmp
        else:
            results |= tmp

    return_results = list()
    for r in results:
        return_results.append({valid_key: r})
    return return_results


def count_(argument):
    if isinstance(argument, list):
        return len(argument)
    if argument is not None:
        return 1
    return 0


def max_(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    valid_key = None
    keys = set()
    for e in entities:
        keys |= set(e.keys())
    keys = keys & {'one_direction_cost', 'arrival_time', 'departure_time'}
    if len(keys) > 0:
        valid_key = list(keys)[0]
        print(valid_key)
        max_value = max([e[valid_key] for e in entities])
        return max_value
    else:
        return 0.0


def min_(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    valid_key = None
    keys = set()
    for e in entities:
        keys |= set(e.keys())
    keys = keys & {'one_direction_cost', 'arrival_time', 'departure_time'}
    if len(keys) > 0:
        valid_key = list(keys)[0]
        print(valid_key)
        min_value = min([e[valid_key] for e in entities])
        return min_value
    else:
        return 0.0


def argmin_departure_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "select flight.flight_id, flight.departure_time FROM flight WHERE flight.flight_id IN %s" % flight_id
    results = get_result(sql)
    min_time = min([r['departure_time'] for r in results])
    return_results = [r for r in results if r['departure_time'] == min_time]
    return return_results


def argmax_arrival_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "select flight.flight_id, flight.arrival_time FROM flight WHERE flight.flight_id IN %s" % flight_id
    results = get_result(sql)
    max_time = max([r['arrival_time'] for r in results])
    return_results = [r for r in results if r['arrival_time'] == max_time]
    return return_results


def argmax_departure_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "select flight.flight_id, flight.departure_time FROM flight WHERE flight.flight_id IN %s" % flight_id
    results = get_result(sql)
    max_time = max([r['departure_time'] for r in results])
    return_results = [r for r in results if r['departure_time'] == max_time]
    return return_results


def argmin_arrival_time(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "select flight.flight_id, flight.arrival_time FROM flight WHERE flight.flight_id IN %s" % flight_id
    results = get_result(sql)
    min_time = min([r['arrival_time'] for r in results])
    return_results = [r for r in results if r['arrival_time'] == min_time]
    return return_results


def argmin_fare(argument):
    results = fare(argument)
    if len(results) == 0:
        return list()
    min_fare = min([r['one_direction_cost'] for r in results])
    return_results = [
        r for r in results if r['one_direction_cost'] == min_fare]
    return return_results


def argmax_fare(argument):
    results = fare(argument)
    max_fare = max([r['one_direction_cost'] for r in results])
    return_results = [
        r for r in results if r['one_direction_cost'] == max_fare]
    return return_results


def argmax_capacity(argument):
    results = capacity(argument)
    max_capacity = max([r['capacity'] for r in results])
    return_results = [
        r for r in results if r['capacity'] == max_capacity]
    return return_results


def argmin_capacity(argument):
    results = capacity(argument)
    min_capacity = min([r['capacity'] for r in results])
    return_results = [
        r for r in results if r['capacity'] == min_capacity]
    return return_results


def sum_capacity(argument):
    results = capacity(argument)
    total_capacity = sum([r['capacity'] for r in results])
    return total_capacity


def sum_stops(argument):
    results = stops(argument)
    total_stops = sum([r['stops'] for r in results])
    return total_stops


def argmax_stops(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_id, stops FROM flight WHERE flight_id IN %s" % (flight_id)
    results = get_result(sql)
    max_stops = max([r['stops'] for r in results])
    return_results = [
        r for r in results if r['stops'] == max_stops]
    return return_results


def argmin_stops(argument):

    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)

    if len(entities) == 0:
        return list()

    flight_id = "(%s)" % ','.join(['"%s"' % e['flight_id'] for e in entities])
    sql = "SELECT DISTINCT flight_id, stops FROM flight WHERE flight_id IN %s" % (
        flight_id)
    results = get_result(sql)
    min_stops = min([r['stops'] for r in results])
    return_results = [
        r for r in results if r['stops'] == min_stops]
    return return_results


def argmin_miles_distant_2(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    if len(entities) == 0:
        return list()

    assert 'airport_code' in entities[0]
    key = 'airport_code'
    values = "(%s)" % ','.join(
        ['"%s"' % e[key] for e in entities])
    sql = "SELECT airport_service.miles_distant, airport_service.airport_code FROM airport_service JOIN city ON city.city_code = airport_service.city_code WHERE airport_service.airport_code IN %s AND airport_service.miles_distant > 0 ORDER BY airport_service.miles_distant ASC LIMIT 1" % values
    print(sql)
    results = get_result(sql)
    return results


def argmin_time_elapsed(argument):
    results = time_elapsed(argument)
    min_time = min([r['time_elapsed'] for r in results])
    return_results = [
        r for r in results if r['time_elapsed'] == min_time]
    return return_results


def argmax_count(argument):
    if isinstance(argument, dict):
        entities = [argument]
    elif isinstance(argument, list):
        entities = argument
    else:
        raise Exception("Not Supported Argument Type", argument)
    
    if len(entities) == 0:
        return list()

    assert 'airline_code' in entities[0]
    key = 'airline_code'
    values = "(%s)" % ','.join(
        ['"%s"' % e[key] for e in entities])
    sql = "SELECT airline_code FROM flight WHERE airline_code IN %s GROUP BY airline_code order by count(DISTINCT flight_id) LIMIT 1" % values
    results = get_result(sql)
    return results


def equals(arguemnt_1, arguemnt_2):
    if isinstance(arguemnt_1, list):
        entities_1 = arguemnt_1
    elif isinstance(arguemnt_1, dict):
        entities_1 = [arguemnt_1]
    if isinstance(arguemnt_2, list):
        entities_2 = arguemnt_2
    elif isinstance(arguemnt_2, dict):
        entities_2 = [arguemnt_2]
    
    for e1 in entities_1:
        is_found = False
        for e2 in entities_2:
            is_match = True
            for k, v in e1.items():
                if k not in e2 or e2[k].lower() != v.lower():
                    is_match = False
            if is_match:
                is_found = True
                break
        if not is_found:
            return False
    return True


def named_1(values):
    return values


if __name__ == '__main__':
    values = answer(argmin_capacity(aircraft(intersection(not_(turboprop(
        aircraft_all())), larger_than_capacity_2(turboprop(aircraft_all()))))))
    print(values)

    data = list()
    with open('../../../data/atis/atis_funql_train.tsv', 'r') as f:
        for line in f:
            line = line.strip()
            data.append(line.split('\t'))
    for idx, (question, funql) in enumerate(data):
        print(idx)
        print(question)
        print(funql)
        expression = transform(funql)
        print(expression)
        results = eval(expression)
        print(results)
        print('====\n\n')
