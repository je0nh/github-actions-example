# pylint: disable=C0301
# pylint: disable=C0303
# pylint: disable=C0114
# pylint: disable=R1710

import time
from datetime import datetime
import requests
from fake_useragent import UserAgent

class Fconline:
    """
    nexon API를 사용해 FConline 유저 데이터를 가져옵니다
    """
    def __init__(self, api_key):
        self.api_key = api_key

    def call(self, url):
        '''
        Args:
            url (str): '/fconline/v1/id?nickname=nickname' (https://openapi.nexon.com/guide/request-api/)
        '''
        # 오류 메세지
        error_message = ['OPENAPI00003', 'OPENAPI00005', 'OPENAPI00006', 'OPENAPI00009']
        # nexon api url & headers
        url_string = f'https://open.api.nexon.com{url}'
        ua = UserAgent()
        headers = {
            "User-Agent" : ua.random,
            "x-nxopen-api-key": self.api_key
            }
        # 조건에 맞을 때 까지 반복
        while True:
            # API 요청
            try:
                response = requests.get(url_string, headers=headers, timeout=10)
            except requests.Timeout:
                print("Timeout error")
            error_code = None

            try:
                # API 요청 시 error가 발생하면 error의 'name' 값 가져오기
                error_code = response.json().get('error').get('name')
            except (AttributeError, ValueError):
                pass

            # error 코드가 400이고 에러 이름이 error_message 있으면 API 호출 종료
            if response.status_code == 400 and error_code in error_message:
                now = datetime.now()
                cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
                if error_code == 'OPENAPI00003':
                    print(cur_time, '유효하지 않은 식별자')
                elif error_code == 'OPENAPI00005':
                    print(cur_time, '유효하지 않은 API KEY')
                elif error_code == 'OPENAPI00006':
                    print(cur_time, '유효하지 않은 게임 또는 API PATH')
                elif error_code == 'OPENAPI00009':
                    print(cur_time, '데이터 준비 중')
                break

            # error 코드가 200이면 데이터 적재
            if response.status_code == 200:
                data = response.json()
                return data

            # error 코드가 429이면 잠시 기다렸다가 API 다시 호출
            if response.status_code == 429:
                now = datetime.now()
                cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
                print(cur_time, 'Too Many Requests')
                time.sleep(10)

            # error 코드가 400이고 유저의 이름 변경으로 인해 파라미터가 누락되었다고 나오면 null값을 append
            if response.status_code == 400:
                now = datetime.now()
                cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
                error_code = response.json().get('error').get('name')
                if error_code == 'OPENAPI00004':
                    data = response.json()
                    print(cur_time, '파라미터 누락 또는 유효하지 않음')
                    return data

    def ouid(self, nickname) -> str:
        """
        Args:
            nickname (str): 

        Returns:
            str: _description_
        """
        url = f'/fconline/v1/id?nickname={nickname}'
        _ouid = self.call(url)
        return _ouid.get('ouid')

    def match_id(self, ouid, matchtype=50, offset=0, limit=100) -> list:
        '''
        Args:
            matchtype (int): 기본 변수 50
            
            offset (int): 기본 변수 0
            
            limit (int): 기본 변수 100
        
        Returns:
            list: match_id가 정해진 limit 숫자에 맞게 출력 (https://openapi.nexon.com/game/fconline/?id=15)
        '''
        url = f'/fconline/v1/user/match?ouid={ouid}&matchtype={matchtype}&offset={offset}&limit={limit}'
        return self.call(url=url)

    def match_detail(self, match_id) -> dict:
        """
        Args:
            match_id (str)

        Returns:
            dict: 해당 경기의 정보 (https://openapi.nexon.com/game/fconline/?id=16)
        """
        url = f'/fconline/v1/match-detail?matchid={match_id}'
        return self.call(url)
    
