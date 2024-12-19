#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from common import common_utils
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
    test_declartion_str:str
    req_content_type:str
    formparms_str:str
    multipart_file_str:str
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
        self.formparms_str=""
        self.multipart_file_str=""
        self.test_declartion_str = ""
        # self.assert_str_list = []
        # self.testmethod_declaration = ""
        
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