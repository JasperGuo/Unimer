# coding=utf8

import os
import re
import pandas as pd
from pprint import pprint

number_pattern = re.compile('[+-]?([0-9]*[.])?[0-9]+')


if __name__ == '__main__':
    path = '../../data/geo/sql_data'
    terminals = set()
    terminal_dict = dict()
    for filename in os.listdir(path):
        table_name = filename.split('.')[0]
        filepath = os.path.join(path, filename)
        df = pd.read_csv(filepath)
        for column in df.columns:
            if column not in terminal_dict:
                terminal_dict[column] = list()
            values = df[column].tolist()
            v = values[0]
            if number_pattern.match(str(v).strip()):
                # number
                for i in values:
                    if '.' in str(i):
                        # float
                        terminal_dict[column].append('"%s"' % str(float(i)))
                        terminals.add('"%s"' % str(float(i)))
                    else:
                        terminal_dict[column].append('"%s"' % str(int(i)))
                        terminals.add('"%s"' % str(int(i)))
            else:
                # str
                for i in values:
                    i = i.strip()
                    terminal_dict[column].append('"%s"' % i)
                    terminals.add('"%s"' % i)
    # print(terminals)
    for terminal, values in terminal_dict.items():
        terminal_dict[terminal] = list(set(values))
    pprint(terminal_dict)
