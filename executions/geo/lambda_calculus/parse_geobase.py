# coding=utf8

import re


def parse_state(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('state('):
                info = line[len('state('):-2]
                # print(info)
                infos = info.split(',')
                for idx, content in enumerate(infos):
                    if "'" in content:
                        infos[idx] = content.replace("'", '"')
                new_infos = ["State"]
                state_abbre = None
                for idx, content in enumerate(infos):
                    if idx == 6:
                        new_infos.append('[' + content + ',')
                    elif idx == 0:
                        # state_name
                        n = infos[idx]
                        if " " in n:
                            n = n.replace(" ", "_")
                        n = n[:-1] + ':s"'
                        new_infos.append(n)
                    elif idx == 1:
                        state_abbre = content.replace('"', '')
                        new_infos.append(content)
                    elif idx == 2:
                        # Capital
                        n = infos[idx]
                        if " " in n:
                            n = n.replace(" ", "_")
                        n = n[:-1] + '_%s:c"' % state_abbre
                        new_infos.append(n)
                    elif idx > 6:
                        new_infos.append(content + ',')
                    else:
                        new_infos.append(content)
                else:
                    new_infos[-1] = new_infos[-1][:-1]+']'

                # Process city
                string = " ".join(new_infos)
                cities = string[string.index('[')+1:string.index(']')]
                new_cities = list()
                for c in cities.split(","):
                    c = c.strip().replace(" ", "_")
                    new_cities.append(c[:-1] + '_%s:c"' % state_abbre)
                string = string[:string.index('[')+1] + ", ".join(new_cities) + ']'
                print(string  + ",")


def parse_city(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('city('):
                info = line[len('city('):-2]
                # print(info)
                infos = info.split(',')
                state_abbre = None
                for idx, content in enumerate(infos):
                    if "'" in content:
                        infos[idx] = content.replace("'", '"')
                        content = infos[idx]
                    if idx == 0:
                        # state_name
                        n = content
                        if " " in n:
                            n = n.replace(" ", "_")
                        n = n[:-1] + ':s"'
                        infos[idx] = n
                    elif idx == 1:
                        # abbre
                        state_abbre = content.replace('"', '')
                    elif idx == 2:
                        # city
                        n = content
                        if " " in n:
                            n = n.replace(" ", "_")
                        n = n[:-1] + '_%s:c"' % state_abbre
                        infos[idx] = n

                infos.insert(0, "City")
                print(" ".join(infos) + ",")


def parse_river(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('river(') and line.endswith('.'):
                info = line[len('river('):-2]
                info = info.replace("'", '"')
                lindex = info.index('[')
                rindex = info.index(']')
                infos = info.split(',')
                new_infos = ['River', infos[0][:-1].replace(" ", "_") + ':r"', infos[1], info[lindex:rindex+1]]

                string = " ".join(new_infos)
                states = string[string.index('[')+1:string.index(']')]
                new_states = list()
                for c in states.split(","):
                    c = c.strip().replace(" ", "_")
                    new_states.append(c[:-1] + ':s"')
                string = string[:string.index('[')+1] + ", ".join(new_states) + ']'
                print(string  + ",")


def parse_border(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('border(') and line.endswith('.'):
                info = line[len('border('):-2]
                info = info.replace("'", '"')
                lindex = info.index('[')
                rindex = info.index(']')
                infos = info.split(',')
                new_infos = ['Border', infos[0][:-1].replace(" ", "_") + ':s"', infos[1], info[lindex:rindex+1]]

                string = " ".join(new_infos)
                states = string[string.index('[')+1:string.index(']')]
                new_states = list()
                for c in states.split(","):
                    c = c.strip().replace(" ", "_")
                    new_states.append(c[:-1] + ':s"')
                string = string[:string.index('[')+1] + ", ".join(new_states) + ']'
                print("    " + string  + ",")


def parse_highlow(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('highlow(') and line.endswith('.'):
                info = line[len('highlow('):-2]
                info = info.replace("'", '"')
                infos = info.split(',')
                infos.insert(0, 'HighLow')

                infos[1] = infos[1][:-1].replace(" ", "_") + ':s"'
                infos[3] = infos[3][:-1].replace(" ", "_") + ':lo"'
                infos[5] = infos[5][:-1].replace(" ", "_") + ':lo"'
                print(" ".join(infos) + ",")


def parse_mountain(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('mountain(') and line.endswith('.'):
                info = line[len('mountain('):-2]
                info = info.replace("'", '"')
                infos = info.split(',')
                infos.insert(0, 'Mountain')

                infos[1] = infos[1][:-1].replace(" ", "_") + ':s"'
                infos[3] = infos[3][:-1].replace(" ", "_") + ':m"'
                print(" ".join(infos) + ",")


def parse_road(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('road(') and line.endswith('.'):
                info = line[len('road('):-2]
                info = info.replace("'", '"')
                index = info.index(',')
                info = "RoadInfo " + info[:index] + " " + info[index+1:]+","
                print(info)


def parse_lake(path):
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('lake(') and line.endswith('.'):
                info = line[len('lake('):-2]
                info = info.replace("'", '"')
                lindex = info.index('[')
                rindex = info.index(']')
                infos = info.split(',')
                new_infos = ['Lake', infos[0][:-1].replace(" ", "_") + ':l"', infos[1], info[lindex:rindex+1]]

                string = " ".join(new_infos)
                states = string[string.index('[')+1:string.index(']')]
                new_states = list()
                for c in states.split(","):
                    c = c.strip().replace(" ", "_")
                    new_states.append(c[:-1] + ':s"')
                string = string[:string.index('[')+1] + ", ".join(new_states) + ']'
                print("    " + string  + ",")


if __name__ == '__main__':
    path = '../prolog/geobase.pl'
    parse_lake(path)