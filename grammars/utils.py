# coding=utf8

import re
from collections import defaultdict
from sys import exc_info
from typing import List, Dict, Set

from overrides import overrides
from parsimonious.exceptions import VisitationError, UndefinedLabel
from parsimonious.expressions import Literal, OneOf, Sequence
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor
from six import reraise
from allennlp.data.tokenizers import WordTokenizer

from .geo import geo_normalization, geo_tokenizer
from .job import job_normalization, job_tokenizer
from .atis import atis_normalization, atis_tokenizer


WHITESPACE_REGEX = re.compile(" wsp |wsp | wsp| ws |ws | ws")
AGG_OPS = ('none', 'max', 'min', 'count', 'sum', 'avg')
WHERE_OPS = ('not', 'between', '=', '>', '<', '>=',
             '<=', '!=', 'in', 'like', 'is', 'exists')


def format_grammar_string(grammar_dictionary: Dict[str, List[str]]) -> str:
    """
    Formats a dictionary of production rules into the string format expected
    by the Parsimonious Grammar class.
    """
    return '\n'.join([f"{nonterminal} = {' / '.join(right_hand_side)}"
                      for nonterminal, right_hand_side in grammar_dictionary.items()])


def initialize_valid_actions(grammar: Grammar,
                             keywords_to_uppercase: List[str] = None) -> Dict[str, List[str]]:
    """
    We initialize the valid actions with the global actions. These include the
    valid actions that result from the grammar and also those that result from
    the tables provided. The keys represent the nonterminals in the grammar
    and the values are lists of the valid actions of that nonterminal.
    """
    valid_actions: Dict[str, Set[str]] = defaultdict(set)

    for key in grammar:
        rhs = grammar[key]

        # Sequence represents a series of expressions that match pieces of the text in order.
        # Eg. A -> B C
        if isinstance(rhs, Sequence):
            valid_actions[key].add(
                format_action(key, " ".join(rhs._unicode_members()),  # pylint: disable=protected-access
                              keywords_to_uppercase=keywords_to_uppercase))

        # OneOf represents a series of expressions, one of which matches the text.
        # Eg. A -> B / C
        elif isinstance(rhs, OneOf):
            for option in rhs._unicode_members():  # pylint: disable=protected-access
                valid_actions[key].add(format_action(key, option,
                                                     keywords_to_uppercase=keywords_to_uppercase))

        # A string literal, eg. "A"
        elif isinstance(rhs, Literal):
            if rhs.literal != "":
                valid_actions[key].add(format_action(key, repr(rhs.literal),
                                                     keywords_to_uppercase=keywords_to_uppercase))
            else:
                valid_actions[key] = set()

    valid_action_strings = {key: sorted(value)
                            for key, value in valid_actions.items()}
    return valid_action_strings


def format_action(nonterminal: str,
                  right_hand_side: str,
                  is_string: bool = False,
                  is_number: bool = False,
                  keywords_to_uppercase: List[str] = None) -> str:
    """
    This function formats an action as it appears in models. It
    splits productions based on the special `ws` and `wsp` rules,
    which are used in grammars to denote whitespace, and then
    rejoins these tokens a formatted, comma separated list.
    Importantly, note that it `does not` split on spaces in
    the grammar string, because these might not correspond
    to spaces in the language the grammar recognises.

    Parameters
    ----------
    nonterminal : ``str``, required.
        The nonterminal in the action.
    right_hand_side : ``str``, required.
        The right hand side of the action
        (i.e the thing which is produced).
    is_string : ``bool``, optional (default = False).
        Whether the production produces a string.
        If it does, it is formatted as ``nonterminal -> ['string']``
    is_number : ``bool``, optional, (default = False).
        Whether the production produces a string.
        If it does, it is formatted as ``nonterminal -> ['number']``
    keywords_to_uppercase: ``List[str]``, optional, (default = None)
        Keywords in the grammar to uppercase. In the case of sql,
        this might be SELECT, MAX etc.
    """
    keywords_to_uppercase = keywords_to_uppercase or []
    if right_hand_side.upper() in keywords_to_uppercase:
        right_hand_side = right_hand_side.upper()

    if is_string:
        return f'{nonterminal} -> ["\'{right_hand_side}\'"]'

    elif is_number:
        return f'{nonterminal} -> ["{right_hand_side}"]'

    else:
        right_hand_side = right_hand_side.lstrip("(").rstrip(")")
        child_strings = [token for token in WHITESPACE_REGEX.split(
            right_hand_side) if token]
        child_strings = [tok.upper() if tok.upper(
        ) in keywords_to_uppercase else tok for tok in child_strings]
        return f"{nonterminal} -> [{' '.join(child_strings)}]"


def action_sequence_to_logical_form(action_sequences: List[str], add_table_names: bool = False) -> str:
    # Convert an action sequence like ['statement -> [query, ";"]', ...] to the
    # SQL string.
    query = []
    for action in action_sequences:
        nonterminal, right_hand_side = action.split(' -> ')
        right_hand_side_tokens = right_hand_side[1:-1].split(' ')
        if nonterminal == 'statement':
            query.extend(right_hand_side_tokens)
        else:
            for query_index, token in list(enumerate(query)):
                if token == nonterminal:
                    # if nonterminal == 'column_name' and '@' in right_hand_side_tokens[0] and len(right_hand_side_tokens) == 1:
                    #     if add_table_names:
                    #         table_name, column_name = right_hand_side_tokens[0].split('@')
                    #         if '.' in table_name:
                    #             table_name = table_name.split('.')[0]
                    #         right_hand_side_tokens = [table_name + '.' + column_name]
                    #     else:
                    #         right_hand_side_tokens = [right_hand_side_tokens[0].split('@')[-1]]
                    query = query[:query_index] + \
                        right_hand_side_tokens + \
                        query[query_index + 1:]
                    break
    return ' '.join([token.strip('"') for token in query])


class SqlVisitor(NodeVisitor):
    """
    ``SqlVisitor`` performs a depth-first traversal of the the AST. It takes the parse tree
    and gives us an action sequence that resulted in that parse. Since the visitor has mutable
    state, we define a new ``SqlVisitor`` for each query. To get the action sequence, we create
    a ``SqlVisitor`` and call parse on it, which returns a list of actions. Ex.

        sql_visitor = SqlVisitor(grammar_string)
        action_sequence = sql_visitor.parse(query)

    Importantly, this ``SqlVisitor`` skips over ``ws`` and ``wsp`` nodes,
    because they do not hold any meaning, and make an action sequence
    much longer than it needs to be.

    Parameters
    ----------
    grammar : ``Grammar``
        A Grammar object that we use to parse the text.
    keywords_to_uppercase: ``List[str]``, optional, (default = None)
        Keywords in the grammar to uppercase. In the case of sql,
        this might be SELECT, MAX etc.
    """

    def __init__(self, grammar: Grammar, keywords_to_uppercase: List[str] = None) -> None:
        self.action_sequence: List[str] = []
        self.grammar: Grammar = grammar
        self.keywords_to_uppercase = keywords_to_uppercase or []

    @overrides
    def generic_visit(self, node: Node, visited_children: List[None]) -> List[str]:
        self.add_action(node)
        if node.expr.name == 'statement':
            return self.action_sequence
        return []

    def add_action(self, node: Node) -> None:
        """
        For each node, we accumulate the rules that generated its children in a list.
        """
        if node.expr.name and node.expr.name not in ['ws', 'wsp']:
            nonterminal = f'{node.expr.name} -> '
            if isinstance(node.expr, Literal):
                right_hand_side = f'["{node.text}"]'
            else:
                child_strings = []
                for child in node.__iter__():
                    if child.expr.name in ['ws', 'wsp']:
                        continue
                    if child.expr.name != '':
                        child_strings.append(child.expr.name)
                    else:
                        child_right_side_string = child.expr._as_rhs().lstrip("(").rstrip(
                            ")")  # pylint: disable=protected-access
                        child_right_side_list = [tok for tok in
                                                 WHITESPACE_REGEX.split(child_right_side_string) if tok]
                        child_right_side_list = [tok.upper() if tok.upper() in
                                                 self.keywords_to_uppercase else tok
                                                 for tok in child_right_side_list]
                        child_strings.extend(child_right_side_list)
                right_hand_side = "[" + " ".join(child_strings) + "]"
            rule = nonterminal + right_hand_side
            self.action_sequence = [rule] + self.action_sequence

    @overrides
    def visit(self, node):
        """
        See the ``NodeVisitor`` visit method. This just changes the order in which
        we visit nonterminals from right to left to left to right.
        """
        method = getattr(self, 'visit_' + node.expr_name, self.generic_visit)

        # Call that method, and show where in the tree it failed if it blows
        # up.
        try:
            # Changing this to reverse here!
            return method(node, [self.visit(child) for child in reversed(list(node))])
        except (VisitationError, UndefinedLabel):
            # Don't catch and re-wrap already-wrapped exceptions.
            raise
        except self.unwrapped_exceptions:
            raise
        except Exception:  # pylint: disable=broad-except
            # Catch any exception, and tack on a parse tree so it's easier to
            # see where it went wrong.
            exc_class, exc, traceback = exc_info()
            reraise(VisitationError, VisitationError(
                exc, exc_class, node), traceback)


def format_col_unit(col_unit, column_names, table_names):
    agg_id, col_id, _ = col_unit
    agg = '' if int(agg_id) == 0 else AGG_OPS[agg_id]
    if col_id == 0:
        result = "*"
    else:
        result = "%s@%s" % (
            table_names[column_names[col_id][0]], column_names[col_id][1])
    return agg, result


def transform_query_tree(query_tree, schema):
    # from
    from_clause = query_tree['from']
    table_names = schema['table_names_original']
    column_names = schema['column_names_original']
    # table_units = from_clause['table_units']
    # column_length = len(schema['column_names'])
    # from_table_names = list()
    # from_table_entities = list()
    # for tu in table_units:
    #     if tu[0] == 'table_unit':
    #         from_table_names.append(table_names[tu[1]])
    #         from_table_entities.append("@entity_%d" % (tu[1] + column_length))

    # select
    select_clause = query_tree['select']
    select_columns = list()
    for agg_id, val_unit in select_clause[1]:
        unit_op, col_unit1, col_unit2 = val_unit
        col_unit1[0] = agg_id
        select_columns.append(format_col_unit(
            col_unit1, column_names, table_names))

    # groupby clause
    groupby_clause = query_tree.get('groupBy', None)
    groupby_columns = list()
    if groupby_clause:
        for col_unit in groupby_clause:
            groupby_columns.append(format_col_unit(
                col_unit, column_names, table_names))

    # orderby clause
    orderby_clause = query_tree.get('orderBy', None)
    orderby_direction = ''
    orderby_columns = list()
    if orderby_clause:
        orderby_direction = orderby_clause[0]
        for val_unit in orderby_clause[1]:
            unit_op, col_unit1, col_unit2 = val_unit
            orderby_columns.append(format_col_unit(
                col_unit1, column_names, table_names))

    # limit clause
    limit_clause = query_tree.get('limit', None)
    limit_value = -1
    if limit_clause:
        limit_value = limit_clause

    # where clause
    where_clause = query_tree.get('where', None)
    where_columns = list()
    if where_clause:
        for cond_unit in where_clause:
            if isinstance(cond_unit, str):
                where_columns.append(cond_unit)
                continue
            not_op, op_id, val_unit, val1, val2 = cond_unit
            unit_op, col_unit1, col_unit2 = val_unit
            if not_op:
                operator = "not " + WHERE_OPS[op_id]
            else:
                operator = WHERE_OPS[op_id]
            agg, col = format_col_unit(col_unit1, column_names, table_names)
            if operator != 'between':
                if isinstance(val1, dict):
                    value1 = '(' + transform_query_tree(val1, schema) + ')'
                else:
                    value1 = 'value'
                where_columns.append((col, operator, str(value1)))
            else:
                if isinstance(val1, dict):
                    value1 = '(' + transform_query_tree(val1, schema) + ')'
                else:
                    value1 = 'value'
                if isinstance(val2, dict):
                    value2 = '(' + transform_query_tree(val2, schema) + ')'
                else:
                    value2 = 'value'
                where_columns.append(
                    (col, operator, str(value1), "and", str(value2)))

    # having clause
    having_clause = query_tree.get('having', None)
    having_columns = list()
    if having_clause:
        for cond_unit in having_clause:
            if isinstance(cond_unit, str):
                having_columns.append(cond_unit)
                continue
            not_op, op_id, val_unit, val1, val2 = cond_unit
            unit_op, col_unit1, col_unit2 = val_unit
            if not_op:
                operator = "not " + WHERE_OPS[op_id]
            else:
                operator = WHERE_OPS[op_id]
            agg, col_idx = format_col_unit(
                col_unit1, column_names, table_names)
            if operator != 'between':
                if isinstance(val1, dict):
                    value1 = '(' + transform_query_tree(val1, schema) + ')'
                else:
                    value1 = 'value'
                having_columns.append(
                    (agg + '(%s)' % col_idx, operator, str(value1)))
            else:
                if isinstance(val1, dict):
                    value1 = '(' + transform_query_tree(val1, schema) + ')'
                else:
                    value1 = 'value'
                if isinstance(val2, dict):
                    value2 = '(' + transform_query_tree(val2, schema) + ')'
                else:
                    value2 = 'value'
                having_columns.append(
                    (agg + '(%s)' % col_idx, operator, str(value1), "and", str(value2)))

    sql = "SELECT " + \
        ', '.join([col if agg == '' else agg + '(%s)' %
                   col for agg, col in select_columns])

    # sql += " FROM " + " JOIN ".join(from_table_entities)

    if len(where_columns) > 0:
        where_str = " WHERE "
        for wc in where_columns:
            if isinstance(wc, str):
                where_str += wc + " "
            else:
                assert isinstance(wc, tuple)
                where_str += ' '.join(wc) + " "
        sql += where_str

    if len(groupby_columns) > 0:
        groupby_str = ' GROUPBY '
        groupby_str += ', '.join([col if agg == '' else agg + '(%s)' %
                                  col for agg, col in groupby_columns])
        sql += groupby_str

    if len(having_columns) > 0:
        having_str = " HAVING "
        for hc in having_columns:
            if isinstance(hc, str):
                having_str += hc + " "
            else:
                assert isinstance(hc, tuple)
                having_str += ' '.join(hc) + " "
        sql += having_str

    if len(orderby_columns) > 0:
        orderby_str = ' ORDERBY '
        orderby_str += ', '.join([col if agg == '' else agg + '(%s)' %
                                  col for agg, col in orderby_columns])
        orderby_str += " %s" % orderby_direction
        sql += orderby_str

    if limit_value > 0:
        sql += " LIMIT %d " % 1

    union_clause = query_tree.get('union', None)
    if union_clause:
        sql += ' UNION ' + transform_query_tree(union_clause, schema)

    except_clause = query_tree.get('except', None)
    if except_clause:
        sql += ' EXCEPT ' + transform_query_tree(except_clause, schema)

    intersect_clause = query_tree.get('intersect', None)
    if intersect_clause:
        sql += ' INTERSECT ' + transform_query_tree(intersect_clause, schema)

    sql = re.sub("\s+", " ", sql)

    return sql


def get_logical_form_preprocessor(task, language, normalize_var_with_de_brujin_index=False):
    logical_form_preprocessor = None
    if task == 'geo':
        if language in ['prolog', 'prolog2']:
            if normalize_var_with_de_brujin_index:
                # Normalize Prolog Variable
                logical_form_preprocessor = geo_normalization.normalize_prolog_variable_names
            else:
                # Original Form
                logical_form_preprocessor = geo_normalization.normalize_prolog
            # Anonymize Prolog Variable
            # logical_form_preprocessor = geo_normalization.anonymize_prolog_variable_names
        elif language in ['sql', 'sql2', 'sql3']:
            logical_form_preprocessor = geo_normalization.normalize_sql
        elif language in ['lambda', 'lambda2']:
            logical_form_preprocessor = geo_normalization.normalize_lambda_calculus
        else:
            # FunQL or typed_funql
            logical_form_preprocessor = geo_normalization.normalize_funql
    elif task == 'atis':
        if language in ['lambda', 'lambda2', 'lambda3', 'lambda4']:
            logical_form_preprocessor = atis_normalization.normalize_lambda_calculus
        elif language in ['prolog', 'prolog2']:
            if normalize_var_with_de_brujin_index:
                logical_form_preprocessor = atis_normalization.normalize_prolog_variable_names
            else:
                logical_form_preprocessor = atis_normalization.preprocess_prolog
        elif language in ['funql', 'typed_funql']:
            logical_form_preprocessor = atis_normalization.preprocess_funql
        else:
        # elif language == 'sql':
            logical_form_preprocessor = atis_normalization.preprocess_sql
    elif task == 'job':
        if language in ['prolog', 'prolog2']:
            logical_form_preprocessor = job_normalization.preprocess_prolog
        elif language in ['funql', 'funql2']:
            logical_form_preprocessor = job_normalization.preprocess_funql
        elif language in ['sql', 'sql2']:
            logical_form_preprocessor = job_normalization.normalize_sql
        elif language in ['lambda', 'lambda2']:
            logical_form_preprocessor = job_normalization.normalize_lambda_calculus
    return logical_form_preprocessor


def get_logical_form_postprocessor(task, language):
    logical_form_postprocessor = None
    if task == 'atis':
        if language in ['sql', 'sql2', 'sql3']:
            logical_form_postprocessor = atis_normalization.postprocess_sql
        elif language in ['lambda', 'lambda2', 'lambda3', 'lambda4']:
            logical_form_postprocessor = atis_normalization.postprocess_lambda_calculus
    elif task == 'job':
        if language in ['prolog', 'prolog2']:
            logical_form_postprocessor = job_normalization.postprocess_prolog
        elif language in ['funql', 'funql2']:
            logical_form_postprocessor = job_normalization.postprocess_prolog
        elif language in ['sql', 'sql2']:
            logical_form_postprocessor = job_normalization.postprocess_sql
        elif language in ['lambda', 'lambda2']:
            logical_form_postprocessor = job_normalization.postprocess_sql
    return logical_form_postprocessor


def get_logical_form_tokenizer(task, language):
    if task == 'geo':
        splitter = geo_tokenizer.get_logical_tokenizer(language)
    elif task == 'job':
        splitter = job_tokenizer.get_logical_tokenizer(language)
    else:
        assert task == 'atis'
        splitter = atis_tokenizer.get_logical_tokenizer(language)
    tokenizer = WordTokenizer(splitter)
    return tokenizer


def get_utterance_preprocessor(task, language):
    preprocessor = None
    if task == 'job' and language in ['prolog', 'funql', 'sql', 'lambda']:
        preprocessor = lambda x: x.replace("'", "").replace(
            "windows nt", "windo nt").replace("windows 95", "windo 95")
    return preprocessor
