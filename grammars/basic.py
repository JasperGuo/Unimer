# coding=utf8

from typing import List, Dict

class ProductionRule:
    def __init__(self, rule_id: int, rule: str, lhs: str, rhs: List[str], rhs_nonterminal: List[str], attrs: Dict = None):
        self._rule = rule
        self._rule_id = rule_id
        self._lhs = lhs
        self._rhs = rhs
        self._rhs_nonterminal = rhs_nonterminal
        self._attrs = attrs

    @property
    def rule_id(self):
        return self._rule_id

    @property
    def rhs_nonterminal(self):
        return self._rhs_nonterminal

    @property
    def lhs(self):
        return self._lhs

    @property
    def rhs(self):
        return self._rhs

    @property
    def attrs(self):
        return self._attrs

    @property
    def rule(self):
        return self._rule

    def set_attr(self, key, value):
        if self._attrs is None:
            self._attrs = dict()
        self._attrs[key] = value

    def __str__(self):
        attr_str = "" if self.attrs is None else str(self.attrs)
        if attr_str:
            return self._rule + " Attrs: " + attr_str
        return self._rule

    def __repr__(self):
        return str(self)