#-*- coding: utf-8 -*-
import os, sys, io
import pytest
import json, time
import openapi_tcgenerator

def test_main(get_dirpath, get_projectpath):
    input_swagger_json_path = get_dirpath+"/test_resource/chatexaone_swagger_openapi.json"
    output_testcode_path = get_projectpath+"/test_result"
    template_path=get_projectpath+"/resources"
    openapi_tcgenerator.swagger_base_testcodegenerator(input_path=input_swagger_json_path, output_path=output_testcode_path, output_type="pytest",template_path=template_path)
    print("end")

