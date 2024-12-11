
#-*- coding: utf-8 -*-
import os,sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import json
# from test_utils import api_test_util as api_util

@pytest.fixture(scope='session')
def get_dirpath():
    """ get "tests" directory's absolute path 
    """
    dirname = os.path.dirname(os.path.abspath(__file__))
    return dirname

@pytest.fixture(scope='session')
def get_externalpath():
    """ get external parent folder path to access externally saved big large dicom sample files
    """
    external_parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return external_parent_path

@pytest.fixture(scope='session')
def get_projectpath():
    """ get external parent folder path to access externally saved big large dicom sample files
    """
    external_parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return external_parent_path

