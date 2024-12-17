import collections
from api_info import ApiInfo

class ApiTCInfo(ApiInfo):
    project_str:str #관련 라이브러리 import에서 쓰이는 문자열입니다
    testfile_declaration:str    #테스트 파일 상단 주석 설명에 사용됩니다
    test_pytestmarker_str:str #각 테스트함수 위에 pytest.mark ~ 문장을 생성합니다
    test_declartion_str:str #각 테스트함수 이름을 정의하는 문장입니다
    testmethod_declaration:str  #각 테스트 함수(케이스) 주석 설명에 사용됩니다
    header_str:str  #테스트 상단 헤더 content-type 등 설정에 사용되는 라인입니다

    path_params_set_str:str #상단 path parameter를 세팅하는 라인입니다
    path_params_str:str #상단 path parameter를 세팅하는 라인입니다
    query_params_str:str    #상단 params={}을 채우는데 사용되는 문자열입니다

    formparms_str:str
    multipart_file_str:str

    request_str:str #테스트 실행 문구를 구성합니다
    jsonbody_str:str    #post,put 등에서 json 요청 바디를 표시하는 문자열입니다
    assert_str_list:str #테스트 assertion 을 출력하는데 사용되는 리스트입니다

    def __init__(self, api_info=None):
        self.project_str = ""
        self.testfile_declaration = ""
        self.test_pytestmarker_str = ""
        self.test_declartion_str = ""
        self.test_declartion_str = ""
        self.testmethod_declaration = ""
        self.header_str = ""
        self.path_params_set_str = ""
        self.path_params_str = ""
        self.query_params_str = ""
        self.formparms_str = ""
        self.multipart_file_str = ""
        self.request_str = ""
        self.jsonbody_str = ""
        self.assert_str_list = ""
        if api_info != None:
            self.name = api_info.method+"_"+api_info.name
            self.base_url = api_info.base_url
            self.operation_id = api_info.operation_id
            self.path = api_info.path
            self.method = api_info.method
            self.description = api_info.description
            self.summary = api_info.summary
