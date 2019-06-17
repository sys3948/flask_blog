# application factory function이 작성되어있는 파일로 
# 해당 application에 지원하는 Object들을 instance를 담당하는 파일이다.

from flask import Flask
import pymysql as mysql
from config import config
# import logging은 해당 모듈에 대해 자세히 이해를 한 후에 이용하도록 한다.

# instance 하는 Flask 확장 or 다른 모듈들

db = mysql.connect(host ='192.168.111.139',
                   port = 3306,
                   user = 'sys3948',
                   passwd = 'Tlsdbstjr1+',
                   db = 'FlaskyDB2_test',
                   charset = 'utf8')

cur = db.cursor()
cur.execute('select count(id) from posts')
all_count = cur.fetchone()
cur.close()
all_count = all_count[0]

def create_app(config_name):
    # instance한 객체들을 초기화 하고 Blueprint를 등록하는 부분
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app