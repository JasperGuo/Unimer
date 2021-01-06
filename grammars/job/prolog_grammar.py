# coding=utf-8
"""
Prolog Grammar
"""

# First-order logical form

ROOT_RULE = 'statement -> ["answer(" var "," goal ")"]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['("answer(" var "," goal ")")']
# Goal
GRAMMAR_DICTIONARY['goal'] = [
    '(declaration)',
    '(binary_relation)',
    '(unit_relation)',
    '(meta)',
    '("(" goal "," conjunction ")")', # and
    '("(" goal ";" conjunction ")")', # or
    '("\+(" goal ")")',
    '("\+" unit_relation)'
]
GRAMMAR_DICTIONARY['conjunction'] = [
    '(goal "," conjunction)',
    '(goal ";" conjunction)',
    '(goal)'
]

# Meta Predicates
GRAMMAR_DICTIONARY['meta'] = [
    '("salary_greater_than(" var "," salary_value "," "year" ")")',
    '("salary_greater_than(" var "," salary_value "," "hour" ")")',
    '("salary_greater_than(" var "," salary_value "," "month" ")")',
    '("salary_less_than(" var "," salary_value "," "year" ")")'
]

# Relation
GRAMMAR_DICTIONARY['unit_relation'] = [
    '(is_job)', '(is_unit_req_exp)', '(is_unit_req_deg)',
    '(is_unit_des_deg)','(is_unit_des_exp)'
]
GRAMMAR_DICTIONARY['is_job'] = ['("job(" var ")")']
GRAMMAR_DICTIONARY['is_unit_des_exp'] = ['("des_exp(" var ")")']
GRAMMAR_DICTIONARY['is_unit_req_exp'] = ['("req_exp(" var ")")']
GRAMMAR_DICTIONARY['is_unit_des_deg'] = ['("des_deg(" var ")")']
GRAMMAR_DICTIONARY['is_unit_req_deg'] = ['("req_deg(" var ")")']

GRAMMAR_DICTIONARY['binary_relation'] = [
    '(is_company)', '(is_req_deg)', '(is_area)', '(is_platform)',
    '(is_recruiter)', '(is_const)', '(is_language)', '(is_title)',
    '(is_des_deg)', '(is_application)', '(is_req_exp)', '(is_loc)',
    '(is_country)', '(is_des_exp)'
]
GRAMMAR_DICTIONARY['is_company'] = ['("company(" var "," var ")")']
GRAMMAR_DICTIONARY['is_req_deg'] = ['("req_deg(" var "," var ")")']
GRAMMAR_DICTIONARY['is_area'] = ['("area(" var "," var ")")']
GRAMMAR_DICTIONARY['is_platform'] = ['("platform(" var "," var ")")']
GRAMMAR_DICTIONARY['is_recruiter'] = ['("recruiter(" var "," var ")")']
GRAMMAR_DICTIONARY['is_const'] = ['("const(" var "," var ")")']
GRAMMAR_DICTIONARY['is_language'] = ['("language(" var "," var ")")']
GRAMMAR_DICTIONARY['is_title'] = ['("title(" var "," var ")")']
GRAMMAR_DICTIONARY['is_des_deg'] = ['("des_deg(" var "," var ")")']
GRAMMAR_DICTIONARY['is_application'] = ['("application(" var "," var ")")']
GRAMMAR_DICTIONARY['is_req_exp'] = ['("req_exp(" var "," var ")")']
GRAMMAR_DICTIONARY['is_loc'] = ['("loc(" var "," var ")")']
GRAMMAR_DICTIONARY['is_country'] = ['("country(" var "," var ")")']
GRAMMAR_DICTIONARY['is_des_exp'] = ['("des_exp(" var "," var ")")']

# Terminal
# Normalized Variable
GRAMMAR_DICTIONARY['var'] = ['"NV"', '"V0"', '"V1"', '"V2"',
                             '"V3"', '"V4"', '"V5"', '"V6"', '"V7"']
# Declaration
GRAMMAR_DICTIONARY['declaration'] = [
    '("const(" var "," string ")")']
GRAMMAR_DICTIONARY['string'] = ['"\'Senior Development Engineer\'"', '"\'Lockheed Martin Aeronautics\'"', '"\'Senior Consulting Engineer\'"', '"\'Senior Software Developer\'"', '"\'oil pipeline modeling\'"', '"\'NetWare Administrator\'"', '"\'Verification Engineer\'"', '"\'Systems Administrator\'"', '"\'Manufacturing Manager\'"', '"\'National Instruments\'"', '"\'System Administrator\'"', '"\'research assistant\'"', '"\'Software Developer\'"', '"\'Ic Design Engineer\'"', '"\'Applied Materials\'"', '"\'Software Engineer\'"', '"telecommunications"', '"\'data warehousing\'"', '"\'silicon graphics\'"', '"\'Systems Analyst\'"', '"\'Project Manager\'"', '"speedy3dgraphics"', '"\'microsoft word\'"', '"\'Web Developer\'"', '"\'Test Engineer\'"', '"\'device driver\'"', '"\'visual basic\'"', '"\'Sql Engineer\'"', '"\'3d graphics\'"', '"\'software qa\'"', '"\'san antonio\'"', '"client/server"', '"\'windows nt\'"', '"\'windows 95\'"', '"\'visual j++\'"', '"\'visual c++\'"', '"\'los alamos\'"', '"\'sql server\'"', '"\'Phil Smith\'"', '"powerbuilder"', '"playstation"', '"california"', '"washington"', '"networking"', '"management"', '"commodores"', '" Microsoft"', '"\'cobol ii\'"', '"\'san jose\'"', '"statistics"', '"Consultant"', '"\'new york\'"', '"Programmer"', '"animation"', '"Developer"', '"nashville"', '"Microsoft"', '"colorado"', '"internet"', '"engineer"', '"graphics"', '"database"', '"ethernet"', '"assembly"', '"Longhorn"', '"network"', '"autocad"', '"Trilogy"', '"houston"', '"seattle"', '"solaris"', '"haskell"', '"windows"', '"fortran"', '"tcp/ip"', '"master"', '"prolog"', '"apache"', '"novell"', '"dallas"', '"Boeing"', '"delphi"', '"oracle"', '"canada"', '"Tivoli"', '"tcl/tk"', '"austin"', '"pascal"', '"boston"', '"Compaq"', '"intern"', '"texas"', '"games"', '"tulsa"', '"cobol"', '"Apple"', '"pdp11"', '"shell"', '"linux"', '"latex"', '"excel"', '"Dell"', '"odbc"', '"BSCS"', '"lisp"', '"perl"', '"MSEE"', '"vc++"', '"unix"', '"cics"', '"html"', '"java"', '"MSCS"', '"BSEE"', '"BACS"', '"IBM"', '"rpg"', '"com"', '"ibm"', '"mfc"', '"usa"', '"LCS"', '"vax"', '"sql"', '"c++"', '"sun"', '"JPL"', '"lan"', '"wan"', '"ole"', '"PhD"', '"web"', '"mvs"', '"ada"', '"mac"', '"MBA"', '"aix"', '"vms"', '"gui"', '"x86"', '"ai"', '"BS"', '"BA"', '"10"', '"HP"', '"MA"', '"pc"', '"vb"', '"c"', '"1"', '"4"', '"3"', '"2"', '"5"']
GRAMMAR_DICTIONARY['salary_value'] = [
    '"100000"', '"70000"', '"65000"', '"50000"', '"80000"',
    '"30000"', '"90000"', '"60000"', '"40000"', '"10000"', '"5000"', '"20"'
]

COPY_TERMINAL_SET = {'string', 'salary_value'}
