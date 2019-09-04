from flask import abort, flash, make_response, redirect, render_template, request, session, url_for
from sqlalchemy.sql.expression import func
from . import auth
from .. import db
from ..models import User
import os


# 로그인 라우트 & 뷰함수
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not 'username' in session and not 'id' in session: # 로그인이 안 되어있는 상태를 확인 하는 조건문
        if request.method == 'POST': # method가 POST인 경우(로그인을 하기위해 로그인 submit 버튼을 클릭 했을 때 발생하는 method)
            email = request.form['email'] # Client에서 입력한 email 값을 저장하는 변수
            password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
            try:
                password_hash = db.session.query(func.sha2(password, 224)) # 입력한 비밀번호 해쉬하기.
                user = User.query.filter_by(email = email, password_hash = password_hash).first()
                if not user:
                    # 워 검색한 user가 존재하지 않을 경우
                    flash('존재하지 않는 아이디이거나 비밀번호가 맞지 않습니다.')
                    return redirect(url_for('.login'))
                session['username'] = user.username
                session['id'] = user.id
            except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except 문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

            flash('로그인을 성공했습니다.')
            return redirect(url_for('main.index', username = session['username']))

        # method가 POST가 아닌 경우(대표 method GET)
        return render_template('login.html')
    else: # 로그인 되어있는 상태에서 로그인 페이지로 들어갈시(강제적으로) 메인 페이지로 리다이렉트 하는 조건문(else 문)
        flash('예상치 못한 문제로 로그아웃 합니다.')
        session.pop('username', None)
        session.pop('id', None)
        return redirect(url_for('.login'))


# 로그 아웃 라우트 & 뷰함수
@auth.route('/logout')
def logout():
    try:
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
            # 조건문이 True이면 아래와 같이 저장된 session을 제거(pop)한 후에 메인 페이지로 리다이렉트 한다.
            session.pop('username', None)
            session.pop('id', None)
            flash('로그아웃 합니다.')
            return redirect(url_for('.login'))
        else: # 로그인이 되지 않는 상태에서 강제적으로 로그아웃으로 들어가면 메인페이지로 리다이렉트 한다.
            flash('로그아웃 되었습니다.')
            return redirect(url_for('.login'))
    except Exception as e: # 예상치 못한 Error가 발생할 시 처리하는 except문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 회원가입 라우트 & 뷰함수
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if  not'username' in session and not 'id' in session: # 로그인이 되어있지 않는 상태를 확인하는 조건문
        if request.method == 'POST': # method가 POST인지 확인하는 조건문
            email = request.form['email'] # Clinet에서 입력한 email 값을 저장하는 변수
            username = request.form['username'] # Clinet에서 입력한 username 값을 저장하는 변수
            password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
            password2 = request.form['password2'] # Client에서 입력한 password 확인 값을 저장하는 변수
            
            # 이메일 닉네임 비밀번호가 존재하지 않는 경우 회원가입 페이지로 리다이렉트 하는 기능.
            if not bool(username.strip()) or not bool(email.strip()) or not bool(password.strip()) or \
               not bool(password2.strip()) or password != password2:
                flash('email or username 작성에서 잘 못 되었거나 비밀번호와 비밀번호 확인이 일치하지 않습니다.')
                return redirect(url_for('.register'))

            # 회원가입 절차.
            selected_email = User.query.filter_by(email = email).first()
            if selected_email:
                flash('존재하는 이메일 입니다.')
                return redirect(url_for('.register'))

            selected_username = User.query.filter_by(username = username).first()
            if selected_username:
                flash('존재하는 닉네임 입니다.')
                return redirect(url_for('.register'))

            # 회원가입하여 users 테이블에 입력한 데이터를 insert하고 해당 id value에 맞게 게시글 작성에 대한 폴더 생성하기.
            password_hash = db.session.query(func.sha2(password, 224))
            user = User(email = email, username = username, password_hash = password_hash)
            db.session.add(user)
            db.session.commit()
            os.mkdir('app/templates/postFiles/' + str(user.id))

            flash('가입완료 됬습니다.')
            return redirect(url_for('.login'))
        # method가 POST가 아닐 경우
        return render_template('register.html')
    else: # 로그인이 되어있는 상태면 저장된 session을 제거(pop)한 후에 메인페이지로 리다이렉트 한다.
        session.pop('username', None)
        session.pop('id', None)
        flash('예상치 못한 문제로 로그아웃 합니다.')
        return redirect(url_for('.login'))


# 비밀번호 초기화하는 라우트 & 뷰함수
@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    if not 'username' in session and not 'id' in session: # 로그인이 되어있지 않는 상태를 확인하는 조건문
        if request.method == 'POST': # method가 POST인지 확인하는 조건문
            email = request.form['email'] # Client에서 입력한 값을 저장하는 변수
            user = User.query.filter_by(email = email).first()
            if user:
                # 위에서 검색한 user가 존재할 경우
                session['username'] = user.username
                flash('변경하실 비밀번호를 입력해주세요.')
                return redirect(url_for('.reset_password'))
            else:
                # 위에서 검색한 user가 존재하지 않을 경우
                flash('입력하신 이메일은 존재하지 않는 계정 이메일입니다.')
                return redirect(url_for('.reset'))

        # method가 POST가 아닐 시 대표 method: GET
        flash('비밀번호 찾으실 이메일을 입력해주세요.')
        return render_template('reset.html')
    else: # 로그인이 되어있는 상태에서 강제적으로 해당 페이지로 들어왔을 시 저장된 session값을 제거(pop)한 후 메인페이지로 리다이렉트 한다.
        flash('예상치 못한 접근으로 로그아웃 합니다.')
        session.pop('username', None)
        session.pop('id', None)
        return redirect(url_for('.login'))


# 초기화 하여 비밀번호를 변경하는 라우트 & 뷰함수
@auth.route('/reset_password', methods = ['GET', 'POST'])
def reset_password():
    if 'username' in session and not 'id' in session: # reset 뷰함수에서 저장된 session이 존재하는지 확인하는 조건문 단 id가 저장되어있으면 안된다. id가 저장이 되어있으면 로그인이 되어있다는 의미이다.
        if request.method == 'POST':
            # POST일 경우(submit을 했을 경우)
            password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
            password2 = request.form['password2'] # Client에서 입력한 password 확인 값을 저장하는 변수
            if password != password2:
                # 두 입력 값이 같지 않을 경우
                flash('비밀번호가 같지 않습니다.')
                return redirect(url_for('.reset_password'))

            # 비밀번호를 변경하기.
            password_hash = db.session.query(func.sha2(password, 224)) # 비밀번호 해쉬
            user = User.query.filter_by(username = session['username']).first()
            user.password_hash = password_hash
            db.session.commit()
            session.pop('username', None) # 변경이 완료(update 쿼리가 끝)되면 저장된 session을 제거(pop) 한 후에 로그인 페이지로 리다이렉트한다.password)
            flash('비밀번호 변경이 성공했습니다.')
            return redirect(url_for('.login'))
     
        # method가 post가 아닐시 대표: GET
        return render_template('reset_password.html')
    else:
        flash('문제 발생')
        return redirect(url_for('.login'))