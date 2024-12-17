#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from common import qe_utils
from model.api_info import ApiInfo
from model.api_tc_info import ApiTCInfo
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

class BasicTCAnalyzer():
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
    testmethod_declaration:str
    req_content_type:str
    formparms_str:str
    multipart_file_str:str

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

    def get_commoninfo(self,api_info:ApiInfo):
        """ 각 TC에서 공통으로 설정된 정보를 미리 Analyzer에 세팅 - req_content_type, header_str, project_str
        """
        # 0) 공통으로 적용할 항목 
        # self.req_content_type = qe_utils.get_request_type(api_info, 2)
        if api_info.input_content_type != None and len(api_info.input_content_type) > 0:
            self.header_str = f'"Content-Type": "{api_info.input_content_type[0]}"'
        self.project_str = api_info.project_title.lower().replace(" ","")
        # self.header_str = f'"Content-Type": "{api_info.consumes[0]}"' if api_info.consumes != None and len(api_info.consumes)>0 else ""

    def set_commoninfo(self, tc_info:ApiTCInfo):
        tc_info.project_str = self.project_str
        tc_info.test_declartion_str = self.test_declartion_str
        tc_info.testmethod_declaration = self.testmethod_declaration
        tc_info.header_str = self.header_str
        tc_info.path_params_str = self.path_params_str
        tc_info.path_params_set_str = self.path_params_set_str
        tc_info.query_params_str = self.query_params_required_str
        tc_info.request_str=self.request_str
        tc_info.assert_str_list=self.assert_str_list