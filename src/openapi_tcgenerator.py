#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Set, Dict, Tuple, Optional
from common import common_utils as api_utils
from common.exceptions import QEToolException
from common import tc_generator_constants as constants
from spec_parser.parser_for_20 import SwaggerParser20
from spec_parser.parser_for_30 import SwaggerParser30
from model.api_info import ApiInfo
from model.api_tc_info import ApiTCInfo
from tc_analyzer.get_tc_analyzer import GetTypeTCAnalyzer
from tc_analyzer.post_tc_analyzer import PostJsonBodyTypeTCAnalyzer
from tc_analyzer.post_tc_analyzer import PostMultipartTypeTCAnalyzer
from tc_analyzer.put_tc_analyzer import PutJsonBodyTypeTCAnalyzer
from tc_analyzer.delete_tc_analyzer import DeleteTypeTCAnalyzer
from code_generator import pytest_generator

OUTPUT_PYTEST = "pytest"
OUTPUT_POSTMAN = "postman"

def swagger_base_testcodegenerator(input_path, output_path, output_type, template_path):
    # swagger_spec_version = 3
    default_template_path = "../resource"
    
    ## Spec parsing
    swagger_spec_version = api_utils.get_spec_schema_version(input_path)
    apiinfo_list:List[ApiInfo] = []
    if "3.0" == swagger_spec_version:
        parser = SwaggerParser30()
    elif "2.0" == swagger_spec_version:
        parser = SwaggerParser20()
    else:
        raise QEToolException(f"Not defined spec version - {swagger_spec_version}")
    apiinfo_list = parser.parse_30swagger_json(input_path)

    ## Test analyzing
    get_tc_analyzer = GetTypeTCAnalyzer()
    post_json_tc_analyzer = PostJsonBodyTypeTCAnalyzer()
    post_multipart_tc_analyzer = PostMultipartTypeTCAnalyzer()
    put_json_tc_analyzer = PutJsonBodyTypeTCAnalyzer()
    delete_tc_analyzer = DeleteTypeTCAnalyzer()

    for a_apiinfo in apiinfo_list:
        tc_list:List[ApiTCInfo] = []
        if "get" == a_apiinfo.method:
            get_tc_analyzer.reset()
            template_filename = constants.GET_METHOD_TEMPLATEFILENAME
            tc_list = get_tc_analyzer.analyze_testcases(a_apiinfo)
        elif "post" == a_apiinfo.method:
            if ApiInfo.CONTENTTYPE_JSON == a_apiinfo.requestBody or ApiInfo.CONTENTTYPE_JSON == a_apiinfo.input_content_type:
                post_json_tc_analyzer.reset()
                template_filename = constants.POST_JSONBODY_TEMPLATEFILENAME
                tc_list = post_json_tc_analyzer.analyze_testcases(a_apiinfo)
            elif ApiInfo.CONTENTTYPE_MULTIPART == a_apiinfo.requestBody or ApiInfo.CONTENTTYPE_MULTIPART == a_apiinfo.input_content_type:
                post_multipart_tc_analyzer.reset()
                template_filename = constants.POST_MULTIPART_TEMPLATEFILENAME
                tc_list = post_multipart_tc_analyzer.analyze_testcases(a_apiinfo)
        elif "put" == a_apiinfo.method or "patch" == a_apiinfo.method:
            put_json_tc_analyzer.reset()
            template_filename = constants.PUT_JSONBODY_TEMPLATEFILENAME
            tc_list = put_json_tc_analyzer.analyze_testcases(a_apiinfo)
        elif "delete" == a_apiinfo.method:
            delete_tc_analyzer.reset()
            template_filename = constants.DELETE_METHOD_TEMPLATEFILENAME
            tc_list = delete_tc_analyzer.analyze_testcases(a_apiinfo)
        else:
            print(f"not defined method type - {a_apiinfo.method}")
            # raise QEToolException("")
        if "pytest" == output_type:
            pytest_generator.code_generate(template_path=template_path, template_filename=template_filename, tc_list=tc_list,output_path=output_path)
        else:
            pytest_generator.code_generate(template_path=template_path, template_filename=template_filename, tc_list=tc_list,output_path=output_path)

    