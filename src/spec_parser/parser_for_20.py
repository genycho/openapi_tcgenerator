#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
# from swagger_parser import SwaggerParser
from common.exceptions import QEToolException
from apitest_generator.model.api_info import ApiInfo

def parse_swagger_json(swagger_json_path):
    """
    https://petstore.swagger.io/ - Base URL: petstore.swagger.io/v2
    https://petstore3.swagger.io/ - 
    """
    # parser = SwaggerParser(swagger_path=swagger_json_path)  # 3.0은 전혀 지원되지 않아 (마지막 업데이트가 2020년), 제거하고 일단 바로 json 파싱으로. 
    #   all_api_info = parser.specification
    spec_schema_version = -1
    api_infos = []
    with open(swagger_json_path, 'r',encoding='utf8') as json_file:
        all_api_info = json.load(json_file)
    if "swagger" in all_api_info and "2.0" == all_api_info.get('swagger'):
        # TODO 별도 내부 함수로 분리, 
        project_info = all_api_info["info"].get("description")
        spec_schema_version = all_api_info["swagger"]
        # spec_version = all_api_info["info"].get("version")
        project_title = all_api_info["info"].get("title")
        # project_termsofservice = all_api_info["info"].get("termsOfService")
        project_host = all_api_info.get("host")
        project_basepath = all_api_info.get("basePath")
        scheme = all_api_info.get("schemes")[0]
        if len(project_basepath) < 2:
            base_url = f"{scheme}://{project_host}"
        else:
            base_url = f"{scheme}://{project_host}/{project_basepath}"
        for path_key, value in all_api_info['paths'].items():
            for method_key, value in value.items():
                a_api_info = ApiInfo()
                a_api_info.get_apiinfo_v2(project_title, base_url, path_key, method_key, value)
                api_infos.append(a_api_info)
        # return api_infos
    elif "openapi" in all_api_info:
        spec_schema_version = all_api_info["openapi"]
        project_info = all_api_info["info"].get("description")
        spec_version = all_api_info["info"].get("version")
        project_title = all_api_info["info"].get("title")
        # project_termsofservice = all_api_info["info"].get("termsOfService")
        project_host = None
        project_basepath = all_api_info.get("servers")[0] if all_api_info.get("servers") and len(all_api_info.get("servers"))>0 else "" #{'url': '/api/v3'}
        scheme = None
        api_infos = []
        for path_key, value in all_api_info['paths'].items():
            for method_key, value in value.items():
                a_api_info = ApiInfo()
                # if spec_schema_version == "3.0.0":
                a_api_info.get_apiinfo_v3(project_title, project_basepath, path_key, method_key, value)
                api_infos.append(a_api_info)
        # return api_infos
    else:
        raise QEToolException("Not yet supported API Spec json schema!!")
    return api_infos, spec_schema_version

