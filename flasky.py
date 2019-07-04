# application 실행 스크립트 파일이다.
# 후에 cil 모듈을 이용하여 여러 flask application 실행에 관한 명령을 만들 예정이다.

from app import create_app

app = create_app('default')