#-*- coding: utf-8 -*-
import os, sys, io
import pytest
import json, time
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
from tc_analyzer.get_tc_analyzer import GetTypeTCAnalyzer

def _make_inputparam(in_type, name, type, description, required:bool):
    input_param = InputParameterInfo()
    input_param.default_value = str(type)
    input_param.description = description
    input_param.in_type = in_type
    input_param.param_type = type
    input_param.required = required
    input_param.param_name = name
    return input_param

def _make_apiinfo(api_name, path_param_count, req_param_count, opt_param_count):
    api_info = ApiInfo()
    api_info.project_title = ""
    api_info.base_path = "/testpath"
    api_info.path = f"/test-api-{api_name.lower()}"
    api_info.base_url = "http://test.com"
    api_info.description = f"테스트 API {api_name}"
    api_info.summary = f"summary {api_name}"
    api_info.input_content_type = ""
    api_info.method = "GET"
    api_info.name = f"{api_name}"
    api_info.operation_id = f"{api_name.lower()}"
    api_info.output_content_type = ""
    for i in range(path_param_count):
        api_info.parameters.append(_make_inputparam("path", f"path_param_{i}", "string", f"path_param_{i}", True))    
    for i in range(req_param_count):
        api_info.parameters.append(_make_inputparam("query", f"req_param_{i}", "string", f"req_param_{i}", True))    
    for i in range(opt_param_count):
        api_info.parameters.append(_make_inputparam("query", f"opt_param_{i}", "string", f"opt_param_{i}", False))
    api_info.requestBody = ""
    api_info.responses = {"200": {"description": "Successful Response","content": {"application/json": {"schema": {}}}},"422": {"description": "Validation Error","content": {"application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}}}}
    api_info.security = '{"HTTPBearer": []}'
    api_info.tag = "{'test'}"
    return api_info

def test_get_tc_analyzer_1():
    """
    """
    get_tc_analyzer = GetTypeTCAnalyzer()

    test_api_info = _make_apiinfo("testApi", 0, 1,3)
    result_tc_list = get_tc_analyzer.analyze_testcases(test_api_info)
    assert len(result_tc_list) >0
    assert len(result_tc_list) == 4
    first_basic_tc = result_tc_list[0]
    assert "" != first_basic_tc.assert_str_list
    assert "http://test.com" == first_basic_tc.base_url
    assert "테스트 API testApi" == first_basic_tc.description
    assert "GET" == first_basic_tc.method
    assert "GET_testApi" == first_basic_tc.name
    assert "testapi" == first_basic_tc.operation_id
    assert '"req_param_0":"string"' == first_basic_tc.query_params_str
    assert "get_loggedin_session.get(get__baseurl + constants.GET_TESTAPI_APIPATH" == first_basic_tc.request_str


def test_get_tc_analyzer_2():
    """
    """
    get_tc_analyzer = GetTypeTCAnalyzer()

    test_api_info = _make_apiinfo("testApi", 1, 0,1)
    result_tc_list = get_tc_analyzer.analyze_testcases(test_api_info)
    assert len(result_tc_list) >0
    assert len(result_tc_list) == 5
    first_basic_tc = result_tc_list[0]
    assert "" != first_basic_tc.assert_str_list
    assert "http://test.com" == first_basic_tc.base_url
    assert "테스트 API testApi" == first_basic_tc.description
    assert "GET" == first_basic_tc.method
    assert "GET_testApi" == first_basic_tc.name
    assert "testapi" == first_basic_tc.operation_id
    assert 'test_path_param_0 = _util.getpath_param_0()' == first_basic_tc.path_params_set_str
    assert '.format(path_param_0=test_path_param_0)' == first_basic_tc.path_params_str
    assert 'get_loggedin_session.get(get__baseurl + constants.GET_TESTAPI_APIPATH.format(path_param_0=test_path_param_0)' == first_basic_tc.request_str
    assert 'testapi_basic(get__baseurl, get_loggedin_session)' == first_basic_tc.testmethod_declaration_str
    assert '테스트 목적 : basic(required params only)' == first_basic_tc.testmethod_description_comment
    

