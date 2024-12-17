#-*- coding: utf-8 -*-
import os, sys, io
from os import path
from common import common_utils
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from common.exceptions import QEToolException

def code_generate(template_path, template_filename, output_path, tc_list):
    """
    https://documentation.bloomreach.com/engagement/docs/datastructures
    """
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_filename) 
    output = template.render(tc_list=tc_list)
    # Write the output to a file
    if len(tc_list) ==0:
        raise QEToolException("There is no tc data to generate!!")
    first_tc = tc_list[0]
    file_name = first_tc.name.lower()
    output_fullpath = output_path + f"/test_{file_name}.py"
    if path.exists(output_fullpath):
        output_fullpath = output_path + f"/test_{file_name}_{common_utils.get_curdatetime()}.py"
    with open(output_fullpath, 'wb') as f:
    # with open(output_fullpath, 'w') as f:
        f.write(output.encode("utf-8"))
    return output_fullpath