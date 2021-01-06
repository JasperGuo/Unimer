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
            ("'", " ' "),
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


def get_logical_tokenizer(language: str) -> WordTokenizer:
    splitter = None
    if language == 'funql':
        splitter = FunQLWordSplitter()
        # splitter = FunQLWordSplitter2()
    elif language == 'prolog':
        splitter = PrologWordSplitter()
    #     # splitter = PrologWordSplitter2()
    # elif language == 'prolog2':
    #     splitter = PrologWordSplitter3()
    elif language == 'sql':
        splitter = SQLWordSplitter()
    elif language == 'lambda':
        splitter = LambdaCalculusWordSplitter()
    assert splitter is not None
    return splitter


if __name__ == '__main__':
    spliiter = get_logical_tokenizer('sql')
    tokenizer = WordTokenizer(spliiter)
    from atis_normalization import normalize_lambda_calculus, preprocess_funql, normalize_prolog_variable_names, preprocess_sql
    normalized_lf = preprocess_sql("SELECT DISTINCT flight_1.flight_id FROM flight flight_1 , airport airport_1 , airport_service airport_service_1 , city city_1 WHERE flight_1.to_airport = airport_1.airport_code AND airport_1.airport_code = 'MKE' AND flight_1.from_airport = airport_service_1.airport_code AND airport_service_1.city_code = city_1.city_code AND 1 = 1")
    print(normalized_lf)
    tokens = tokenizer.tokenize(normalized_lf)
    print(tokens)
