# coding=utf8

from typing import List
from overrides import overrides
from allennlp.data.tokenizers import Token, WordTokenizer
from allennlp.data.tokenizers.word_splitter import WordSplitter


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


class SQLWordSplitter(WordSplitter):
    @overrides
    def split_words(self, logical_form: str) -> List[Token]:
        normalized_sql = logical_form
        replacements = [
            ('(', ' ( '),
            (')', ' ) '),
            (',', ' , '),
            ('.', ' . '),
            ("'", " \\' ")
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
            ("'", " \\' ")
        ]
        for a, b in replacements:
            normalized_lc = normalized_lc.replace(a, b)
        tokens = [Token(t) for t in normalized_lc.split()]
        return tokens


def get_logical_tokenizer(language: str) -> WordTokenizer:
    splitter = None
    if language == 'prolog':
        splitter = PrologWordSplitter()
    elif language == 'prolog2':
        splitter = PrologWordSplitter2()
    elif language == 'funql':
        splitter = FunQLWordSplitter()
    elif language == 'funql2':
        splitter = FunQLWordSplitter2()
    elif language == 'sql':
        splitter = SQLWordSplitter()
    elif language == 'lambda':
        splitter = LambdaCalculusWordSplitter()
    assert splitter is not None
    return splitter


if __name__ == '__main__':
    prolog = "(lambda $0:e (and (job $0) (language $0 perl) (company $0 \'Lockheed Martin Aeronautics\') (loc $0 colorado)))"
    spliiter = get_logical_tokenizer('lambda')
    tokenizer = WordTokenizer(spliiter)
    tokens = tokenizer.tokenize(prolog)
    print(tokens)
