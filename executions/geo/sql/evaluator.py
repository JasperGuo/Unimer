# coding=utf8

import re
import mysql.connector
from pprint import pprint


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="geo",
    auth_plugin='mysql_native_password'
)


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


def get_result(sql):
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


def compare_sqls(sql_1, sql_2):
    try:
        sql_1_results = get_result(sql_1)
        sql_2_results = get_result(sql_2)
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
    sql_1 = 'SELECT STATEalias0.POPULATION FROM STATE AS STATEalias0 WHERE STATEalias0.STATE_NAME = "texas" ;'
    # sql_2 = "select count(distinct flight_1.flight_id) from flight flight_1 , airport_service airport_service_1 , city city_1 , airport_service airport_service_2 , city city_2 , days days_1 , date_day date_day_1 where flight_1.from_airport = airport_service_1.airport_code and airport_service_1.city_code = city_1.city_code and city_1.city_name = 'san francisco' and (flight_1.to_airport = airport_service_2.airport_code and airport_service_2.city_code = city_2.city_code and city_2.city_name = 'philadelphia' and flight_1.flight_days = days_1.days_code and days_1.day_name = date_day_1.day_name and date_day_1.year = 1991 and date_day_1.month_number = 8 and date_day_1.day_number = 18);"
    # print(compare_sqls(sql_1, sql_2))
    formatted_results = get_result(sql_1)
    pprint(formatted_results)
