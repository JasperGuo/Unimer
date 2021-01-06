# coding=utf8

from multiprocessing import Process, Manager
import re
import mysql.connector
from pprint import pprint


class TimeoutException(Exception):
    pass


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


def get_result(sql, db):
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


def get_result_process_func(sql, return_dict):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123456",
        database="atis",
        auth_plugin='mysql_native_password'
    )
    try:
        results = get_result(sql, db)
    except Exception as e:
        print(e)
        return_dict['is_valid'] = False
    else:
        return_dict['is_valid'] = True
        return_dict['results'] = results


def get_result_with_time_limit(sql, time):
    manager = Manager()
    return_dict = manager.dict()
    p = Process(target=get_result_process_func, args=(sql, return_dict))
    p.start()
    p.join(time)
    if p.is_alive():
        p.terminate()
        raise TimeoutException("Timeout")
    is_valid = return_dict['is_valid']
    if is_valid:
        return return_dict['results']
    else:
        raise Exception("SQL Execution Error")


def compare_sqls(sql_1, sql_2, timeout=300):
    try:
        sql_1_results = get_result_with_time_limit(sql_1, 300)
        sql_2_results = get_result_with_time_limit(sql_2, 300) 
    except Exception as e:
        return False

    if len(sql_1_results) != len(sql_2_results):
        return False

    for sql_1_row in sql_1_results:
        for sql_2_row in sql_2_results:
            is_same = True
            for key, value in sql_1_row.items():
                if key not in sql_2_row or sql_2_row[key] != value:
                    is_same = False
            if is_same:
                sql_2_results.remove(sql_2_row)
                break
        else:
            return False
    return True


if __name__ == '__main__':
    sql_1 = "select distinct flight_1.flight_id from flight flight_1 where (flight_1.airline_code = 'aa' and (flight_1.from_airport in (select airport_service_1.airport_code from airport_service airport_service_1 where airport_service_1.city_code in (select city_1.city_code from city city_1 where city_1.city_name = 'miami')) and flight_1.to_airport in (select airport_service_1.airport_code from airport_service airport_service_1 where airport_service_1.city_code in (select city_1.city_code from city city_1 where city_1.city_name = 'chicago'))));"
    # print(compare_sqls(sql_1, sql_2))
    formatted_results = get_result_with_time_limit(sql_1, 60)
    pprint(formatted_results)
