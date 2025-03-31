#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from common import common_utils
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
from model.api_tc_info import ApiTCInfo
import logging
from common.log_config import setup_logging
from tc_analyzer.base_tc_anayzer import BasicTCAnalyzer

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

class PostJsonBodyTypeTCAnalyzer(BasicTCAnalyzer):
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
        self.formparams_str=""
        self.multipart_file_str=""
        self.jsonbody_str = ""

    def analyze_testcases(self,api_info:ApiInfo):
        tc_list = []
        self.reset()
        self.analyze_input_parameters(api_info)
        # 1st) 기본 호출 - 기본
        tc_list.append(self.get_postjsonbody_basic_tc_object(api_info))
        # 2nd) path 파라미터 있으면, not exist TC 
        if "" != self.path_params_str:
            tc_list.append(self.get_postjsonbody_pathparamnotexist_tc(api_info))
        # 3rd) json 바디 있으면 parameterized test 추가
        if "" != self.jsonbody_str:
            tc_list.append(self.get_postjsonbody_parameterzied_tc(api_info))
        # 4th) 에러 응답 상태 코드 
        if api_info.responses != None or len(api_info.responses)>0:
            for a_response_key in api_info.responses.keys():
                try:
                    if 400<=int(a_response_key) and 500 > int(a_response_key):
                        tc_list.append(self.get_errorreresponse_tc(api_info, a_response_key))
                except Exception as ignore:
                    logger.warning(f"responses status code was not int type, but was {a_response_key}")
        # 5th),6th) 인증정보 없이, 잘못된 인증 정보로 요청 TC 
        if api_info.security != None and len(api_info.security) >0:
            tc_list.append(self.get_noauth_tc(api_info))
        return tc_list
    
    def get_noauth_tc(self, api_info,):
        # tc_info = self.get_postjsonbody_basic_tc_object(api_info)
        tc_info = self.get_basic_tc_object(api_info)
        self.test_declartion_str = f"{api_info.operation_id.lower()}_noauth(get_{self.project_str}_baseurl)"
        tc_info.testmethod_declaration_str = "테스트 목적 : noauth "
        if self.path_params_str == "" : 
            self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
        else:
            self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.query_params_str = self.query_params_required_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 401 == response.status_code, response.text\n")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_errorreresponse_tc(self, api_info, response_code):
        """ 4xx responses """
        tc_info = self.get_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl, get_loggedin_session)"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl)"
        tc_info.testmethod_description_comment = f"테스트 목적 : Tests for the case of response code= {response_code}, description= {api_info.responses.get(response_code)} "
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.query_params_str = self.query_params_required_str
        this_assert_str_list = []
        this_assert_str_list.append(f"assert {response_code} == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_postjsonbody_parameterzied_tc(self, api_info):
        tc_info = self.get_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_parameterized(get_{self.project_str}_baseurl, get_loggedin_session, input, expected)"
            if self.path_params_str == "" : 
                tc_info.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_parameterized(get_{self.project_str}_baseurl, input, expected)"
            if self.path_params_str == "" : 
                tc_info.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.test_pytestmarker_str = '@pytest.mark.skip(reason="상황에 따라 수행")\n@pytest.mark.parametrize("input, expected", {("first_input","first_expected")})'
        tc_info.testmethod_description_comment = "테스트 목적 : pytest parameterized test sample for json request body"
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.query_params_str = self.query_params_required_str
        this_assert_str_list = []
        this_assert_str_list.append("assert expected == response.status_code, response.text\n")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_postjsonbody_pathparamnotexist_tc(self, api_info):
        tc_info = self.get_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl, get_loggedin_session)"
            if self.path_params_str == "" : 
                tc_info.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl)"
            if self.path_params_str == "" : 
                tc_info.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.testmethod_declaration_str = "테스트 목적 : path parameter does not exist, expected 404 "
        tc_info.jsonbody_str = self.jsonbody_str
        tc_info.path_params_str = self.path_params_notexist_str
        tc_info.query_params_str = self.query_params_required_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 404 == response.status_code, response.text\n")
        this_assert_str_list.append("assert '' in response.json()")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def get_postjsonbody_basic_tc_object(self, api_info):
        tc_info = self.get_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl, get_loggedin_session)"
            if self.path_params_str == "" : 
                tc_info.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            tc_info.testmethod_declaration_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl)"
            if tc_info.path_params_str == "" : 
                tc_info.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.testmethod_description_comment = "테스트 목적 : basic"
        tc_info.jsonbody_str = self.jsonbody_str
        this_assert_str_list = []
        if '201' in api_info.responses.keys():
            this_assert_str_list.append("assert 201 == response.status_code, response.text\n")
        else:            
            this_assert_str_list.append("assert 200 == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.query_params_str = self.query_params_required_str
        tc_info.assert_str_list = this_assert_str_list
        return tc_info
    
    def get_basic_tc_object(self, api_info):
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
        self.copy_pre_tcinfo(tc_info)
        if api_info.security != None and len(api_info.security) >0:
            if self.path_params_str == "" :
                tc_info.request_str = f"get_loggedin_session.{api_info.method.lower()}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"get_loggedin_session.{api_info.method.lower()}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            if self.path_params_str == "" : 
                tc_info.request_str = f"requests.{api_info.method.lower()}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH"
            else:
                tc_info.request_str = f"requests.{api_info.method.lower()}(get_{self.project_str}_baseurl + constants.{api_info.method.upper()}_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info.query_params_str = self.query_params_required_str
        return tc_info

class PostMultipartTypeTCAnalyzer(BasicTCAnalyzer):
    def analyze_testcases(self,api_info:ApiInfo):
        return None
    
    def get_tclist(self,api_info:ApiInfo):
        # 0) (A)json 바디 타입 vs (B)multipart-formdata 분기
        # B-1) basic 수행, 파일 첨부. form-param 이 있는지 없는지. 
        # B-2) basic 수행, 파일 첨부. form-param 별 존재하지 않을 때. 
        # B-3) file이 없을 때  
        tc_list = []
        # 1번)기본 호출
        self.formparams_str = "{"
        for a_param in api_info.parameters:
            name = a_param['name']
            # path 파라미터 체크
            if 'path' == a_param['in']:   # TO_EXTRACT
                p_type = a_param['type']
                self.path_params_set_str=(f'test_{name} = {self.project_str}_util.get{name}()')
                self.path_params_str = f'.format({name}=test_{name})'
                if p_type == "integer":
                    self.path_params_notexist_str=(f'test_{name} = 999999')
                else:
                    self.path_params_notexist_str=(f'test_{name} = "not_exist_id"')
            elif 'formData' == a_param['in']:   # TO_EXTRACT
                #form params
                if "file" != a_param['type']:
                    if self.formparams_str !="{":
                        self.formparams_str +=f'        ,"{a_param['name']}":"{a_param['type']}" #required:{a_param['required']}\n'
                    else:
                        self.formparams_str +=f'\n        "{a_param['name']}":"{a_param['type']}" #required:{a_param['required']}\n'
                elif "file" == a_param['type']:
                    self.multipart_file_str =f'test_file_path = get_dirpath + "/{api_info.project_title}/test_resource/sample_file.jpg"\n    files= {{\n        "{a_param['name']}": ("sample_file.jpg", open(test_file_path, "rb"),"image/jpeg")\n    }}'
        self.formparams_str += "    }"


        
        # 1번)기본 호출 - 기본
        tc_list.append(self.get_postmultipart_basic_tc_object(api_info))
        # 2번)path 파라미터 있으면, not exist TC 
        if "" != self.path_params_str:
            tc_list.append(self.get_postmultipart_pathparamnotexist_tc(api_info))
        # 4번) 에러 응답 상태 코드 
        if api_info.responses != None or len(api_info.responses)>0:
            for a_response_key in api_info.responses.keys():
                try:
                    if 400<=int(a_response_key) and 500 > int(a_response_key):
                        tc_list.append(self.get_postmultipart_errorreresponse_tc(api_info, a_response_key))
                except Exception as ignore:
                    logger.warning(f"responses status code was not int type, but was {a_response_key}")
        # 5번),6번) 인증정보 없이, 잘못된 인증 정보로 요청 TC 
        if api_info.security != None and len(api_info.security) >0:
            tc_list.append(self.get_postmultipart_noauth_tc(api_info))
        return tc_list
    
    def _get_postmultipart_noauth_tc(self, api_info,):
        self.test_declartion_str = f"{api_info.operation_id.lower()}_noauth(get_{self.project_str}_baseurl, get_dirpath)"
        tc_info.testmethod_declaration = "테스트 목적 : noauth "
        if self.path_params_str == "" : 
            self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH"
        else:
            self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.GET_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        this_assert_str_list = []
        this_assert_str_list.append("assert 401 == response.status_code, response.text\n")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def _get_postmultipart_errorreresponse_tc(self, api_info, response_code):
        """ 4xx responses """
        tc_info = self.get_postmultipart_basic_tc_object(api_info)
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl, get_loggedin_session, get_dirpath)"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_{response_code}(get_{self.project_str}_baseurl, get_dirpath)"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.testmethod_declaration = f"테스트 목적 : Tests for the case of response code= {response_code}, description= {api_info.responses.get(response_code)} "
        this_assert_str_list = []
        this_assert_str_list.append(f"assert {response_code} == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def _get_postmultipart_pathparamnotexist_tc(self, api_info):
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl, get_loggedin_session, get_dirpath)"
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_notexistid(get_{self.project_str}_baseurl, get_dirpath)"
            if self.path_params_str == "" : 
                self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.testmethod_declaration = "테스트 목적 : path parameter does not exist, expected 404 "
        tc_info.pathparam = self.path_params_notexist_str
        this_assert_str_list = []
        this_assert_str_list.append("assert 404 == response.status_code, response.text\n")
        this_assert_str_list.append("assert '' in response.json()")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

    def _get_postmultipart_basic_tc_object(self, api_info):
        if api_info.security != None and len(api_info.security) >0:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl, get_loggedin_session, get_dirpath)"
            if self.path_params_str == "" : 
                self.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"get_loggedin_session.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        else:
            self.test_declartion_str = f"{api_info.operation_id.lower()}_basic(get_{self.project_str}_baseurl, get_dirpath)"
            if self.path_params_str == "" : 
                self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH"
            else:
                self.request_str = f"requests.post(get_{self.project_str}_baseurl + constants.POST_{api_info.operation_id.upper()}_APIPATH{self.path_params_str}"
        tc_info = ApiTCInfo()
        tc_info.set_apiinfo(api_info)
        self.set_commoninfo(tc_info)
        tc_info.testfile_declaration = f"API Test for {api_info.operation_id}, {api_info.summary}, \ndescription:{api_info.description}"
        tc_info.testmethod_declaration = "테스트 목적 : basic(multipart/form-data)"
        tc_info.formparams_str = self.formparams_str
        tc_info.multipart_file_str = self.multipart_file_str
        this_assert_str_list = []
        if '201' in api_info.responses.keys():
            this_assert_str_list.append("assert 201 == response.status_code, response.text\n")
        else:            
            this_assert_str_list.append("assert 200 == response.status_code, response.text\n")
        this_assert_str_list.append("response_json = response.json()\n")
        this_assert_str_list.append("assert '' in response_json")
        tc_info.assert_str_list = this_assert_str_list
        return tc_info

