# coding=utf8

"""
FunQL Grammar
"""

ROOT_RULE = 'statement -> [answer]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['(answer ws)']
GRAMMAR_DICTIONARY['answer'] = ['("answer" ws "(" ws predicate ws ")" )']

GRAMMAR_DICTIONARY['predicate'] = [
    'meta', 'object', '"job(all)"', 'relation',
    '("intersect" ws "(" ws predicate ws "," ws conjunction ws ")")',
    '("or" ws "(" ws predicate ws "," ws predicate ws ")")',
    '("not" ws "(" ws predicate ws ")")',
]
GRAMMAR_DICTIONARY['conjunction'] = [
    '(predicate ws "," ws conjunction)',
    '(predicate)'
]
GRAMMAR_DICTIONARY['object'] = ['("const(" string ")")']
GRAMMAR_DICTIONARY['relation'] = [
    '("req_exp_1(" ws predicate ws ")")',
    '("req_exp_0(" ws predicate ws ")")',
    '("req_deg_1(" ws predicate ws ")")',
    '("req_deg_0(" ws predicate ws ")")',
    '("platform_1(" ws predicate ws ")")',
    '("platform_0(" ws predicate ws ")")',
    '("language_1(" ws predicate ws ")")',
    '("language_0(" ws predicate ws ")")',
    '("application_1(" ws predicate ws ")")',
    '("company_1(" ws predicate ws ")")',
    '("company_0(" ws predicate ws ")")',
    '("recruiter_1(" ws predicate ws ")")',
    '("des_deg_1(" ws predicate ws ")")',
    '("des_exp_1(" ws predicate ws ")")',
    '("des_exp_0(" ws predicate ws ")")',
    '("country_1(" ws predicate ws ")")',
    '("title_1(" ws predicate ws ")")',
    '("title_0(" ws predicate ws ")")',
    '("area_1(" ws predicate ws ")")',
    '("loc_1(" ws predicate ws ")")',
    '("loc_0(" ws predicate ws ")")',
    '("des_exp(" ws predicate ws ")")',
    '("des_deg(" ws predicate ws ")")',
    '("req_exp(" ws predicate ws ")")',
    '("req_deg(" ws predicate ws ")")',
    '("job(" ws predicate ws ")")',
]
GRAMMAR_DICTIONARY['meta'] = [
    '("salary_greater_than(" salary_value "," "year" ")")',
    '("salary_greater_than(" salary_value "," "hour" ")")',
    '("salary_greater_than(" salary_value "," "month" ")")',
    '("salary_less_than(" salary_value "," "year" ")")'
]

GRAMMAR_DICTIONARY['string'] = ['"\'Senior Development Engineer\'"', '"\'Lockheed Martin Aeronautics\'"', '"\'Senior Consulting Engineer\'"', '"\'Senior Software Developer\'"', '"\'oil pipeline modeling\'"', '"\'NetWare Administrator\'"', '"\'Verification Engineer\'"', '"\'Systems Administrator\'"', '"\'Manufacturing Manager\'"', '"\'National Instruments\'"', '"\'System Administrator\'"', '"\'research assistant\'"', '"\'Software Developer\'"', '"\'Ic Design Engineer\'"', '"\'Applied Materials\'"', '"\'Software Engineer\'"', '"telecommunications"', '"\'data warehousing\'"', '"\'silicon graphics\'"', '"\'Systems Analyst\'"', '"\'Project Manager\'"', '"speedy3dgraphics"', '"\'microsoft word\'"', '"\'Web Developer\'"', '"\'Test Engineer\'"', '"\'device driver\'"', '"\'visual basic\'"', '"\'Sql Engineer\'"', '"\'3d graphics\'"', '"\'software qa\'"', '"\'san antonio\'"', '"client/server"', '"\'windows nt\'"', '"\'windows 95\'"', '"\'visual j++\'"', '"\'visual c++\'"', '"\'los alamos\'"', '"\'sql server\'"', '"\'Phil Smith\'"', '"powerbuilder"', '"playstation"', '"california"', '"washington"', '"networking"', '"management"', '"commodores"', '" Microsoft"', '"\'cobol ii\'"', '"\'san jose\'"', '"statistics"', '"Consultant"', '"\'new york\'"', '"Programmer"', '"animation"', '"Developer"', '"nashville"', '"Microsoft"', '"colorado"', '"internet"', '"engineer"', '"graphics"', '"database"', '"ethernet"', '"assembly"', '"Longhorn"', '"network"', '"autocad"', '"Trilogy"', '"houston"', '"seattle"', '"solaris"', '"haskell"', '"windows"', '"fortran"', '"tcp/ip"', '"master"', '"prolog"', '"apache"', '"novell"', '"dallas"', '"Boeing"', '"delphi"', '"oracle"', '"canada"', '"Tivoli"', '"tcl/tk"', '"austin"', '"pascal"', '"boston"', '"Compaq"', '"intern"', '"texas"', '"games"', '"tulsa"', '"cobol"', '"Apple"', '"pdp11"', '"shell"', '"linux"', '"latex"', '"excel"', '"Dell"', '"odbc"', '"BSCS"', '"lisp"', '"perl"', '"MSEE"', '"vc++"', '"unix"', '"cics"', '"html"', '"java"', '"MSCS"', '"BSEE"', '"BACS"', '"IBM"', '"rpg"', '"com"', '"ibm"', '"mfc"', '"usa"', '"LCS"', '"vax"', '"sql"', '"c++"', '"sun"', '"JPL"', '"lan"', '"wan"', '"ole"', '"PhD"', '"web"', '"mvs"', '"ada"', '"mac"', '"MBA"', '"aix"', '"vms"', '"gui"', '"x86"', '"ai"', '"BS"', '"BA"', '"10"', '"HP"', '"MA"', '"pc"', '"vb"', '"c"', '"1"', '"4"', '"3"', '"2"', '"5"']
GRAMMAR_DICTIONARY['salary_value'] = [
    '"100000"', '"70000"', '"65000"', '"50000"', '"80000"',
    '"30000"', '"90000"', '"60000"', '"40000"', '"10000"', '"5000"', '"20"'
]
GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']

COPY_TERMINAL_SET = {'string', 'salary_value'}