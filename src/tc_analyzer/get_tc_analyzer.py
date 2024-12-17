#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from common import qe_utils
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
from model.api_tc_info import ApiTCInfo
from tc_analyzer.base_tc_anayzer import BasicTCAnalyzer
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

class GetTypeTCAnalyzer(BasicTCAnalyzer):
    query_params_required_str:str
    query_params_all_str:str
    path_params_str:str
    path_params_set_str:str
    path_params_notexist_str:str
    header_str:str
    project_str:str
    request_str:str
    query_reqparam_count:int
    query_optparam_count:int
    assert_str_list:list
    test_declartion_str:str

    def __init__(self):
        self.reset()

    def reset(self):
        self.query_params_required_str = ""
        self.query_params_all_str = ""
        self.path_params_str = ""
        self.path_params_set_str = ""
        self.path_params_notexist_str=""
        self.header_str = ""
        self.project_str = ""
        self.request_str = ""
        self.query_reqparam_count = 0
        self.query_optparam_count = 0
        self.assert_str_list = []
        self.test_declartion_str = ""
        self.testmethod_declaration = ""
        self.formparms_str=""
        self.multipart_file_str=""

    def get_tclist(self,api_info:ApiInfo):
        """
        """
        tc_list = []
        self.reset()
        super().get_commoninfo(api_info)
        ## get인 경우 parameters만 꺼내서. 
        for a_inputparam in api_info.parameters:
            a_inputparam : InputParameterInfo
            # 쿼리 파라미터 체크
            if 'query' == a_inputparam.in_type:
                p_type = a_inputparam.param_type
                if True == a_inputparam.required:
                    if self.query_reqparam_count >0:
                        self.query_params_required_str+=',\n        '
                        self.query_params_all_str+=',\n        '
                    self.query_params_required_str+=f'"{a_inputparam.param_name}":"{p_type}"'
                    self.query_params_all_str+=f'"{a_inputparam.param_name}":"{p_type}"'
                    self.query_reqparam_count+=1
                else:
                    if self.query_reqparam_count+self.query_optparam_count > 0:
                        self.query_params_all_str+=',\n        '
                    self.query_params_all_str+=f'"{a_inputparam.param_name}":"{p_type}"'
                    self.query_optparam_count +=1
            # path 파라미터 체크
            elif 'path' == a_inputparam.in_type:
                p_type = a_inputparam.param_type
                self.path_params_set_str=(f'test_{a_inputparam.param_name} = {self.project_str}_util.get{a_inputparam.param_name}()')
                self.path_params_str = f'.format({a_inputparam.param_name}=test_{a_inputparam.param_name})'
                if p_type == "integer":
                    self.path_params_notexist_str=(f'test_{a_inputparam.param_name} = 999999')
                else:
                    self.path_params_notexist_str=(f'test_{a_inputparam.param_name} = "not_exist_id"')
            elif 'header' == a_inputparam.in_type:
                pass    # TODO
            elif 'formData' == a_inputparam.in_type:
                pass    # TODO
            
        # 1번)기본 호출 - 필수/선택 파라미터 있으면, 1번은 필수만
        tc_list.append(self.get_first_basic_tc(api_info))
        if self.query_optparam_count > 0:
        # 2번)기본호출 - 필수/선택 모든 파라미터 
            tc_list.append(self.get_second_basic_tc(api_info))
        # 3번) path parameter가 있는 경우 not_exist_id TC 
        if "" != self.path_params_str:
            tc_list.append(self.get_third_pathparamnotexist_tc(api_info))
        # 4번) 에러 응답 상태 코드 
        if api_info.responses != None or len(api_info.responses)>0:
            for a_response_key in api_info.responses.keys():
                try:
                    if 400<=int(a_response_key) and 500 > int(a_response_key):
                        tc_list.append(self.get_errorreresponse_tc(api_info, a_response_key))
                except Exception as ignore:
                    logger.warning(f"responses status code was not int type, but was {a_response_key}")
        # 5번),6번) 인증정보 없이, 잘못된 인증 정보로 요청 TC 
        if api_info.security != None and len(api_info.security) >0:
            tc_list.append(self.get_noauth_tc(api_info))
        return tc_list
    
    def get_noauth_tc(self, api_info,):
        tc_info = self.get_basic_tc_object(api_info)
        self.test_declartion_str = f"{api_info.operation_id.lower()}_noauth(get_{self.project_str}_baseurl)"
        tc_info.testmethod_declaration = "테스트 목적 : noauth "
        if self.path_params_str == "" : 
            self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
        else:
            self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        self.set_commoninfo(tc_info)
        tc_info.query_params_str = self.query_params_all_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 401 == response.status_code, response.text\n")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_errorreresponse_tc(self, api_info, response_code):
        """ 4xx responses """
        tc_info = self.get_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl)"
        tc_info.testmethod_declaration = f"테스트 목적 : Tests for the {response_code}: {api_info.responses.get(response_code)} "
        self.set_commoninfo(tc_info)
        # if api_info.security != None and len(api_info.security) >0:
        #     if self.path_params_str == "" : 
        #         self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
        #     else:
        #         self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        # else:
        #     if self.path_params_str == "" : 
        #         self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
        #     else:
        #         self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        # self.set_commoninfo(tc_info)
        this_assert_str_list = []
        this_assert_str_list.append(f"assert {response_code} == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info
    
    def get_third_pathparamnotexist_tc(self, api_info):
        """ not exist path id for 404 returns """
        tc_info_3 = self.get_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl)"
        tc_info_3.testfile_declaration = f"This tests to summary:{api_info.summary}, description:{api_info.description}"
        tc_info_3.testmethod_declaration = "테스트 목적 : path parameter does not exist, expected 404 "
        if api_info.security != None and len(api_info.security) >0:
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            if self.path_params_str == "" : 
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        self.set_commoninfo(tc_info_3)
        tc_info_3.path_params_set_str = self.path_params_notexist_str
        tc_info_3.query_params_str = self.query_params_all_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 404 == response.status_code, response.text\n")
        this_assert_str_list.append("assert '' in response.json()")
        tc_info_3.assert_str_list = this_assert_str_list
        return tc_info_3

    def get_second_basic_tc(self, api_info):
        """ 파라미터 부분만 다른 2번째 basic TC 정의 - 별도 함수로 공용화. GET 등 메소드별 차이가 있을까? """
        tc_info_2 = ApiTCInfo()
        tc_info_2.set_apiinfo(api_info)
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_allparams(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_allparams(get_{self.project_str}_baseurl)"
        tc_info_2.testfile_declaration = f"This tests to summary:{api_info.summary}, description:{api_info.description}"
        tc_info_2.testmethod_declaration = "테스트 목적 : basic(all params)"
        if api_info.security != None and len(api_info.security) >0:
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            if self.path_params_str == "" : 
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        self.set_commoninfo(tc_info_2)
        tc_info_2.query_params_str = self.query_params_all_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 200 == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info_2.query_params_str = self.query_params_required_str
        tc_info_2.assert_str_list = this_assert_str_list
        return tc_info_2

    def get_first_basic_tc(self, api_info):
        """ """
        self.testfile_declaration = f"API Test for {api_info.operation_id}, {api_info.summary}, \ndescription:{api_info.description}"
        self.testmethod_declaration = "테스트 목적 : basic(required params only)"
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl, get_loggedin_session)"
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl)"
            if self.path_params_str == "" : 
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl)"  
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        this_assert_str_list = []
        this_assert_str_list.append("assert 200 == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.query_params_str = self.query_params_required_str
        tc_info.assert_str_list = this_assert_str_list
        return tc_info
    
    def get_basic_tc_object(self, api_info):
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        if api_info.security != None and len(api_info.security) >0:
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            if self.path_params_str == "" : 
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.query_params_str = self.query_params_required_str
        return tc_info
    
    def set_commoninfo(self,tc_info):
        tc_info.project_str = self.project_str
        tc_info.header_str = self.header_str
        tc_info.path_params_str = self.path_params_str
        tc_info.query_params_str = self.query_params_all_str
        tc_info.test_declartion_str = self.test_declartion_str
        tc_info.request_str=self.request_str
        tc_info.assert_str_list=self.assert_str_list
        tc_info.path_params_set_str = self.path_params_set_str