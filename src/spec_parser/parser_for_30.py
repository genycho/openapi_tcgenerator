#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
# from swagger_parser import SwaggerParser
from common.exceptions import QEToolException
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)

def _get_requestjson_param(json_info):
        """
        # "requestBody": {
        #         "description": "Create a new pet in the store",
        #         "content": {
        #             "application/json": {
        #                 "schema": {
        #                     "$ref": "#/components/schemas/Pet"
        #                 }
        #             },
        #         "required": true
        #     },
        #######################
        # "requestBody": {
        #         "required": true,
        #         "content": {
        #             "application/json": {
        #                 "schema": {
        #                     "type": "object",
        #                     "properties": {
        #                         "name": {
        #                             "type": "string",
        #                             "example": "my_key"
        #                         }
        #                     }
        #                 }
        #             }
        #         }
        #     },
        """
        a_param = InputParameterInfo()
        a_param.in_type='json_body'
        a_param.description=json_info.get('description')
        a_param.required=json_info.get('required')
        a_param.param_name='json_body'
        a_param.param_type=json_info.get('content').get('application/json').get("schema")
        return a_param

class SwaggerParser30():
    """
        https://petstore.swagger.io/ - Base URL: petstore.swagger.io/v2
        https://petstore3.swagger.io/ - 
    """
    # common(Project) infos:
    spec_schema_version = None
    project_title = None
    project_info = None
    project_host = None
    base_url = None
    project_basepath = None
    scheme = None
    api_infos = []
    
    def __init__(self):
        spec_schema_version = None
        project_title = None
        project_info = None
        project_host = None
        base_url = None
        project_basepath = None
        scheme = None
        api_infos = []
    
    def parse_30swagger_json(self, swagger_json_path)->list:
        spec_schema_version = -1
        with open(swagger_json_path, 'r',encoding='utf8') as json_file:
            all_api_info = json.load(json_file)
            self.project_info
            self.spec_schema_version = all_api_info["openapi"]
            self.project_info = all_api_info["info"].get("description")
            self.spec_version = all_api_info["info"].get("version")
            self.project_title = all_api_info["info"].get("title")
            self.project_host = all_api_info.get("servers")[0].get('url') if all_api_info.get("servers") and len(all_api_info.get("servers"))>0 and all_api_info.get("servers")[0].get('url') else "" #{'url': '/api/v3'}
            self.project_basepath = all_api_info.get("servers")[0] if all_api_info.get("servers") and len(all_api_info.get("servers"))>0 else "" #{'url': '/api/v3'}
            self.scheme = None
            for path_key, value in all_api_info['paths'].items():
                for method_key, value in value.items():
                    a_api_info = self._get_a_apiinfo(path_key, method_key, value)
                    self.api_infos.append(a_api_info)
            return self.api_infos
    
    def _get_a_apiinfo(self, path_key, method_key, apiinfo_json):
        a_api_info = ApiInfo()
        a_api_info.project_title = self.project_title
        a_api_info.base_url = self.project_host
        a_api_info.path = path_key
        a_api_info.method = method_key
        a_api_info.name = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") else apiinfo_json.get("summary")
        a_api_info.operation_id = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") != None else path_key.replace("/","").lower()
        a_api_info.description = apiinfo_json.get("description")
        a_api_info.summary = apiinfo_json.get("summary")
        a_api_info.tag = apiinfo_json.get("tags")[0] if apiinfo_json.get("tags") and len(apiinfo_json.get("tags"))>0 else None
        if apiinfo_json.get("parameters") != None and len(apiinfo_json.get("parameters"))>0:
            a_api_info.input_content_type = ""  #2.0의 경우 따로 정의되어 있음. # self.consumes = apiinfo_json.get("consumes")
            for v3_a_param in apiinfo_json.get("parameters"):
                if v3_a_param.get('schema').get('type') == None:
                    logger.warning("Not expected schema. there is no parameter schema type!!!")
                a_api_info.parameters.append(InputParameterInfo(in_type=v3_a_param['in'], param_name=v3_a_param['name'], description=v3_a_param.get('description'), required=v3_a_param.get('required'), param_type=v3_a_param.get('schema').get('type')))
        if apiinfo_json.get("requestBody") != None and apiinfo_json.get("requestBody").get("content") != None and len(apiinfo_json.get("requestBody").get("content").keys())>0:
            a_api_info.input_content_type = list(apiinfo_json.get("requestBody").get("content").keys())
            if "application/json" in apiinfo_json['requestBody']['content']:
                a_api_info.parameters.append(_get_requestjson_param(apiinfo_json.get("requestBody")))
            elif "application/json" in apiinfo_json['requestBody']['content']:
                pass
            else:
                # TODO 파일 바디 
                pass
        a_api_info.responses = apiinfo_json.get("responses")
        if apiinfo_json.get('responses') :
            # TO DEBUG
            first_response_code = next(iter(apiinfo_json.get('responses')))
            try:
                a_api_info.output_content_type = next(iter(apiinfo_json['responses'][first_response_code].get('content')))
            except:
                logger.info(f"There is no output content type declaration - {first_response_code}")
                a_api_info.output_content_type = None
        a_api_info.security = apiinfo_json.get("security")
        return a_api_info
    
    
        

        


