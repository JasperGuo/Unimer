# coding=utf8

import logging
from .query import *
from .transform import transform


def get_result(funql):
    python_lf = transform(funql)
    return_dict = dict()
    try:
        results = eval(python_lf)
    except:
        logging.error("Exception", exc_info=True)
        return_dict['is_valid'] = False
    else:
        return_dict['is_valid'] = True
        return_dict['results'] = results
    close_connection()
    return return_dict


def compare_funql(funql_1, funql_2, time_limit=600):
    try:
        lc_1_results = get_result(funql_1)
        lc_2_results = get_result(funql_2)
    except Exception as e:
        return False

    if type(lc_1_results) != type(lc_2_results):
        return False

    if isinstance(lc_1_results, list):

        if len(lc_1_results) != len(lc_2_results):
            return False

        for lc_1_row in lc_1_results:
            for lc_2_row in lc_2_results:
                is_same = True
                used_keys = set()
                for key, value in lc_1_row.items():
                    if key not in lc_2_row:
                        is_same = False
                    else:
                        # Key in lc_2_row
                        # Find key
                        if key.startswith("<lambda>"):
                            for k2, v2 in lc_2_row.items():
                                if k2 not in used_keys and k2.startswith("<lambda>") and value == v2:
                                    used_keys.add(k2)
                                    break
                            else:
                                is_same = False
                        else:
                            if lc_2_row[key] != value:
                                is_same = False
                if is_same:
                    lc_2_results.remove(lc_2_row)
                    break
            else:
                return False
        return True
    else:
        return lc_1_results == lc_2_results


if __name__ == '__main__':
    funql_1 = 'answer(intersection(_from_2(city_name(milwaukee)),_to_2(city_name(phoenix)),_day_2(day(saturday))))'
    funql_2 = 'answer(intersection(_to_2(city_name(phoenix)), _from_2(city_name(milwaukee)),_day_2(day(saturday))))'
    print(compare_funql(funql_1, funql_2))
