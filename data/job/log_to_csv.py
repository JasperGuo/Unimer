# coding=utf8

if __name__ == '__main__':
    questions, logical_forms = list(), list()
    with open("job_funql_train.log", 'r') as f:
        lines = f.readlines()
        lidx = 0
        while lidx < len(lines):
            line = lines[lidx]
            line = line.strip()
            print(lidx)
            if len(line) > 0:
                if line == "Incorrect FunQL":
                    lidx += 1
                    line = lines[lidx].strip()
                question = line
                lidx += 1
                lc = lines[lidx].strip()
                lidx += 1
                lf = lines[lidx].strip()
                print(question)
                print(lf)
                questions.append(question)
                logical_forms.append(lf)
                lidx += 1
                assert lines[lidx].startswith('==')
            lidx += 1
    with open("job_funql_train.tsv", 'w') as f:
        for question, logical_form in zip(questions, logical_forms):
            f.write("%s\t%s\n" % (question, logical_form))
