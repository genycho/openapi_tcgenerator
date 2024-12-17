import collections 
# from dataclasses import dataclass

class InputParameterInfo:
    """
    "in": v3_a_param['in'],"name": v3_a_param['name'],
    "description":v3_a_param.get('description'), "required":v3_a_param.get('required'), "type":v3_a_param.get('schema').get('type')})
    """
    in_type = None
    param_name = None
    param_type = None
    description = None
    required = False
    default_value = None

    def __init__(self, in_type=None, param_name=None, param_type=None, description=None, required=None):
        self.in_type = in_type
        self.param_name = param_name
        self.param_type = param_type
        self.description = description
        self.required = required


class ApiInfo:
    project_title = ""  # 필수
    base_url = ""   # 필수
    base_path = ""
    name = ""   # 필수
    operation_id = ""   # 필수
    summary = "" # 필수
    description = ""
    path = ""   # 필수
    method = "" # 필수
    tag = []
    input_content_type = ""   #필수 #input content types
    output_content_type = ""   #output content types
    parameters : list[InputParameterInfo]=[] 
    requestBody = {}
    #  파일인 경우, 
    # "requestBody": {
    #                 "content": {
    #                     "application/octet-stream": {
    #                         "schema": {
    #                             "type": "string",
    #                             "format": "binary"
    #                         }
    #                     }
    #                 }
    #             },
    responses = []
    security = ""
    # security_definitions = ""   #커스텀? None(인증 헤더 필요없음) / auth_header (Bearer 토큰) / 그 외에.. 
    # def get_apiinfo_v2(self, project_title, base_url, api_path, api_mehotd, apiinfo_json):
    #     self.project_title = project_title
    #     self.base_url = base_url
    #     self.path = api_path
    #     self.method = api_mehotd
    #     self.name = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") else apiinfo_json.get("summary")
    #     self.operation_id = apiinfo_json.get("operationId")
    #     self.description = apiinfo_json.get("description")
    #     self.summary = apiinfo_json.get("summary")
    #     self.tag = apiinfo_json.get("tags")[0] if apiinfo_json.get("tags") and len(apiinfo_json.get("tags"))>0 else None
    #     self.consumes = apiinfo_json.get("consumes")
    #     self.produces = apiinfo_json.get("produces")
    #     self.parameters = apiinfo_json.get("parameters")
    #     # "parameters": [
    #     #             {
    #     #                 "in": "body",
    #     #                 "name": "body",
    #     #                 "description": "Pet object that needs to be added to the store",
    #     #                 "required": true,
    #     #                 "schema": {
    #     #                     "$ref": "#/definitions/Pet"
    #     #                 }
    #     #             }
    #     #         ],
    #     self.responses = apiinfo_json.get("responses")
    #     self.security = apiinfo_json.get("security")


    def __init__(self):
        self.project_title = ""  # 필수
        self.base_url = ""   # 필수
        self.base_path = ""
        self.name = ""   # 필수
        self.operation_id = ""   # 필수
        self.summary = "" # 필수
        self.description = ""
        self.path = ""   # 필수
        self.method = "" # 필수
        self.tag = []
        self.input_content_type = ""   #필수 #input content types
        self.output_content_type = ""   #output content types
        self.parameters = [] 
        self.requestBody = {}
        self.responses = []
        self.security = ""


