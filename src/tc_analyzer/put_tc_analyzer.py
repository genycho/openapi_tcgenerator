#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from common import common_utils
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
from model.api_tc_info import ApiTCInfo
from tc_analyzer.base_tc_anayzer import BasicTCAnalyzer
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

class PutJsonBodyTypeTCAnalyzer(BasicTCAnalyzer):
    """
    PUT/PATCH Method, json body, multipart 
    """
    jsonbody_str:str
    
    def get_tclist(self,api_info:ApiInfo):
        """
        """
        tc_list = []
        self.jsonbody_str = ""
        self.reset()
        super().get_tclist(api_info)
        for a_param in api_info.parameters:
            param_type = a_param['in']
            p_name = a_param['name']
            # 쿼리 파라미터 체크
            if 'query' == param_type:   # TO_EXTRACT
                required = a_param['required']
                p_type = a_param['type']
                if True == required:
                    if self.query_reqparam_count > 0:
                        self.query_params_required_str+=',\n        '
                        self.query_params_all_str+=',\n        '
                    self.query_params_required_str+=f'"{p_name}":"{p_type}"'
                    self.query_params_all_str+=f'"{p_name}":"{p_type}"'
                    self.query_reqparam_count+=1
                else:
                    if self.query_reqparam_count+self.query_optparam_count > 0:
                        self.query_params_all_str+=',\n        '
                    self.query_params_all_str+=f'"{p_name}":"{p_type}"'
                    self.query_optparam_count +=1
            # path 파라미터 체크
            elif 'path' == a_param['in']:   # TO_EXTRACT
                p_type = a_param['type']
                self.path_params_set_str=(f'test_{p_name} = {self.project_str}_util.get{p_name}()')
                self.path_params_str = f'.format({p_name}=test_{p_name})'
                if p_type == "integer":
                    self.path_params_notexist_str=(f'test_{p_name} = 999999')
                else:
                    self.path_params_notexist_str=(f'test_{p_name} = "not_exist_id"')
            # json 바디 파라미터 체크
            elif 'body' == a_param['in']:   # TO_EXTRACT
                self.jsonbody_str = f'#{a_param["schema"]}'
            elif 'header' == a_param['in']:   # TO_EXTRACT
                self.header_str +=f'"{a_param["name"]}":"{a_param["type"]}"'  #TODO 
        # 1번)기본 호출 - 기본
        tc_list.append(self.get_putjson_basic_tc(api_info))
        # 2번)path 파라미터 있으면, not exist TC 
        if "" != self.path_params_str:
            tc_list.append(self.get_putjson_pathparamnotexist_tc(api_info))
        # 3번)json 바디 있으면 parameterized test 추가
        if "" != self.jsonbody_str:
            tc_list.append(self.get_putjson_parameterzied_tc(api_info))
        # 4번) 에러 응답 상태 코드 
        if api_info.responses != None or len(api_info.responses)>0:
            for a_response_key in api_info.responses.keys():
                try:
                    if 400<=int(a_response_key) and 500 > int(a_response_key):
                        tc_list.append(self.get_putjson_errorreresponse_tc(api_info, a_response_key))
                except Exception as ignore:
                    logger.warning(f"responses status code was not int type, but was {a_response_key}")
        # 5번),6번) 인증정보 없이, 잘못된 인증 정보로 요청 TC 
        if api_info.security != None and len(api_info.security) >0:
            tc_list.append(self.get_putjson_noauth_tc(api_info))
        return tc_list
    
    def get_putjson_noauth_tc(self, api_info,):
        self.test_declartion_str = f"{api_info.operation_id.lower()}_noauth(get_{self.project_str}_baseurl)"
        if self.path_params_str == "" : 
            self.request_str = f"requests.{api_info.operation_id.lower()}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
        else:
            self.request_str = f"requests.{api_info.operation_id.lower()}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.testmethod_declaration = "테스트 목적 : noauth "
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.query_params_str = self.query_params_required_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 401 == response.status_code, response.text\n")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_putjson_errorreresponse_tc(self, api_info, response_code):
        """ 4xx responses """
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl)"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.testmethod_declaration = f"테스트 목적 : Tests for the case of response code= {response_code}, description= {api_info.responses.get(response_code)} "
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.query_params_str = self.query_params_required_str
        this_assert_str_list = []
        this_assert_str_list.append(f"assert {response_code} == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_putjson_parameterzied_tc(self, api_info):
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_parameterized(get_{self.project_str}_baseurl, get_loggedin_session, input, expected)"
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_parameterized(get_{self.project_str}_baseurl, input, expected)"
            if self.path_params_str == "" : 
                self.request_str = f"requests.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.test_pytestmarker_str = '@pytest.mark.skip(reason="상황에 따라 수행")\n@pytest.mark.parametrize("input, expected", {("first_input","first_expected")})'
        tc_info.testfile_declaration = f"This tests to summary:{api_info.summary}, description:{api_info.description}"
        tc_info.testmethod_declaration = "테스트 목적 : pytest parameterized test sample for json request body"
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.query_params_str = self.query_params_required_str
        self.this_assert_str_list = []
        self.this_assert_str_list.append("assert expected == response.status_code, response.text")
        tc_info.assert_str_list = self.this_assert_str_list
        return tc_info

    def get_putjson_pathparamnotexist_tc(self, api_info):
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl, get_loggedin_session)"
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl)"
            if self.path_params_str == "" : 
                self.request_str = f"requests.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        # tc_info = self.get_postjsonbody_basic_tc_object(api_info)
        tc_info.testmethod_declaration = "테스트 목적 : path parameter does not exist, expected 404 "
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.path_params_str = self.path_params_notexist_str
        tc_info.query_params_str = self.query_params_all_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 404 == response.status_code, response.text\n")
        this_assert_str_list.append("assert '' in response.json()")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_putjson_basic_tc(self, api_info):
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl, get_loggedin_session)"
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.{api_info.method}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl)"
            if self.path_params_str == "" : 
                self.request_str = f"requests.{api_info.method}(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.{api_info.method}(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.testfile_declaration = f"API Test for {api_info.operation_id}, {api_info.summary}, \ndescription:{api_info.description}"
        tc_info.testmethod_declaration = "테스트 목적 : basic"
        tc_info.jsonbody_str = self.jsonbody_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 200 == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json\n")
        tc_info.query_params_str = self.query_params_all_str
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

