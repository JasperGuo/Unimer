# coding=utf8

import json
import argparse
from pprint import pprint


def main(path):
    with open(path, 'r', encoding='utf8') as f:
        for line in f:
            results = json.loads(json.loads(line))
            pprint(results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file', help='file that stores hyper-parameters', required=True)
    args = parser.parse_args()
    main(args.file)
