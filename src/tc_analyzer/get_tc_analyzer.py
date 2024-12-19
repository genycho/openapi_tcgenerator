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
    # assert_str_list:list
    # test_declartion_str:str

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
        self.testmethod_declaration = ""
        self.formparms_str=""
        self.multipart_file_str=""
        # self.test_declartion_str = ""
        # self.assert_str_list = []

    def get_tclist(self,api_info:ApiInfo):
        """
        """
        tc_list = []
        self.reset()
        self.testfile_declaration = f"API Test for {api_info.operation_id}, {api_info.summary}, \ndescription:{api_info.description}"
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
                self.header_str += f'"{a_inputparam.param_name}":"{a_inputparam.default_value}"'
            elif 'formData' == a_inputparam.in_type:
                pass    # GET에서 formData로 전달되는 경우는 없을 것으로 보임 
        # 1st TC) 필수 파라미터 기본 호출
        tc_list.append(self._get_first_basic_tc(api_info))
        if self.query_optparam_count > 0:
        # 2nd TC) 선택 파라미터 포함 전체 기본호출
            tc_list.append(self._get_second_basic_tc(api_info))
        # 3rd TC) path parameter가 있는 경우 not_exist_id TC 
        if "" != self.path_params_str:
            tc_list.append(self._get_third_pathparamnotexist_tc(api_info))
        # 4th TC) 에러 응답 상태 코드 
        if api_info.responses != None or len(api_info.responses)>0:
            for a_response_key in api_info.responses.keys():
                try:
                    if 400<=int(a_response_key) and 500 > int(a_response_key):
                        tc_list.append(self._get_errorreresponse_tc(api_info, a_response_key))
                except Exception as ignore:
                    logger.warning(f"responses status code was not int type, but was {a_response_key}")
        # 5th) 인증정보 없이, 6th)잘못된 인증 정보로 요청 TC 
        if api_info.security != None and len(api_info.security) > 0:
            tc_list.append(self._get_noauth_tc(api_info))
        return tc_list
    
    def _get_noauth_tc(self, api_info):
        """ noauth TC 추가  """
        tc_info = self._get_basic_tc_object(api_info)
        tc_info.testmethod_description_comment = "테스트 목적 : noauth "
        tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_noauth(get_{self.project_str}_baseurl)"
        tc_info.assert_str_list+=("assert 401 == response.status_code, response.text\n")
        return tc_info

    def _get_errorreresponse_tc(self, api_info, response_code):
        """ 응답 상태 코드 중 4xx 응답이 포함된 경우를 위한 TC 추가 """
        tc_info = self._get_basic_tc_object(api_info)
        tc_info.testmethod_description_comment = f"테스트 목적 : Tests for the {response_code}: {api_info.responses.get(response_code)} "
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl)"
        tc_info.assert_str_list+=(f"assert {response_code} == response.status_code, response.text\n")
        tc_info.assert_str_list+=("response_json = response.json()\n")
        tc_info.assert_str_list+=("assert '' in response_json")
        return tc_info
    
    def _get_third_pathparamnotexist_tc(self, api_info):
        """ PATH 파라미터가 있는 경우, 이 path 가 존재하지 않는 경우에 대한 TC추가  """
        tc_info = self._get_basic_tc_object(api_info)
        tc_info.testmethod_description_comment = "테스트 목적 : path parameter does not exist, expected 404 "
        tc_info.path_params_set_str = self.path_params_notexist_str
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl)"
        tc_info.assert_str_list+=("assert 404 == response.status_code, response.text\n")
        tc_info.assert_str_list+=("assert '' in response.json()")
        return tc_info
    
    def _get_second_basic_tc(self, api_info):
        """ 선택 파라미터 포함 전체 파라미터 기본 TC 생성 """
        tc_info = self._get_basic_tc_object(api_info)
        tc_info.testmethod_description_comment = "테스트 목적 : basic(all params)"
        tc_info.query_params_str = self.query_params_all_str
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_allparams(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_allparams(get_{self.project_str}_baseurl)"
        tc_info.assert_str_list+=("assert 200 == response.status_code, response.text\n")
        tc_info.assert_str_list+=("response_json = response.json()\n")
        tc_info.assert_str_list+=("assert '' in response_json")
        return tc_info

    def _get_first_basic_tc(self, api_info):
        """ 필수파라미터 only 제일 기본 TC 생성 """
        tc_info = self._get_basic_tc_object(api_info)
        tc_info.testmethod_description_comment = "테스트 목적 : basic(required params only)"
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl)"
        tc_info.assert_str_list+=("assert 200 == response.status_code, response.text\n")
        tc_info.assert_str_list+=("response_json = response.json()\n")
        tc_info.assert_str_list+=("assert '' in response_json")
        return tc_info
    
    def _get_basic_tc_object(self, api_info):
        """ 각 TC별로 일괄 공통된 정보를 세팅한 API TC Info 클래스를 반환하는 내부 함수 \n
            - project_str,  \n
            - header_str,  \n
            - path_params_str : path 파라미터가 있는 경우 / 없는 경우로 분기하여 처리,  \n
            - query_params_str : 필수/선택 파라미터가 섞여 있는 경우 모든 TC 디폴트로 필수 파라미터만으로 설정,  \n
            - test_declartion_str,  \n
            - request_str :  : path 파라미터 유무, 인증 필요 여부에 따른 분기 처리,  \n
            - assert_str_list,  \n
            - path_params_set_str,  \n
        """
        tc_info = ApiTCInfo(api_info)
        self._copy_pre_tcinfo(tc_info)
        if api_info.security != None and len(api_info.security) >0:
            if self.path_params_str == "" :
                tc_info.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"get_loggedin_session.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            if self.path_params_str == "" : 
                tc_info.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"requests.get(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.query_params_str = self.query_params_required_str
        return tc_info
    
    def _copy_pre_tcinfo(self, tc_info:ApiTCInfo):
        """  Parser 클래스에 저장된 값으로 다음 정보를 업데이트. 기본/공통 정보 \n
            - project_str \n
            - header_str \n
            - path_params_str \n
            - request_str \n
            - path_params_set_str \n
        """
        tc_info.project_str = self.project_str
        tc_info.testfile_description_comment = self.testfile_declaration
        tc_info.header_str = self.header_str
        tc_info.path_params_str = self.path_params_str
        tc_info.request_str = self.request_str
        tc_info.path_params_set_str = self.path_params_set_str

    # def _copy_post_tcinfo(self, tc_info:ApiTCInfo):
    #     """ Parser 클래스에 저장된 값으로 다음 정보를 업데이트  \n
    #         - test_declartion_str,  \n
    #         - assert_str_list \n
    #     """
    #     tc_info.test_declartion_str = self.test_declartion_str
    #     tc_info.assert_str_list=self.assert_str_list
