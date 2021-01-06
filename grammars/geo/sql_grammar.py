# coding=utf8


ROOT_RULE = 'statement -> [mquery]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY["statement"] = ['(mquery ws)']
GRAMMAR_DICTIONARY["mquery"] = [
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause ws having_clause ws orderby_clause ws limit)',
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause ws having_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause ws having_clause)',
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause ws orderby_clause ws limit)',
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws where_clause ws groupby_clause)',
    '(ws select_clause ws from_clause ws where_clause ws orderby_clause ws limit)',
    '(ws select_clause ws from_clause ws where_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws where_clause)',
    '(ws select_clause ws from_clause ws groupby_clause ws having_clause ws orderby_clause ws limit)',
    '(ws select_clause ws from_clause ws groupby_clause ws having_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws groupby_clause ws having_clause)',
    '(ws select_clause ws from_clause ws groupby_clause ws orderby_clause ws limit)',
    '(ws select_clause ws from_clause ws groupby_clause ws orderby_clause)',
    '(ws select_clause ws from_clause ws groupby_clause)',
    '(ws select_clause ws from_clause ws orderby_clause ws limit)',
    '(ws select_clause ws from_clause ws orderby_clause)',
    '(ws select_clause ws from_clause)'
]

# SELECT
GRAMMAR_DICTIONARY["select_clause"] = [
    '(select_with_distinct ws select_results)']
GRAMMAR_DICTIONARY["select_with_distinct"] = [
    '(ws "select" ws "distinct")', '(ws "select")']
GRAMMAR_DICTIONARY["select_results"] = [
    '(ws select_result ws "," ws select_results)', '(ws select_result)']
GRAMMAR_DICTIONARY["select_result"] = [
    '(subject ws selectop ws subject)',
    '(subject wsp "as" wsp column_alias)',
    'subject',
]

# FROM
GRAMMAR_DICTIONARY["from_clause"] = ['(ws "from" ws table_source ws join_clauses)',
                                     '(ws "from" ws source)']
GRAMMAR_DICTIONARY["join_clauses"] = [
    '(join_clause ws join_clauses)', 'join_clause']
GRAMMAR_DICTIONARY["join_clause"] = [
    'joinop ws table_source ws "on" ws join_condition_clause']
GRAMMAR_DICTIONARY["joinop"] = ['"join"', '"left outer join"']
GRAMMAR_DICTIONARY["join_condition_clause"] = [
    '(join_condition ws "and" ws join_condition_clause)', 'join_condition']
GRAMMAR_DICTIONARY["join_condition"] = ['ws col_ref ws "=" ws col_ref']
GRAMMAR_DICTIONARY["source"] = [
    '(ws single_source ws "," ws source)', '(ws single_source)']
GRAMMAR_DICTIONARY["single_source"] = ['table_source', 'source_subq']
GRAMMAR_DICTIONARY["source_subq"] = ['("(" ws mquery ws ")" wsp "as" wsp table_alias)',
                                     '("(" ws mquery ws ")" wsp table_alias)', '("(" ws mquery ws ")")']
GRAMMAR_DICTIONARY["table_source"] = [
    '(table_name ws "as" ws table_alias)', 'table_name']

# LIMIT
GRAMMAR_DICTIONARY["limit"] = ['("limit" ws non_literal_number)']

# ORDER
GRAMMAR_DICTIONARY["orderby_clause"] = ['ws "order" ws "by" ws order_clause']
GRAMMAR_DICTIONARY["order_clause"] = [
    '(ordering_term ws "," ws order_clause)', 'ordering_term']
GRAMMAR_DICTIONARY["ordering_term"] = [
    '(ws subject ws ordering)', '(ws subject)']
GRAMMAR_DICTIONARY["ordering"] = ['(ws "asc")', '(ws "desc")']

# WHERE
GRAMMAR_DICTIONARY["where_clause"] = [
    '(ws "where" wsp expr ws where_conj)', '(ws "where" wsp expr)']
GRAMMAR_DICTIONARY["where_conj"] = ['(ws "and" wsp expr ws where_conj)', '(ws "and" wsp expr)',
                                    '(ws "or" wsp expr ws where_conj)', '(ws "or" wsp expr)']

# GROUP BY
GRAMMAR_DICTIONARY["groupby_clause"] = ['(ws "group" ws "by" ws group_clause)']
GRAMMAR_DICTIONARY["group_clause"] = [
    '(ws subject ws "," ws group_clause)', '(ws subject)']

# HAVING
GRAMMAR_DICTIONARY["having_clause"] = [
    '(ws "having" wsp expr ws having_conj)', '(ws "having" wsp expr)']
GRAMMAR_DICTIONARY["having_conj"] = ['(ws "and" wsp expr ws having_conj)', '(ws "and" wsp expr)',
                                     '(ws "or" wsp expr ws having_conj)', '(ws "or" wsp expr)']

GRAMMAR_DICTIONARY["expr"] = [
    '(subject wsp "not" wsp "in" wsp "(" ws mquery ws ")")',
    '(subject wsp "in" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "all" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "any" ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws "(" ws mquery ws ")")',
    '(subject ws binaryop ws value)',
]
GRAMMAR_DICTIONARY["value"] = ['non_literal_number', 'col_ref', 'string']
GRAMMAR_DICTIONARY["subject"] = ['function', 'col_ref']
GRAMMAR_DICTIONARY["col_ref"] = [
    '(table_alias ws "." ws column_name)', 'column_name']

GRAMMAR_DICTIONARY["function"] = ['(fname ws "(" ws "distinct" ws col_ref ws ")")',
                                  '(fname ws "(" ws col_ref ws ")")']
GRAMMAR_DICTIONARY["fname"] = ['"count"',
                               '"sum"', '"max"', '"min"', '"avg"', '"all"']

# TODO(MARK): This is not tight enough. AND/OR are strictly boolean value operators.
GRAMMAR_DICTIONARY["binaryop"] = ['"="', '"!="', '"<>"',
                                  '">="', '"<="', '">"', '"<"', '"like"', '"not like"']
GRAMMAR_DICTIONARY['selectop'] = ['"/"', '"+"', '"-"']

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY['wsp'] = ['~"\s+"i']
GRAMMAR_DICTIONARY["table_name"] = ['"state"', '"city"',
                                    '"lake"', '"river"', '"border_info"', '"highlow"', '"mountain"']
GRAMMAR_DICTIONARY["table_alias"] = [
    '"statealias0"', '"statealias1"', '"statealias2"', '"statealias3"', '"statealias4"', '"statealias5"',
    '"cityalias0"', '"cityalias1"', '"cityalias2"',
    '"lakealias0"', '"mountainalias0"', '"mountainalias1"',
    '"riveralias0"', '"riveralias1"', '"riveralias2"', '"riveralias3"',
    '"border_infoalias0"', '"border_infoalias1"', '"border_infoalias2"', '"border_infoalias3"',
    '"highlowalias0"', '"highlowalias1"', '"derived_tablealias0"', '"derived_tablealias1"',
    '"tmp"',
]
GRAMMAR_DICTIONARY["column_name"] = [
    '"*"', '"city_name"', '"population"', '"country_name"', '"state_name"',  # city
    '"border"',  # border_info
    '"highest_elevation"', '"lowest_point"', '"highest_point"', '"lowest_elevation"',  # highlow
    '"lake_name"', '"area"', '"country_name"',  # lake
    '"mountain_name"', '"mountain_altitude"',  # mountain
    '"river_name"', '"length"', '"traverse"',  # river
    '"capital"', '"density"',  # state,
    '"derived_fieldalias0"', '"derived_fieldalias1"',
]
GRAMMAR_DICTIONARY['column_alias'] = [
    '"derived_fieldalias0"', '"derived_fieldalias1"'  # custom
]

GRAMMAR_DICTIONARY["non_literal_number"] = [
    '"150000"', '"750"', '"0"', '"1"', '"2"', '"3"', '"4"', ]
GRAMMAR_DICTIONARY['string'] = ['"\'usa\'"', '"\'red\'"', '"750"', '"0"', '"150000"', '"\'oregon\'"', '"\'georgia\'"', '"\'wisconsin\'"', '"\'montana\'"', '"\'colorado\'"', '"\'west virginia\'"', '"\'hawaii\'"', '"\'new hampshire\'"', '"\'washington\'"', '"\'florida\'"', '"\'north dakota\'"', '"\'idaho\'"', '"\'minnesota\'"', '"\'tennessee\'"', '"\'vermont\'"', '"\'kentucky\'"', '"\'alabama\'"', '"\'oklahoma\'"', '"\'maryland\'"', '"\'nebraska\'"', '"\'iowa\'"', '"\'kansas\'"', '"\'california\'"', '"\'wyoming\'"',
                                '"\'massachusetts\'"', '"\'missouri\'"', '"\'nevada\'"', '"\'south dakota\'"', '"\'utah\'"', '"\'rhode island\'"', '"\'new york\'"', '"\'new jersey\'"', '"\'indiana\'"', '"\'new mexico\'"', '"\'maine\'"', '"\'illinois\'"', '"\'louisiana\'"', '"\'michigan\'"', '"\'mississippi\'"', '"\'ohio\'"', '"\'south carolina\'"', '"\'arkansas\'"', '"\'texas\'"', '"\'virginia\'"', '"\'pennsylvania\'"', '"\'north carolina\'"', '"\'alaska\'"', '"\'arizona\'"', '"\'delaware\'"', '"\'north platte\'"',
                                '"\'chattahoochee\'"', '"\'rio grande\'"', '"\'potomac\'"', '"\'mckinley\'"', '"\'whitney\'"', '"\'death valley\'"', '"\'mount mckinley\'"', '"\'guadalupe peak\'"', '"\'detroit\'"', '"\'plano\'"', '"\'des moines\'"', '"\'boston\'"', '"\'salem\'"', '"\'fort wayne\'"', '"\'houston\'"', '"\'portland\'"', '"\'montgomery\'"', '"\'minneapolis\'"', '"\'tempe\'"', '"\'boulder\'"', '"\'seattle\'"', '"\'columbus\'"', '"\'dover\'"', '"\'indianapolis\'"', '"\'san antonio\'"', '"\'albany\'"', '"\'flint\'"', '"\'chicago\'"', '"\'miami\'"',
                                   '"\'scotts valley\'"', '"\'san francisco\'"', '"\'springfield\'"', '"\'sacramento\'"', '"\'salt lake city\'"', '"\'new orleans\'"', '"\'atlanta\'"', '"\'tucson\'"', '"\'denver\'"', '"\'riverside\'"', '"\'erie\'"', '"\'san jose\'"', '"\'durham\'"', '"\'kalamazoo\'"', '"\'baton rouge\'"', '"\'san diego\'"', '"\'pittsburgh\'"', '"\'spokane\'"', '"\'austin\'"', '"\'rochester\'"', '"\'dallas\'"']

COPY_TERMINAL_SET = {'non_literal_number', 'string'}
