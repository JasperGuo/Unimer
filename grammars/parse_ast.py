# coding=utf8

from grammars.basic import ProductionRule
from grammars.utils import action_sequence_to_logical_form


class ASTNode:
    def __init__(self, production_rule: ProductionRule, parent, node_id: int, nonterminals_to_skip: list = None):
        self._production_rule = production_rule
        if nonterminals_to_skip is None:
            self._nonterminals_to_skip = list()
        else:
            self._nonterminals_to_skip = nonterminals_to_skip
        self._rhs_nodes, self._rhs_nonterminals = list(), list()
        for r in production_rule.rhs_nonterminal:
            if r not in self._nonterminals_to_skip:
                self._rhs_nodes.append(None)
                self._rhs_nonterminals.append(r)
        self._parent = parent
        self._id = node_id

    @property
    def is_complete(self):
        complete = True
        for r in self._rhs_nodes:
            if r is None:
                complete = False
                break
        return complete

    @property
    def production_rule(self):
        return self._production_rule

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def lhs(self):
        return self._production_rule.lhs

    @property
    def rhs(self):
        terms = [term for term in self._production_rule.rhs.strip(
            '[] ').split(' ')]
        nodes = list()
        idx = 0
        for t in terms:
            if idx < len(self._rhs_nonterminals) and self._rhs_nonterminals[idx] == t:
                nodes.append(self.rhs_nodes[idx])
                idx += 1
            else:
                nodes.append(t)
        return nodes

    @property
    def rhs_nodes(self):
        return self._rhs_nodes

    @property
    def rhs_nonterminals(self):
        return self._rhs_nonterminals

    @property
    def node_id(self):
        return self._id

    def add_column(self, column_id):
        pass

    def add_node(self, node):
        for ridx, r in enumerate(self._rhs_nodes):
            if r is None:
                assert self._rhs_nonterminals[ridx] == node.production_rule.lhs
                self._rhs_nodes[ridx] = node
                break
        else:
            raise Exception("AST Node %s Already Completed" %
                            str(self._production_rule))

    def get_curr_non_terminal(self):
        for ridx, r in enumerate(self._rhs_nodes):
            if r is None:
                return self._rhs_nonterminals[ridx]
        return None

    def clean_up(self):
        self._parent = None

    def __str__(self):
        return str(self._production_rule)

    def __repr__(self):
        return str(self)


class AST:
    def __init__(self, root_rule: ProductionRule, is_sketch_only: bool = False, nonterminals_to_skip: list = None):
        self._is_sketch_only = is_sketch_only
        if self._is_sketch_only:
            self._nonterminals_to_skip = nonterminals_to_skip
        else:
            self._nonterminals_to_skip = None
        self._root = ASTNode(root_rule, parent=None, node_id=0,
                             nonterminals_to_skip=nonterminals_to_skip)
        self._curr_node = self._root
        self._last_node = self._curr_node
        self._curr_node_id = 1
        self._nodes = [self._root]

    def clean_up(self):
        def traverse(node):
            node.clean_up()
            for rhs in node.rhs_nodes:
                traverse(rhs)
        traverse(self._root)

    @property
    def root(self):
        return self._root

    @property
    def nodes(self):
        return self._nodes

    @property
    def curr_node_id(self):
        return self._curr_node_id

    def increase_node_id(self):
        self._curr_node_id += 1

    @property
    def is_complete(self):
        def traverse(node):
            if node is None:
                return False
            _is_complete = node.is_complete
            for rhs in node.rhs_nodes:
                _is_complete &= traverse(rhs)
            return _is_complete
        return traverse(self._root)

    def get_curr_node(self):
        return self._curr_node

    def get_last_production_rule(self):
        return self._last_node.production_rule

    def add_rule(self, rule):
        node = ASTNode(rule, parent=self._curr_node, node_id=self._curr_node_id,
                       nonterminals_to_skip=self._nonterminals_to_skip)
        self._nodes.append(node)
        self._curr_node_id += 1
        self._curr_node.add_node(node)
        self._last_node = node
        if node.is_complete:
            _node = node
            while _node != self._root and _node.is_complete:
                _node = _node.parent
            self._curr_node = _node
        else:
            # self._last_node = self._curr_node
            self._curr_node = node

    def get_production_rules(self):
        def traverse(node, rules):
            if node is not None:
                rules.append(node.production_rule)
                for rhs in node.rhs_nodes:
                    traverse(rhs, rules)
        production_rules = list()
        traverse(self._root, production_rules)
        return production_rules

    def get_parent_production_rules(self):
        def traverse(node, rules):
            if node is not None:
                if node.parent is None:
                    rules.append(None)
                else:
                    rules.append(node.parent.production_rule)
                for rhs in node.rhs_nodes:
                    traverse(rhs, rules)
        production_rules = list()
        traverse(self._root, production_rules)
        return production_rules

    def get_parent_ids(self):
        def traverse(node, ids):
            if node is not None:
                if node.parent is None:
                    ids.append(-1)
                else:
                    ids.append(node.parent.node_id)
                for rhs in node.rhs_nodes:
                    traverse(rhs, ids)
        ids = list()
        traverse(self._root, ids)
        return ids

    def get_curr_parent_node(self):
        return self._curr_node

    def get_curr_non_terminal(self):
        return self._curr_node.get_curr_non_terminal()


def _print(node, indent, string_array):
    if not isinstance(node, ASTNode):
        # str
        string_array.append('    ' * indent + node)
        return
    string_array.append('    ' * indent + node.lhs)
    if len(node.rhs) > 0:
        for child in node.rhs:
            _print(child, indent + 1, string_array)


def print_ast(ast):
    print(get_tree_str(ast.root))


def get_tree_str(t):
    string_array = list()
    _print(t, 0, string_array)
    return '\n'.join(string_array)
