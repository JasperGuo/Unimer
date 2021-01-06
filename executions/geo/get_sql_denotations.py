# coding=utf8

from sql.evaluator import get_result


def evaluate(path):
    questions, logical_forms = list(), list()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            splits = line.split('\t')
            q, l = splits[0], splits[1]
            questions.append(q)
            logical_forms.append(l)

    with open('./sql_execution_results.tsv', 'w') as f:
        for question, lf in zip(questions, logical_forms):
            print(question)
            print(lf)
            formated_results = get_result(lf)
            results = list()
            for fr in formated_results:
                key = list(fr.keys())[0]
                results.append(fr[key])
            print(results)
            f.write("%s\t%s\n" % (question, str(results)))
            print('===\n\n')


if __name__ == '__main__':
    evaluate('../../data/geo/geo_sql_question_based_train.tsv')
