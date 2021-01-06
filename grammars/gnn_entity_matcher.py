# coding=utf8

import os
from .geo import geo_entity_extractor, geo_gnn_entity_matcher
from .atis import atis_entity_extractor, atis_gnn_entity_matcher


def get_gnn_entity_matcher(task, language):
    matcher = None
    if task == 'geo':
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'geo')
        entity_path = os.path.join(base_path, 'geo_entities.json')
        if language in ['funql', 'prolog']:
            matcher = geo_gnn_entity_matcher.GeoGNNEntityMatcher(entity_path)
        elif language == 'lambda':
            matcher = geo_gnn_entity_matcher.GeoLambdaCalculusGNNEntityMatcher(entity_path)
        elif language == 'sql':
            matcher = geo_gnn_entity_matcher.GeoSQLGNNEntityMatcher(entity_path)
    elif task == 'atis':
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'atis', 'db')
        if language in ['lambda', 'lambda2', 'lambda3', 'lambda4',]:
            matcher = atis_gnn_entity_matcher.ATISGNNLambdaCalculusEntityMatcher(db_path)
        elif language in ['funql', 'prolog']:
            matcher = atis_gnn_entity_matcher.ATISGNNEntityMatcher(db_path)
    return matcher


def get_gnn_entity_extractor(task, language):
    """
    Extract entities from logical form
    :param task:
    :param language:
    :return:
    """
    extractor = None
    if task == 'geo':
        if language == 'funql':
            extractor = geo_entity_extractor.funql_entity_extractor
        elif language == 'prolog':
            extractor = geo_entity_extractor.prolog_entity_extractor
        elif language == 'lambda':
            extractor = geo_entity_extractor.lambda_calculus_entity_extractor
        elif language == 'sql':
            extractor = geo_entity_extractor.sql_entity_extractor
    elif task == 'atis':
        if language == 'lambda':
            extractor = atis_entity_extractor.lambda_calculus_entity_extractor
        elif language == 'funql':
            extractor = atis_entity_extractor.funql_entity_extractor
        elif language == 'prolog':
            extractor = atis_entity_extractor.prolog_entity_extractor
    return extractor


def get_gnn_entity_replacer(task, language):
    """
    Replace entities in logical form with recognized entities from utterance
    :param task:
    :param language:
    :return:
    """
    replacer = None
    if task == 'geo':
        if language == 'funql':
            replacer = geo_entity_extractor.replace_funql_entity
        elif language == 'prolog':
            replacer = geo_entity_extractor.replace_prolog_entity
        elif language == 'lambda':
            replacer = geo_entity_extractor.replace_lambda_calculus_entity
        elif language == 'sql':
            replacer = geo_entity_extractor.replace_sql_entity
    elif task == 'atis':
        if language == 'lambda':
            replacer = atis_entity_extractor.replace_lambda_calculus_entity
        elif language == 'funql':
            replacer = atis_entity_extractor.replace_funql_entity
        elif language == 'prolog':
            replacer = atis_entity_extractor.replace_prolog_entity
    return replacer
