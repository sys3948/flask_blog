# config.py는 application의 설정값이 지정되어있는 파일이며 
# 개발, 테스트, 배포 작업에 필요한 설정값이 있는 파일이다.

class Config:
    # 개발, 테스트, 배포 작업에 공통되는 설정값이 지정되어있는 class이다.
    SECRET_KEY = 'secret key in flasky example'
    EXTENTION_FILES = set({'png', 'jpg', 'jpeg', 'gif'})
    UPLOAD_FOLDERS = 'app/static/icon'
    UPLOAD_POST_PATH_DEFAULT = 'app/templates/'
    UPLOAD_POST_PATH = 'postFiles/'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # 개발 작업에 필요한 설정값이 지정되어있는 class이다.
    # 추후 추가가될 것이다.
    SQLALCHEMY_DATABASE_URI = 'mysql+driver(ex:pymysql)://user:password@ip/database schema?charset=utf8'
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    # 테스트 작업에 필요한 설정값이 지정되어있는 class이다.
    # 추후 추가가될 것이다.
    pass


class ProductionConfig(Config):
    # 배포 작업에 필요한 설정값이 지정되어있는 class이다.
    # 추후 추가가될 것이다.
    pass


# app 실행시 어느 환경으로 실행할 것인가를 선택하기 위한 딕셔너리.
# 이 딕셔너리를 통해 위의 설정 class를 선택한다.
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'product': ProductionConfig,
    'default': DevelopmentConfig
}