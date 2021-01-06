# coding=utf8

ROOT_RULE = 'statement -> [expression]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['(expression ws)']
GRAMMAR_DICTIONARY['expression'] = ['(application)', '(abstraction)', '(constant)', '(variable)']
GRAMMAR_DICTIONARY['abstraction'] = ['("(" ws "lambda" wsp variable_definition wsp expression ws ")")']
GRAMMAR_DICTIONARY['application'] = ['("(" ws function ws ")")']
GRAMMAR_DICTIONARY['function'] = [
    '("company" wsp expression wsp expression)',
    '("area" wsp expression wsp expression)',
    '("platform" wsp expression wsp expression)',
    '("recruiter" wsp expression wsp expression)',
    '("language" wsp expression wsp expression)',
    '("title" wsp expression wsp expression)',
    '("application" wsp expression wsp expression)',
    '("loc" wsp expression wsp expression)',
    '("country" wsp expression wsp expression)',
    '("des_exp" wsp expression wsp expression)',
    '("des_exp" wsp expression)',
    '("req_exp" wsp expression wsp expression)',
    '("req_exp" wsp expression)',
    '("des_deg" wsp expression wsp expression)',
    '("des_deg" wsp expression)',
    '("req_deg" wsp expression wsp expression)',
    '("req_deg" wsp expression)',
    '("job" wsp expression)',
    '("and_" wsp application wsp polyvariadic_expression)',
    '("or_" wsp application wsp polyvariadic_expression)',
    '("not_" wsp expression)',
    '("exists_" wsp variable_definition wsp expression)',
    '("salary_greater_than" wsp expression wsp expression wsp expression)',
    '("salary_less_than" wsp expression wsp expression wsp expression)',
]
GRAMMAR_DICTIONARY['polyvariadic_expression'] = ['(application ws polyvariadic_expression)', '""']
GRAMMAR_DICTIONARY['variable'] = ['"$0"', '"$1"']
GRAMMAR_DICTIONARY['variable_definition'] = ['"$0:e"', '"$1:e"']
GRAMMAR_DICTIONARY['constant'] = ['salary_value', 'string']
GRAMMAR_DICTIONARY['string'] = [
    '"\'Senior Development Engineer\'"', '"\'Lockheed Martin Aeronautics\'"',
    '"\'Senior Consulting Engineer\'"', '"\'Senior Software Developer\'"', '"\'oil pipeline modeling\'"', '"\'NetWare Administrator\'"', '"\'Verification Engineer\'"', '"\'Systems Administrator\'"', '"\'Manufacturing Manager\'"', '"\'National Instruments\'"', '"\'System Administrator\'"', '"\'research assistant\'"', '"\'Software Developer\'"', '"\'Ic Design Engineer\'"', '"\'Applied Materials\'"', '"\'Software Engineer\'"', '"telecommunications"', '"\'data warehousing\'"', '"\'silicon graphics\'"', '"\'Systems Analyst\'"', '"\'Project Manager\'"', '"speedy3dgraphics"', '"\'microsoft word\'"', '"\'Web Developer\'"', '"\'Test Engineer\'"', '"\'device driver\'"', '"\'visual basic\'"', '"\'Sql Engineer\'"', '"\'3d graphics\'"', '"\'software qa\'"', '"\'san antonio\'"', '"client/server"', '"\'windows nt\'"', '"\'windows 95\'"', '"\'visual j++\'"', '"\'visual c++\'"', '"\'los alamos\'"', '"\'sql server\'"', '"\'Phil Smith\'"', '"powerbuilder"', '"playstation"', '"california"', '"washington"', '"networking"', '"management"', '"commodores"', '" Microsoft"', '"\'cobol ii\'"', '"\'san jose\'"', '"statistics"', '"Consultant"', '"\'new york\'"', '"Programmer"', '"animation"', '"Developer"', '"nashville"', '"Microsoft"', '"colorado"', '"internet"', '"engineer"', '"graphics"', '"database"', '"ethernet"', '"assembly"', '"Longhorn"', '"network"', '"autocad"', '"Trilogy"', '"houston"', '"seattle"', '"solaris"', '"haskell"', '"windows"', '"fortran"', '"tcp/ip"', '"master"', '"prolog"', '"apache"', '"novell"', '"dallas"', '"Boeing"', '"delphi"', '"oracle"', '"canada"', '"Tivoli"', '"tcl/tk"', '"austin"', '"pascal"', '"boston"', '"Compaq"', '"intern"', '"texas"', '"games"', '"tulsa"', '"cobol"', '"Apple"', '"pdp11"', '"shell"', '"linux"', '"latex"', '"excel"', '"Dell"', '"odbc"', '"BSCS"', '"lisp"', '"perl"', '"MSEE"', '"vc++"', '"unix"', '"cics"', '"html"', '"java"', '"MSCS"', '"BSEE"', '"BACS"', '"IBM"', '"rpg"', '"com"', '"ibm"', '"mfc"', '"usa"', '"LCS"', '"vax"', '"sql"', '"c++"', '"sun"', '"JPL"', '"lan"', '"wan"', '"ole"', '"PhD"', '"web"', '"mvs"', '"ada"', '"mac"', '"MBA"', '"aix"', '"vms"', '"gui"', '"x86"', '"ai"', '"BS"', '"BA"', '"10"', '"HP"', '"MA"', '"pc"', '"vb"', '"hour"', '"year"', '"month"', '"c"', '"1"', '"4"', '"3"', '"2"', '"5"',]
GRAMMAR_DICTIONARY['salary_value'] = [
    '"100000"', '"70000"', '"65000"', '"50000"', '"80000"',
    '"30000"', '"90000"', '"60000"', '"40000"', '"10000"', '"5000"', '"20"'
]

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY["wsp"] = ['~"\s+"i']

COPY_TERMINAL_SET = {'string', 'salary_value'}
