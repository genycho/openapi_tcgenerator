#-*- coding: utf-8 -*-
import os, sys, io
import pytest
import json, time
# from common import api_test_util as util
from spec_parser.parser_for_30 import SwaggerParser30
from spec_parser.parser_for_20 import SwaggerParser20

def test_spec_parser30_basic1(get_dirpath):
    spec_file_path1 = get_dirpath+"/test_resource/api_portal_30.json"

    spec_parser = SwaggerParser30()
    result_apiinfo = spec_parser.parse_30swagger_json(spec_file_path1)
    assert 14 == len(result_apiinfo)
    first_api_info_class = result_apiinfo[0]
    assert first_api_info_class.project_title != ""
    assert first_api_info_class.base_url != ""
    assert first_api_info_class.base_path == ""
    assert first_api_info_class.name != ""
    assert first_api_info_class.operation_id != ""
    assert first_api_info_class.summary != ""
    assert first_api_info_class.description != ""
    assert first_api_info_class.path != ""
    assert first_api_info_class.method != ""
    assert first_api_info_class.tag != ""
    assert first_api_info_class.input_content_type != ""
    assert first_api_info_class.output_content_type != ""
    assert first_api_info_class.parameters != ""
    assert first_api_info_class.requestBody != ""


def test_spec_parser30_basic2(get_dirpath):
    spec_file_path2 = get_dirpath+"/test_resource/petstore_v3_openapi.json"

    spec_parser = SwaggerParser30()
    result_apiinfo = spec_parser.parse_30swagger_json(spec_file_path2)
    assert len(result_apiinfo) > 0
    first_api_info_class = result_apiinfo[0]
    assert first_api_info_class.project_title != ""
    assert first_api_info_class.base_url != ""
    assert first_api_info_class.base_path == ""
    assert first_api_info_class.name != ""
    assert first_api_info_class.operation_id != ""
    assert first_api_info_class.summary != ""
    assert first_api_info_class.description != ""
    assert first_api_info_class.path != ""
    assert first_api_info_class.method != ""
    assert first_api_info_class.tag != ""
    assert first_api_info_class.input_content_type != ""
    assert first_api_info_class.output_content_type != ""
    assert first_api_info_class.parameters != ""
    assert first_api_info_class.requestBody != ""


def test_spec_parser20_basic1(get_dirpath):
    spec_file_path = get_dirpath+"/test_resource/petstore_v2_openapi.json"

    spec_parser = SwaggerParser20()
    result_apiinfo = spec_parser.parse_swagger20_json(spec_file_path)
    assert len(result_apiinfo) > 0
    first_api_info_class = result_apiinfo[0]
    assert first_api_info_class.project_title != ""
    assert first_api_info_class.base_url != ""
    assert first_api_info_class.base_path == ""
    assert first_api_info_class.name != ""
    assert first_api_info_class.operation_id != ""
    assert first_api_info_class.summary != ""
    # assert first_api_info_class.description != ""
    assert first_api_info_class.path != ""
    assert first_api_info_class.method != ""
    assert first_api_info_class.tag != ""
    assert first_api_info_class.input_content_type != ""
    assert first_api_info_class.output_content_type != ""
    assert first_api_info_class.parameters != ""
    assert first_api_info_class.requestBody != ""

