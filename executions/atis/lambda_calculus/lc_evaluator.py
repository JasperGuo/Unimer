# coding=utf8

import logging
from pprint import pprint
from multiprocessing import Process, Manager
from .query import *
from .transform import transform_lambda_calculus


class TimeoutException(Exception):
    pass


def get_result(lambda_calculus, return_dict):
    python_lf, _, _, _= transform_lambda_calculus(
        lambda_calculus)
    print(lambda_calculus)
    print(python_lf)
    try:
        results = eval(python_lf)
    except:
        logging.error("Exception", exc_info=True)
        return_dict['is_valid'] = False
    else:
        return_dict['is_valid'] = True

        if isinstance(results, list):
            updated_results = list()
            for r in results:
                if isinstance(r, dict):
                    updated_results.append(r)
                else:
                    assert isinstance(r, tuple)
                    new_r, names = dict(), dict()
                    for idx, v in enumerate(r):
                        assert isinstance(v, dict)
                        for k, value in v.items():
                            if k in names:
                                names[k] += 1
                                key = "%s_%d" % (k, names[k])
                            else:
                                key = k
                                names[k] = 0
                            assert key not in new_r
                            new_r[key] = value
                    updated_results.append(new_r)
            results = updated_results

        return_dict['results'] = results
    close_connection()
    return return_dict


def get_result_with_time_limit(lambda_calculus, time):
    manager = Manager()
    return_dict = manager.dict()
    p = Process(target=get_result, args=(lambda_calculus, return_dict))
    p.start()
    p.join(time)
    if p.is_alive():
        p.terminate()
        raise TimeoutException("Timeout")
    is_valid = return_dict['is_valid']
    if is_valid:
        return return_dict['results']
    else:
        raise Exception("Lambda Calculus Execution Error")


def compare_lambda_calculus(lc_1, lc_2, time_limit=600):
    try:
        lc_1_results = get_result_with_time_limit(lc_1, time_limit)
        lc_2_results = get_result_with_time_limit(lc_2, time_limit)
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
    lc_1 = '(_lambda x (_lambda y (_and (_aircraft_code x y) (_airline x dl:_al) (_flight x) (_from x seattle:_ci) (_to x salt_lake_city:_ci))))'
    lc_2 = '(_lambda x (_lambda y (_and (_aircraft_code x y) (_airline x dl:_al) (_flight x) (_from x seattle:_ci) (_to x salt_lake_city:_ci))))'
    formatted_results = get_result_with_time_limit(lc_1, 600)
    pprint(formatted_results)
    print(compare_lambda_calculus(lc_1, lc_2))
