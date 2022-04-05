# application factory function이 작성되어있는 파일로 
# 해당 application에 지원하는 Object들을 instance를 담당하는 파일이다.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import config
# import logging은 해당 모듈에 대해 자세히 이해를 한 후에 이용하도록 한다.

# instance 하는 Flask 확장 or 다른 모듈들

db = SQLAlchemy()
socketio = SocketIO()


def create_app(config_name):
    # instance한 객체들을 초기화 하고 Blueprint를 등록하는 부분
    app = Flask(__name__)
    db.init_app(app)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .main import main as main_blueprint, errors as errors_handler
    app.register_blueprint(main_blueprint)
    # 팩토리 함수에서 에러 핸들링 패턴.
    app.register_error_handler(404, errors_handler.not_found)
    app.register_error_handler(403, errors_handler.forbidden)
    app.register_error_handler(500, errors_handler.internal_server)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint)
    socketio.init_app(app)

    return app