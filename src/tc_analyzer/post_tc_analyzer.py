#-*- coding: utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from common.exceptions import QEToolException
from common import qe_utils
from model.api_info import ApiInfo
from model.api_tc_info import ApiTCInfo
import logging
from common.log_config import setup_logging

logger = logging.getLogger()
setup_logging()
logger = logging.getLogger(__name__)