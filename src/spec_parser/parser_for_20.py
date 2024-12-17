#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from model.api_info import ApiInfo
from model.api_info import InputParameterInfo
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)



class SwaggerParser20():
    """
    """
    # common project infos:
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
    
    def parse_swagger20_json(self, swagger_json_path)->list:
        spec_schema_version = -1
        with open(swagger_json_path, 'r',encoding='utf8') as json_file:
            all_api_info = json.load(json_file)
            self.spec_schema_version = all_api_info["swagger"]
            self.project_info = all_api_info["info"].get("description")
            self.spec_version = all_api_info["info"].get("version")
            self.project_title = all_api_info["info"].get("title")
            self.project_host = all_api_info.get("host")
            self.project_basepath = all_api_info.get("basePath")
            self.scheme = all_api_info.get("schemes")[0]    # ["https","http"]
            if len(self.project_basepath) < 2:
                self.base_url = f"{self.scheme}://{self.project_host}"
            else:
                self.base_url = f"{self.scheme}://{self.project_host}/{self.project_basepath}"
            for path_key, value in all_api_info['paths'].items():
                for method_key, value in value.items():
                    a_api_info = self._get_a_apiinfo(path_key, method_key, value)
                    self.api_infos.append(a_api_info)
            return self.api_infos
    
    def _get_a_apiinfo(self, path_key, method_key, apiinfo_json):
        a_api_info = ApiInfo()
        a_api_info.project_title = self.project_title
        a_api_info.base_url = self.base_url
        a_api_info.path = path_key
        a_api_info.method = method_key
        a_api_info.name = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") else apiinfo_json.get("summary")
        a_api_info.operation_id = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") != None else path_key.replace("/","").lower()
        a_api_info.description = apiinfo_json.get("description")
        a_api_info.summary = apiinfo_json.get("summary")
        a_api_info.tag = apiinfo_json.get("tags")[0] if apiinfo_json.get("tags") and len(apiinfo_json.get("tags"))>0 else None
        a_api_info.input_content_type = apiinfo_json.get("consumes")
        # if apiinfo_json.get("parameters") != None and len(apiinfo_json.get("parameters"))>0:
            
        for v2_a_param in apiinfo_json.get("parameters"):
            if "body" == v2_a_param.get('in'):
                a_api_info.requestBody = _get_requestjson_param(v2_a_param)
            elif "file" == v2_a_param.get('in'):
                a_api_info.requestBody = _get_v2_params(v2_a_param)
            else:
                a_api_info.parameters.append(_get_v2_params(v2_a_param))
            # elif "path" == v2_a_param.get('in'):
            #     a_api_info.parameters.append(_get_v2_params(v2_a_param))
            # elif "query" == v2_a_param.get('in'):
            #     a_api_info.parameters.append(_get_v2_params(v2_a_param))
            # elif "header" == v2_a_param.get('in'):
            #     a_api_info.parameters.append(_get_v2_params(v2_a_param))
            # elif "formData" == v2_a_param.get('in'):
            #     a_api_info.parameters.append(_get_v2_params(v2_a_param))
            
            # else:
            #     #NOT ADD. NOT DEFINED IN TYPE.
            #     logger.warning(f"Not Expected parameter in type definition - {v2_a_param.get('in')}")
        a_api_info.responses = apiinfo_json.get("responses")
        a_api_info.output_content_type = apiinfo_json.get("produces")
        a_api_info.security = apiinfo_json.get("security")
        return a_api_info


def _get_v2_params(json_param_info) ->InputParameterInfo:
    """
    {
        "name": "petId",
        "in": "path",
        "description": "ID of pet to update",
        "required": true,
        "type": "integer",
        "format": "int64"
    },
    {
        "name": "additionalMetadata",
        "in": "formData",
        "description": "Additional data to pass to server",
        "required": false,
        "type": "string"
    },
    {
        "name": "file",
        "in": "formData",
        "description": "file to upload",
        "required": false,
        "type": "file"
    }

    {
        "name": "status",
        "in": "query",
        "description": "Status values that need to be considered for filter",
        "required": true,
        "type": "array",
        "items": {
            "type": "string",
            "enum": [
                "available",
                "pending",
                "sold"
            ],
            "default": "available"
        },
        "collectionFormat": "multi"
    }
    {
        "name": "api_key",
        "in": "header",
        "required": false,
        "type": "string"
    },
    """
    a_paraminfo = InputParameterInfo()
    a_paraminfo.description = json_param_info.get('description')
    a_paraminfo.in_type = json_param_info.get('in')
    a_paraminfo.param_name = json_param_info.get('name')
    a_paraminfo.required = json_param_info.get('required')
    if json_param_info.get('in') == "body":
        a_paraminfo.param_type = json_param_info.get('schema')
        a_paraminfo.default_value = json_param_info.get('schema')
    else:
        a_paraminfo.param_type = json_param_info.get('type')
        a_paraminfo.default_value = json_param_info.get('type')
    return a_paraminfo

def _get_requestjson_param(json_param_info)->InputParameterInfo:
    """
    {
        "in": "body",
        "name": "body",
        "description": "Pet object that needs to be added to the store",
        "required": true,
        "schema": {
            "$ref": "#/definitions/Pet"
        }
    }
    """
    a_paraminfo = InputParameterInfo()
    a_paraminfo.description = json_param_info.get('description')
    a_paraminfo.in_type = 'json_body'
    a_paraminfo.param_name = json_param_info.get('name') if json_param_info.get('name') else "json_body"
    a_paraminfo.required = json_param_info.get('required')
    if json_param_info.get('in') == "body":
        a_paraminfo.param_type = json_param_info.get('schema')
        a_paraminfo.default_value = json_param_info.get('schema')
    return a_paraminfo
        