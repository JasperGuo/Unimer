# coding=utf8

from typing import List
from overrides import overrides
from allennlp.data.tokenizers import Token, WordTokenizer
from allennlp.data.tokenizers.word_splitter import WordSplitter


class FunQLWordSplitter(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lf = logical_form.replace(" ", "::")
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ("\\+", " \\+ "),
        ]
        for a, b in replacements:
            normalized_lf = normalized_lf.replace(a, b)
        tokens = [Token(t) if "::" not in t else Token(
            t.replace("::", " ")) for t in normalized_lf.split()]
        return tokens


class FunQLWordSplitter2(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lf = logical_form.replace(" ", "::")
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ("\\+", " \\+ "),
            ("'", " ' "),
        ]
        for a, b in replacements:
            normalized_lf = normalized_lf.replace(a, b)
        tokens = list()
        for t in normalized_lf.split():
            if "::" not in t:
                tokens.append(Token(t))
            else:
                tokens += [Token(_t) for _t in t.replace("::", " ").split()]
        return tokens


class PrologWordSplitter(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lf = logical_form.replace(" ", "::")
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ("\\+", " \\+ "),
        ]
        for a, b in replacements:
            normalized_lf = normalized_lf.replace(a, b)
        tokens = [Token(t) if "::" not in t else Token(
            t.replace("::", " ")) for t in normalized_lf.split()]
        return tokens


class PrologWordSplitter2(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lf = logical_form.replace(" ", "::")
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ("\\+", " \\+ "),
            ("'", " ' "),
        ]
        for a, b in replacements:
            normalized_lf = normalized_lf.replace(a, b)
        tokens = list()
        for t in normalized_lf.split():
            if "::" not in t:
                tokens.append(Token(t))
            else:
                tokens += [Token(_t) for _t in t.replace("::", " ").split()]
        return tokens


class PrologWordSplitter3(WordSplitter):

    PREDS = [
        'cityid', 'countryid', 'placeid', 'riverid', 'stateid',
        'capital', 'city', 'lake', 'major', 'mountain', 'place', 'river',
        'state', 'area', 'const', 'density', 'elevation', 'high_point',
        'higher', 'loc', 'longer', 'low_point', 'lower', 'len', 'next_to',
        'population', 'size', 'traverse',
        'answer', 'largest', 'smallest', 'highest', 'lowest', 'longest',
        'shortest', 'count', 'most', 'fewest', 'sum']

    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lf = logical_form.replace(" ", "::")
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ("\\+", " \\+ "),
            ("'", " ' "),
        ]
        for a, b in replacements:
            normalized_lf = normalized_lf.replace(a, b)
        tokens = list()
        for t in normalized_lf.split():
            if "::" not in t:
                if t in self.PREDS:
                    tokens.append(Token("_%s" % t))
                else:
                    tokens.append(Token(t))
            else:
                tokens += [Token(_t) for _t in t.replace("::", " ").split()]
        return tokens


class SQLWordSplitter(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_sql = logical_form
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ("'", ""),
            ('.', ' . '),
            ("\\+", " \\+ "),
        ]
        for a, b in replacements:
            normalized_sql = normalized_sql.replace(a, b)
        tokens = [Token(t) for t in normalized_sql.split()]
        return tokens


class LambdaCalculusWordSplitter(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lc = logical_form
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            ("\\+", " \\+ "),
        ]
        for a, b in replacements:
            normalized_lc = normalized_lc.replace(a, b)
        tokens = [Token(t) for t in normalized_lc.split()]
        return tokens


class LambdaCalculusWordSplitter2(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_lc = logical_form
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            ("\\+", " \\+ "),
        ]
        for a, b in replacements:
            normalized_lc = normalized_lc.replace(a, b)
        tokens = list()
        for t in normalized_lc.split():
            if any([t.endswith(suffix) for suffix in [':s', ':co', ':n', ':c', ':r', ':m', ':p', ':lo']]):
                _t = t.replace(":", " : ").replace("_", " ")
                tokens.append(Token("'"))
                for _token in _t.split():
                    tokens.append(Token(_token))
                tokens.append(Token("'"))
            else:
                tokens.append(Token(t))
        return tokens


def get_logical_tokenizer(language: str) -> WordTokenizer:
    splitter = None
    if language == 'funql':
        # splitter = FunQLWordSplitter()
        splitter = FunQLWordSplitter2()
    elif language == 'prolog':
        # splitter = PrologWordSplitter()
        splitter = PrologWordSplitter2()
    elif language == 'prolog2':
        splitter = PrologWordSplitter3()
    elif language == 'sql':
        splitter = SQLWordSplitter()
    elif language == 'lambda':
        splitter = LambdaCalculusWordSplitter()
    elif language == 'lambda2':
        splitter = LambdaCalculusWordSplitter2()
    assert splitter is not None
    return splitter


if __name__ == '__main__':
    spliiter = get_logical_tokenizer('lambda2')
    tokenizer = WordTokenizer(spliiter)
    tokens = tokenizer.tokenize("(count:<<e,t>,i> (lambda $0:e (and:<t*,t> (river:<r,t> $0) (loc:<lo,<lo,t>> $0 new_york:s))))")
    print(tokens)
