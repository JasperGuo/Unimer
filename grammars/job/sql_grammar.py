# coding=utf8


ROOT_RULE = 'statement -> [mquery]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY["statement"] = ['(mquery ws)']
GRAMMAR_DICTIONARY["mquery"] = [
    '(ws select_clause ws from_clause ws where_clause)',
    '(ws select_clause ws from_clause)'
]

# SELECT
GRAMMAR_DICTIONARY["select_clause"] = [
    '("select" ws "distinct" ws col_ref)']
# FROM
GRAMMAR_DICTIONARY["from_clause"] = ['(ws "from" ws table_name ws join_clauses)', '(ws "from" ws table_name)']
GRAMMAR_DICTIONARY["join_clauses"] = [
    '(join_clause ws join_clauses)', 'join_clause']
GRAMMAR_DICTIONARY["join_clause"] = [
    '"join" ws table_name ws "on" ws join_condition']
GRAMMAR_DICTIONARY["join_condition"] = ['ws col_ref ws "=" ws col_ref']

# WHERE
GRAMMAR_DICTIONARY["where_clause"] = ['(ws "where" wsp condition)']
GRAMMAR_DICTIONARY["condition"] = ['(ws single ws "and" wsp condition)',
                                   '(ws single ws "or" wsp condition)',
                                   '(single)']
GRAMMAR_DICTIONARY["single"] = ['(expr)',
                                '("(" ws condition ws ")")',
                                '("not" ws single)']

GRAMMAR_DICTIONARY["expr"] = [
    '(col_ref wsp "not" wsp "in" wsp "(" ws mquery ws ")")',
    '(col_ref wsp "in" wsp "(" ws mquery ws ")")',
    '(col_ref wsp "is" wsp "null")',
    '(col_ref wsp "is" wsp "not" wsp "null")',
    '(col_ref wsp binaryop ws value)',
]
GRAMMAR_DICTIONARY["value"] = ['non_literal_number', 'string']
GRAMMAR_DICTIONARY["col_ref"] = ['(table_name ws "." ws column_name)']

# TODO(MARK): This is not tight enough. AND/OR are strictly boolean value operators.
GRAMMAR_DICTIONARY["binaryop"] = ['"="', '"!="', '"<>"',
                                  '">="', '"<="', '">"', '"<"', ]

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY['wsp'] = ['~"\s+"i']
GRAMMAR_DICTIONARY["table_name"] = ['"job"', '"salary"', '"country"', '"city"',
                                    '"platform"', '"age"', '"application"',
                                    '"area"', '"language"']

GRAMMAR_DICTIONARY["column_name"] = [
    '"job_id"', '"age"', '"time"', '"money"', '"language"',
    '"country"', '"platform"', '"application"', '"title"',
    '"company"', '"major"', '"req_exp"', '"req_deg"',
    '"des_deg"', '"des_exp"', '"recruiter"', '"post_day"',
    '"area"', '"city_name"'
]
GRAMMAR_DICTIONARY["non_literal_number"] = ['"100000"', '"90000"', '"80000"', '"70000"', '"65000"', '"60000"', '"50000"', '"40000"', '"30000"', '"10000"', '"5000"', '"20"', '"10"', '"5"', '"4"', '"3"', '"2"', '"1"']
GRAMMAR_DICTIONARY["string"] = ['"\'senior development engineer\'"', '"\'lockheed martin aeronautics\'"', '"\'senior consulting engineer\'"', '"\'senior software developer\'"', '"\'manufacturing manager\'"', '"\'systems administrator\'"', '"\'verification engineer\'"', '"\'oil pipeline modeling\'"', '"\'netware administrator\'"', '"\'national instruments\'"', '"\'system administrator\'"', '"\'software developer\'"', '"\'research assistant\'"', '"\'telecommunications\'"', '"\'ic design engineer\'"', '"\'software engineer\'"', '"\'applied materials\'"', '"\'silicon graphics\'"', '"\'speedy3dgraphics\'"', '"\'data warehousing\'"', '"\'systems analyst\'"', '"\'project manager\'"', '"\'microsoft word\'"', '"\'device driver\'"', '"\'web developer\'"', '"\'test engineer\'"', '"\'client/server\'"', '"\'powerbuilder\'"', '"\'visual basic\'"', '"\'sql engineer\'"', '"\'san antonio\'"', '"\'3d graphics\'"', '"\'software qa\'"', '"\'playstation\'"', '"\'programmer\'"', '"\'networking\'"', '"\'commodores\'"', '"\'visual c++\'"', '"\'sql server\'"', '"\'windows nt\'"', '"\'phil smith\'"', '"\'statistics\'"', '"\'washington\'"', '"\'los alamos\'"', '"\'management\'"', '"\'california\'"', '"\'consultant\'"', '"\'windows 95\'"', '"\'visual j++\'"', '"\'microsoft\'"', '"\'developer\'"', '"\'nashville\'"', '"\'animation\'"', '"\'new york\'"', '"\'engineer\'"', '"\'internet\'"', '"\'assembly\'"', '"\'database\'"', '"\'cobol ii\'"', '"\'san jose\'"', '"\'graphics\'"', '"\'longhorn\'"', '"\'colorado\'"', '"\'ethernet\'"', '"\'windows\'"', '"\'seattle\'"', '"\'autocad\'"', '"\'solaris\'"', '"\'network\'"', '"\'haskell\'"', '"\'trilogy\'"', '"\'fortran\'"', '"\'houston\'"', '"\'dallas\'"', '"\'apache\'"', '"\'boeing\'"', '"\'tcp/ip\'"', '"\'tcl/tk\'"', '"\'canada\'"', '"\'boston\'"', '"\'compaq\'"', '"\'prolog\'"', '"\'intern\'"', '"\'novell\'"', '"\'austin\'"', '"\'pascal\'"', '"\'master\'"', '"\'oracle\'"', '"\'tivoli\'"', '"\'delphi\'"', '"\'texas\'"', '"\'shell\'"', '"\'tulsa\'"', '"\'cobol\'"', '"\'month\'"', '"\'pdp11\'"', '"\'excel\'"', '"\'games\'"', '"\'latex\'"', '"\'apple\'"', '"\'linux\'"', '"\'year\'"', '"\'bscs\'"', '"\'bsee\'"', '"\'dell\'"', '"\'mscs\'"', '"\'html\'"', '"\'hour\'"', '"\'unix\'"', '"\'lisp\'"', '"\'cics\'"', '"\'bacs\'"', '"\'vc++\'"', '"\'msee\'"', '"\'java\'"', '"\'odbc\'"', '"\'perl\'"', '"\'mvs\'"', '"\'ole\'"', '"\'web\'"', '"\'usa\'"', '"\'ada\'"', '"\'sun\'"', '"\'vms\'"', '"\'c++\'"', '"\'mba\'"', '"\'gui\'"', '"\'wan\'"', '"\'lcs\'"', '"\'aix\'"', '"\'mfc\'"', '"\'vax\'"', '"\'x86\'"', '"\'mac\'"', '"\'jpl\'"', '"\'lan\'"', '"\'sql\'"', '"\'phd\'"', '"\'ibm\'"', '"\'rpg\'"', '"\'com\'"', '"\'ma\'"', '"\'vb\'"', '"\'pc\'"', '"\'ai\'"', '"\'ba\'"', '"\'bs\'"', '"\'hp\'"', '"\'c\'"']

COPY_TERMINAL_SET = {"non_literal_number", "string"}
