#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import uuid
import datetime
from datetime import datetime as dt
import requests
from common.exceptions import QEToolException
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
import logging
from common.log_config import setup_logging


def get_params_info(api_info:ApiInfo, project_str:str)->dict:
    result_dict = {}
    query_reqparam_count = 0
    query_optparam_count = 0
    query_params_required_str = ""
    query_params_all_str =""
    path_params_set_str = ""
    path_params_str = ""
    path_params_notexist_str = ""

    for a_inputparam in api_info.parameters:
        a_inputparam : InputParameterInfo
        # 쿼리 파라미터 체크
        if 'query' == a_inputparam.in_type:
            p_type = a_inputparam.param_type
            if True == a_inputparam.required:
                if query_reqparam_count >0:
                    query_params_required_str+=',\n        '
                    query_params_all_str+=',\n        '
                query_params_required_str+=f'"{a_inputparam.param_name}":"{p_type}"'
                query_params_all_str+=f'"{a_inputparam.param_name}":"{p_type}"'
                query_reqparam_count+=1
            else:
                if query_reqparam_count+query_optparam_count > 0:
                    query_params_all_str+=',\n        '
                query_params_all_str+=f'"{a_inputparam.param_name}":"{p_type}"'
                query_optparam_count +=1
        # path 파라미터 체크
        elif 'path' == a_inputparam.in_type:
            p_type = a_inputparam.param_type
            path_params_set_str=(f'test_{a_inputparam.param_name} = {project_str}_util.get{a_inputparam.param_name}()')
            path_params_str = f'.format({a_inputparam.param_name}=test_{a_inputparam.param_name})'
            if p_type == "integer":
                path_params_notexist_str=(f'test_{a_inputparam.param_name} = 999999')
            else:
                path_params_notexist_str=(f'test_{a_inputparam.param_name} = "not_exist_id"')
        elif 'header' == a_inputparam.in_type:
            header_str += f'"{a_inputparam.param_name}":"{a_inputparam.default_value}"'
        elif 'formData' == a_inputparam.in_type:
            pass    # GET에서 formData로 전달되는 경우는 없을 것으로 보임 
        result_dict.update({"query_params_required_str":query_params_required_str})
        result_dict.update({"query_params_all_str":query_params_all_str})
        result_dict.update({"path_params_set_str":path_params_set_str})
        result_dict.update({"path_params_str":path_params_str})
        result_dict.update({"path_params_notexist_str":path_params_notexist_str})
        # query_params_required_str = ""
        # query_params_all_str =""
        # path_params_set_str = ""
        # path_params_str = ""
        # path_params_notexist_str = ""
