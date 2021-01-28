# coding=utf-8

import re
import numpy as np
from grammars.utils import action_sequence_to_logical_form


def evaluate_grammar_based_prediction(instance, prediction, grammar, preprocessor, postprocessor=None):
    meta_field = instance['meta_field']
    question = meta_field['question']
    truth_logical_form = meta_field['logical_form']

    predicted_rules = prediction['predicted_rules']
    production_rules, rule_str = list(), list()
    for rule_id in predicted_rules:
        rule = grammar.get_production_rule_by_id(int(rule_id))
        if rule is None:
            break
        rule_str.append(rule.rule)
        production_rules.append(rule)

    predicted_logical_form = preprocessor(action_sequence_to_logical_form(rule_str))
    if postprocessor:
        predicted_logical_form = postprocessor(predicted_logical_form)
        truth_logical_form = postprocessor(truth_logical_form)

    is_correct = (truth_logical_form == predicted_logical_form)
    result = {
        "question": question,
        "truth_logical_form": truth_logical_form,
        "predicted_logical_form": predicted_logical_form,
        "is_correct": is_correct
    }
    return is_correct, result


def evaluate_grammar_copy_based_prediction(instance, prediction, grammar, preprocessor, postprocessor=None):
    meta_field = instance['meta_field']
    question = meta_field['question']
    truth_logical_form = meta_field['logical_form']
    question_tokens = instance.fields['source_tokens'].tokens

    predicted_rules = prediction['predicted_rules']
    copy_gates = prediction['recorded_copy_gates']
    copy_weights = prediction['recorded_copy_weights']
    assert len(copy_weights) == len(copy_gates)
    production_rules, rule_str, copy_info = list(), list(), list()
    for idx, rule_id in enumerate(predicted_rules):
        rule = grammar.get_production_rule_by_id(int(rule_id))
        if rule is None:
            break
        rule_str.append(rule.rule)
        production_rules.append(rule)
        if idx > 0 and rule.lhs in grammar.copy_terminal_set:
            gate = copy_gates[idx-1]
            weights = [(token.text, copy_weights[idx-1][sidx],) for (sidx, token) in enumerate(question_tokens)]
            max_weights = max(weights, key=lambda x: x[1])
            copy_info.append({"gate": gate, "rule": rule.rule, "weights": max_weights})

    predicted_logical_form = preprocessor(action_sequence_to_logical_form(rule_str))
    if postprocessor:
        predicted_logical_form = postprocessor(predicted_logical_form)
        truth_logical_form = postprocessor(truth_logical_form)

    is_correct = (truth_logical_form == predicted_logical_form)
    result = {
        "question": question,
        "truth_logical_form": truth_logical_form,
        "predicted_logical_form": predicted_logical_form,
        "copy_info": copy_info,
        "is_correct": is_correct
    }
    return is_correct, result


def evaluate_seq_parsing_prediction(instance, prediction, language):
    source_tokens = instance.fields['source_tokens'].tokens
    gold_tokens = instance.fields['target_tokens'].tokens
    predicted_tokens = prediction['predicted_tokens']

    if language in ['sql', 'lambda', 'prolog']:
        logical_form = ' '.join([s.text for s in gold_tokens[1:-1]])
        predicted_logical_form = ' '.join(predicted_tokens)
    else:
        logical_form = ''.join([s.text for s in gold_tokens[1:-1]])
        predicted_logical_form = ''.join(predicted_tokens)

    is_correct = logical_form == predicted_logical_form
    result = {
        "question": " ".join([s.text for s in source_tokens[1:-1]]),
        "truth_logical_form": logical_form,
        "predicted_logical_form": predicted_logical_form,
        "is_correct": is_correct
    }
    return is_correct, result


def evaluate_seq_copy_parsing_prediction(instance, prediction, language):
    source_tokens = instance.fields['source_tokens'].tokens
    gold_tokens = instance.fields['target_tokens'].tokens
    predicted_tokens = prediction['predicted_tokens']
    meta_field = instance['meta_field']
    source_tokens_to_copy = meta_field['source_tokens_to_copy']

    predicted_logical_form_tokens = list()
    for text in predicted_tokens:
        match = re.match("^@@copy@@(\d+)$", text)
        if match:
            source_index = int(match.group(1))
            if source_index >= len(source_tokens_to_copy):
                text = "@@PADDING@@"
            else:
                text = source_tokens_to_copy[source_index]
        predicted_logical_form_tokens.append(text)

    if language in ['sql', 'lambda', 'lambda2', 'prolog', 'prolog2']:
        logical_form = ' '.join([s.text for s in gold_tokens[1:-1]])
        predicted_logical_form = ' '.join(predicted_logical_form_tokens)
    else:
        logical_form = ''.join([s.text for s in gold_tokens[1:-1]])
        predicted_logical_form = ''.join(predicted_logical_form_tokens)

    is_correct = logical_form == predicted_logical_form
    result = {
        "question": " ".join([s.text for s in source_tokens[1:-1]]),
        "truth_logical_form": logical_form,
        "predicted_logical_form": predicted_logical_form,
        "is_correct": is_correct
    }
    return is_correct, result


def evaluate_gnn_parsing_prediction(instance, prediction, language):
    source_tokens = instance.fields['source_tokens'].tokens
    gold_tokens = instance.fields['target_tokens'].tokens
    predicted_abstract_tokens = prediction['predicted_tokens']
    meta_field = instance.fields['meta_field']

    entity_candidates = meta_field['entity_candidates']

    predicted_logical_form_tokens = list()
    for text in predicted_abstract_tokens:
        match = re.match("^@entity_(\d+)$", text)
        if match:
            source_index = int(match.group(1))
            for entity in entity_candidates:
                if entity['index'] == source_index:
                    text = entity.get('formatted_value', entity['value'])
                    break
            else:
                text = '@@PADDING@@'
        predicted_logical_form_tokens.append(text)

    gold_logical_form_tokens = list()
    for token in gold_tokens[1:-1]:
        text = token.text
        match = re.match("^@entity_(\d+)$", text)
        if match:
            source_index = int(match.group(1))
            for entity in entity_candidates:
                if entity['index'] == source_index:
                    text = entity.get('formatted_value', entity['value'])
                    break
            else:
                text = '@@PADDING@@'
        gold_logical_form_tokens.append(text)

    if language in ['sql', 'lambda', 'lambda2']:
        logical_form = ' '.join(gold_logical_form_tokens)
        predicted_logical_form = ' '.join(predicted_logical_form_tokens)
    else:
        logical_form = ''.join(gold_logical_form_tokens)
        predicted_logical_form = ''.join(predicted_logical_form_tokens)

    is_correct = logical_form == predicted_logical_form
    result = {
        "question": " ".join([s.text for s in source_tokens[1:-1]]),
        "truth_logical_form": logical_form,
        "predicted_logical_form": predicted_logical_form,
        "is_correct": is_correct
    }
    return is_correct, result


def evaluate_translation_prediction(instance, prediction, language):
    source_tokens = instance.fields['source_tokens'].tokens
    gold_tokens = instance.fields['target_tokens'].tokens
    predicted_tokens = prediction['predicted_tokens']

    if language in ['sql', 'lambda']:
        logical_form = ' '.join([s.text for s in source_tokens[1:-1]])
    else:
        logical_form = ''.join([s.text for s in source_tokens[1:-1]])

    gold_question = ' '.join([s.text for s in gold_tokens[1:-1]])
    predicted_question = ' '.join(predicted_tokens)
    is_correct = gold_question == predicted_question
    result = {
        "logical_form": logical_form,
        "truth_question": gold_question,
        "predicted_question": predicted_question,
        "is_correct": is_correct
    }
    return is_correct, result
