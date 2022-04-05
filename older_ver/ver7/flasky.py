# application 실행 스크립트 파일이다.
# 후에 cil 모듈을 이용하여 여러 flask application 실행에 관한 명령을 만들 예정이다.
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Follow, Post, Comment

app = create_app('default')
manager = Manager(app)

@app.shell_context_processor
def make_shell_context():
    return dict(app = app, db = db, User = User, Follow = Follow, Post = Post, Comment = Comment)