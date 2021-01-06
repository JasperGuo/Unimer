# coding=utf8

import re
import mysql.connector
from pprint import pprint


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="job",
    auth_plugin='mysql_native_password'
)


def parse_entry(value):
    first_index = value.index('(')
    last_index = value.rindex(')')
    table_name = value[:first_index]
    values = value[first_index + 1:last_index]
    values = values.split(',')
    formatted_values = list()
    for v in values:
        v = v.strip().replace("'", "").replace('"', "")
        v = re.sub(' +', ' ', v)
        if v == 'n/a':
            v = None
        elif re.match('^\d+$', v):
            v = int(v)
        formatted_values.append(v)
    return table_name, formatted_values


def parse(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    data = list()
    lidx = 0
    while lidx < len(lines):
        line = lines[lidx].strip()
        nlidx = lidx
        while nlidx < len(lines) and not lines[nlidx].strip().endswith('.'):
            nlidx += 1
        nlidx += 1
        info = ' '.join([l.strip() for l in lines[lidx:nlidx]])
        info = re.sub('\t', '', info)
        # print(info)
        data.append(info)
        lidx = nlidx
    value_dict = dict()
    for d in data:
        table_name, values = parse_entry(d)
        if values[0] == '':
            continue
        if table_name not in value_dict:
            value_dict[table_name] = list()
        value_dict[table_name].append(values)
    pprint(value_dict)

    # Validate
    for tn, values in value_dict.items():
        length = len(values[0])
        for vidx, v in enumerate(values):
            if length != len(v):
                # Hot fix
                assert tn == 'raw_area' and v[0] == '38f63940$0$20916@wodc7nh6.news.uu.net'
                values[vidx] = ['38f63940$0$20916@wodc7nh6.news.uu.net', 'atm,ip']
                print("Failed: ", tn, v)

    # Check Duplicate
    count = 0
    job_ids = set()
    for vidx, values in enumerate(value_dict['raw_job']):
        job_id = values[0]
        job_ids.add(job_id)
        for nidx, nvalues in enumerate(value_dict['raw_job']):
            if nidx != vidx and nvalues[0] == job_id:
                print("Duplicated")
                print(values)
                print(nvalues)
                print("===\n\n")
                count += 1

    # Ensure foreign key Constraints
    print(count)

    age_foreign_key_violate_count = 0
    for values in value_dict['raw_age']:
        if values[0] not in job_ids:
            print(values)
            age_foreign_key_violate_count += 1
    print(age_foreign_key_violate_count)




    return value_dict



if __name__ == '__main__':
    parse('./jobdata')
