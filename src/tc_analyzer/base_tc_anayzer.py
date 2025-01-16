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
from abc import ABC, abstractmethod

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

class BasicTCAnalyzer(ABC):
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
    test_declartion_str:str
    req_content_type:str
    formparams_str:str
    multipart_file_str:str
    jsonbody_str:str
    # testmethod_declaration:str
    # assert_str_list:list

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
        self.formparams_str=""
        self.multipart_file_str=""
        self.test_declartion_str = ""
        self.jsonbody_str = ""
        # self.assert_str_list = []
        # self.testmethod_declaration = ""
    
    def analyze_input_parameters(self, api_info:ApiInfo):
        """ Analyze the input ApiInfo's input parameters and then set class variables
        """
        self.testfile_declaration = f"API Test for {api_info.operation_id}, {api_info.summary}, \ndescription:{api_info.description}"
        if api_info.requestBody != None and api_info.requestBody != "":
            a_inputparam = api_info.requestBody
            self.jsonbody_str += "payload = {\n"
            if '$ref' in a_inputparam.param_type:
                self.jsonbody_str += a_inputparam.param_type
            elif 'properties' in a_inputparam.param_type:
                for a_param in a_inputparam.param_type['properties']:
                    self.jsonbody_str += f'"{a_param}" : "{a_inputparam.param_type['properties'][a_param]}"\n'
            else:
                self.jsonbody_str += a_inputparam.param_type
            self.jsonbody_str += "}"

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
                self.formparams_str += f'"{a_inputparam.param_name}":"{a_inputparam.default_value}"'
            elif 'json_body' == a_inputparam.in_type:
                self.jsonbody_str += "payload = {\n"
                if '$ref' in a_inputparam.param_type:
                    self.jsonbody_str += a_inputparam.param_type
                elif 'properties' in a_inputparam.param_type:
                    for a_param in a_inputparam.param_type['properties']:
                        self.jsonbody_str += f'"{a_param}" : "{a_inputparam.param_type['properties'][a_param]}"\n'
                self.jsonbody_str += "}"

    @abstractmethod
    def analyze_testcases(self,api_info:ApiInfo):
        pass

    def copy_pre_tcinfo(self, tc_info:ApiTCInfo):
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


        