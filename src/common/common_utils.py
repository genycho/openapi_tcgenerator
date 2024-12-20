#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import uuid
import datetime
from datetime import datetime as dt
import requests
from common.exceptions import QEToolException
# from model.api_info import ApiInfo
# from model.api_info import InputParameterInfo
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

def get_spec_schema_version(swagger_json_path)->str:
    with open(swagger_json_path, 'r',encoding='utf8') as json_file:
        all_api_info = json.load(json_file)
    if "swagger" in all_api_info and "2.0" == all_api_info.get('swagger'):
        logger.info("swagger appeared. 2.0")
        return "2.0"
    elif "openapi" in all_api_info:
        detail_spec_version = all_api_info["openapi"]
        logger.info(f"openapi appeared. 3.0 and {detail_spec_version}")
        return "3.0"
    
########### COMMON ###########
def get_uuid():
    return str(uuid.uuid4())

def check_contains(to_check_dict, key_value, check_value):
    for this_item in to_check_dict:
        if check_value == this_item.get(key_value):
            return True
    return False
        

############### FILE ################
def open_json_file(filepath):
    with open(filepath) as json_file:
        _json_body = json.load(json_file)
        json_file.close()
    return _json_body

def get_file_binary(filepath):
    with open(filepath, 'rb') as f:
        # sample = bytearray(f.read())
        result = f.read()
        f.close()
    return result

def write_file_text(filepath, text_data):
    with open(filepath, "w") as f:
        f.write(text_data)
        print("file write succeded")
        f.close()
    return True

def write_file_binary(filepath, binary_data):
    with open(filepath, "wb") as f:
        f.write(bytes(binary_data))
        # f.write(binary_data)
        print("file write succeded")
        f.close()
    return True

############### DATETIME ################
def _get_curdatetime_wformat(format):
    gen_value = dt.now().strftime(format)
    return gen_value

def get_curdate():
    return _get_curdatetime_wformat('%Y%m%d')    

def get_curdatetime():
    # return _get_curdatetime_wformat('%Y%m%d_%H%M%S%f')
    return _get_curdatetime_wformat('%Y%m%d_%H%M%S')

def get_curdatetime_millisec():
    # return _get_curdatetime_wformat('%Y%m%d_%H%M%S%f')
    return _get_curdatetime_wformat('%Y%m%d%H%M%S%f')

############### API Spec ################
def get_request_type(api_info):
    return get_request_type(api_info, 2)

def get_request_type(api_info, spec_version):
    """ "swagger": "2.0", "openapi": "3.1.0","openapi": "3.0.0","openapi": "3.0.2",
    """
    if 2 == spec_version:
        if api_info.consumes != None and len(api_info.consumes)>0:
            return api_info.consumes[0]
        else: 
            return ""
    elif 3 == spec_version:
        # if api_info.requestBody != None and api_info.requestBody.content!=None:
        if api_info.consumes != None and len(api_info.consumes)>0:
            if 'application/json' in api_info.consumes:
                return 'application/json'
            else:
                return api_info.consumes[0]
        else:
            return ""


