import collections 
# from dataclasses import dataclass

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
    consumes = ""   #필수 #input content types
    produces = ""   #output content types
    parameters = [] 
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
    security_definitions = ""   #커스텀? None(인증 헤더 필요없음) / auth_header (Bearer 토큰) / 그 외에.. 

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


    # def get_apiinfo_v3(self, project_title, base_url, api_path, api_mehotd, apiinfo_json):
    #     self.project_title = project_title
    #     self.base_url = base_url
    #     self.path = api_path
    #     self.method = api_mehotd
    #     self.name = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") else apiinfo_json.get("summary")
    #     self.operation_id = apiinfo_json.get("operationId") if apiinfo_json.get("operationId") != None else api_path.replace("/","").lower()
    #     self.description = apiinfo_json.get("description")
    #     self.summary = apiinfo_json.get("summary")
    #     self.tag = apiinfo_json.get("tags")[0] if apiinfo_json.get("tags") and len(apiinfo_json.get("tags"))>0 else None
    #     if apiinfo_json.get("parameters") != None and len(apiinfo_json.get("parameters"))>0:
    #         for v3_a_param in apiinfo_json.get("parameters"):
    #             if v3_a_param.get('schema').get('type') == None:
    #                 print("here")
    #             self.parameters.append({"in": v3_a_param['in'],"name": v3_a_param['name'],"description":v3_a_param.get('description'), "required":v3_a_param.get('required'), "type":v3_a_param.get('schema').get('type')})
    #     # self.consumes = apiinfo_json.get("consumes")
    #     if apiinfo_json.get("requestBody") != None and apiinfo_json.get("requestBody").get("content") != None and len(apiinfo_json.get("requestBody").get("content").keys())>0:
    #         self.consumes = list(apiinfo_json.get("requestBody").get("content").keys())
    #         self.parameters.append({"in": "body","name": "body","schema":list(apiinfo_json.get("requestBody").get("content").values())[0]['schema']})
    #     self.produces = apiinfo_json.get("produces")
    #     self.responses = apiinfo_json.get("responses")
    #     self.security = apiinfo_json.get("security")
