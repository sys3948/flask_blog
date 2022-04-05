# 게시글 작성 시 파일을 생성하는 부분과 프로필 수정에서 프로필 이미지 수정에 대한 파일 이름 변경 기능이 있는 모듈

from flask import abort, current_app, flash, session
from datetime import date
import os

# 프로필 이미지 file 저장시에 해당 file의 이름을 문제없이 저장하기 위해 변경해주는 함수
def change_filename(name):
    if ' ' in name:
        name = name.replace(' ', '_')
    return name


# 게시글 파일을 생성하는 함수
def create_file(content):
    try:
        # html 파일 이름을 년/월/일-n 으로 만드는 로직
        filename = ''.join(date.today().isoformat().split('-'))
        filename = filename + '.html'
        path = current_app.config['UPLOAD_POST_PATH_DEFAULT'] + current_app.config['UPLOAD_POST_PATH'] + str(session['id'])# 파일을 저장할 file path
        dbPath = current_app.config['UPLOAD_POST_PATH'] + str(session['id'])# DB에 저장할 file path

        # 파일의 중복확인을 하기위한 반복문
        i = 1
        while os.path.exists(os.path.join(path, filename)):
            # 파일 이름이 존재한다면 n을 1씩 증가하기.
            name, extension = os.path.splitext(filename)
            if i>1:
                filename = filename.replace('-'+str(num), '-'+str(i))
            else:
                filename = name + '-' + str(i) + extension
            num = i
            i = i + 1

        # 중복확인이 되었으면 생성된 파일이름으로 작성한 글을 작성하기.
        f = open(os.path.join(path, filename), 'wt', encoding='utf-8')
        f.write(content)
        f.close()
        filePath = os.path.join(dbPath, filename)
        return filePath

    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)