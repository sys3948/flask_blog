from flask import abort, flash, make_response, redirect, render_template, request, session, url_for
from . import auth
from .. import db


# 로그인 라우트 & 뷰함수
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not 'username' in session: # 로그인이 안 되어있는 상태를 확인 하는 조건문
        if request.method == 'POST': # method가 POST인 경우(로그인을 하기위해 로그인 submit 버튼을 클릭 했을 때 발생하는 method)
            email = request.form['email'] # Client에서 입력한 email 값을 저장하는 변수
            password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
            try:
                with db.cursor() as cur:
                    # 유저가 입력한 email, password값이 존재하는 users.id, users.username을 확인하는 검색 쿼리
                    cur.execute("select id, username from users where email=%s and password_hash = sha2(%s, 224)", (email, password))
                    selected_data = cur.fetchone() # 위 검색 쿼리의 값을 저장하는 변수
                    if not selected_data: # 저장된 변수의 값이 존재 하지 않는지 확인하는 조건문 존재하지 않을 시 로그인 페이지로 리다이렉트 한다.
                        flash('비밀번호가 옳바르지 않거나 해당 계정이 없는 문제로 로그인에 실패했습니다.')
                        return redirect('/login')
                    else: # 저장된 변수의 값이 존재하는 경우 해당 users.id, users.username 값을 session에다 저장한다.
                        session['id'] = selected_data[0]
                        session['username'] = selected_data[1]
            except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except 문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

            flash('로그인을 성공했습니다.')
            return redirect('/')
        return render_template('login.html')
    else: # 로그인 되어있는 상태에서 로그인 페이지로 들어갈시(강제적으로) 메인 페이지로 리다이렉트 하는 조건문(else 문)
        flash('예상치 못한 문제로 로그아웃 합니다.')
        session.pop('username', None)
        return redirect('/')


# 로그 아웃 라우트 & 뷰함수
@auth.route('/logout')
def logout():
    try:
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
            # 조건문이 True이면 아래와 같이 저장된 session을 제거(pop)한 후에 메인 페이지로 리다이렉트 한다.
            session.pop('username', None)
            session.pop('id', None)
            flash('로그아웃 합니다.')
            return redirect('/')
        else: # 로그인이 되지 않는 상태에서 강제적으로 로그아웃으로 들어가면 메인페이지로 리다이렉트 한다.
            flash('로그아웃 되었습니다.')
            return redirect('/')
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

            # user table에 email 또는 username이 존재하는 가? 만일 존재한다면 flash처리로 회원가입 하지 못하게 하기.
            try:
                with db.cursor() as cur:
                    # 이메일과 닉네임 중복처리하는 쿼리 좀더 효율적으로 구현할 수 있는지 생각해보기.
                    # 입력한 email 값이 users.email에 존재하는지 확인하는 검색 쿼리
                    cur.execute('select email from users where email=%s', (email))
                    selected_email = cur.fetchone()
                    # 검색한 쿼리(email)의 값이 존재하는지 확인하는 조건문이며 존재하면 다시 회원 가입 페이지로 리다이렉트한다.
                    if selected_email:
                        flash('존재하는 이메일 입니다.')
                        return redirect('/register')
                    # 입력한 username 값이 users.username에 존재하는지 확인하는 검색 쿼리
                    cur.execute('select username from users where username=%s', (username))
                    select_username = cur.fetchone()
                    # 검색한 쿼리(username)의 값이 존재하는지 확인하는 조건문이며 존재한다면 회원가입 페이지로 이동한다.
                    if select_username:
                        flash('존재하는 닉네임 입니다.')
                        return render_template('register.html', email = email)
                    # 위의 조건문들을 통과하면 입력한 email과 username이 users 테이블에 존재하지 않다는 의미로 users 테이블에 email, username, password를
                    # 삽입하는 쿼리문이다.
                    cur.execute("insert into users(email, username, password_hash) values(%s, %s, sha2(%s, 224))", (email, username, password))
                    # 삽입한 email 값으로 해당 id 값을 검색하는 쿼리
                    cur.execute('select id from users where email=%s', (email))
                    selected_id = cur.fetchone() # 위 검색 쿼리의 값을 저장하는 변수
                    # 저장한 변수의 값으로 followers, follows_count, user_work_count, pagination 테이블에 삽입하는 쿼리
                    # 팔로우 개념에서는 우선 자기가 자신을 팔로우 한다는 것을 잊지말자!
                    cur.execute('insert into follows(follower_id, followed_id) values(%d, %d)' %(selected_id[0], selected_id[0]))
                    cur.execute('insert into follows_count(user_id) values(%s)', (selected_id[0]))
                    cur.execute('insert into works_count(id) values(%s)', (selected_id[0]))
                    db.commit()
            except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

            flash('가입완료 됬습니다.')
            return redirect('/login')
        return render_template('register.html')
    else: # 로그인이 되어있는 상태면 저장된 session을 제거(pop)한 후에 메인페이지로 리다이렉트 한다.
        session.pop('username', None)
        session.pop('id', None)
        flash('예상치 못한 문제로 로그아웃 합니다.')
        return redirect('/')


# 비밀번호 초기화하는 라우트 & 뷰함수
@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    if not 'username' in session and not 'id' in session: # 로그인이 되어있지 않는 상태를 확인하는 조건문
        if request.method == 'POST': # method가 POST인지 확인하는 조건문
            try:
                email = request.form['email'] # Client에서 입력한 값을 저장하는 변수
                with db.cursor() as cur:
                    # 입력한 email값이 users.email에 존재하는지 확인하는 검색 쿼리
                    cur.execute('select username from users where email=%s', (email))
                    selected_data = cur.fetchone() # 위 쿼리의 값을 저장하는 변수
                    if selected_data: # 변수에 값이 존재하는지 확인하는 조건문 존재한다면 해당 값(username)을 session에다 저장한 후에 비밀번호 변경 페이지로 리다이렉트 한다.
                        session['username'] = selected_data[0]
                        return redirect('/reset_password')
                    else: # 존재하지 않으면 초기화 페이지로 리다이렉트 한다.
                        flash('입력하신 이메일은 존재하지 않는 계정 이메일입니다.')
                        return redirect('/reset')
            except Exception as e: # 예상치 못 한 Error가 발생했을 시 처리하는 except 문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

        return render_template('reset.html')
    else: # 로그인이 되어있는 상태에서 강제적으로 해당 페이지로 들어왔을 시 저장된 session값을 제거(pop)한 후 메인페이지로 리다이렉트 한다.
        flash('예상치 못한 접근으로 로그아웃 합니다.')
        session.pop('username', None)
        session.pop('id', None)
        return redirect('/')


# 초기화 하여 비밀번호를 변경하는 라우트 & 뷰함수
@auth.route('/reset_password', methods = ['GET', 'POST'])
def reset_password():
    if 'username' in session and not 'id' in session: # reset 뷰함수에서 저장된 session이 존재하는지 확인하는 조건문 단 id가 저장되어있으면 안된다. id가 저장이 되어있으면 로그인이 되어있다는 의미이다.
        if request.method == 'POST':
            try:
                password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
                with db.cursor() as cur:
                    # 저장한 password 변수를 session username에 해당하는 users 행의 password_hash열에다 update하는 쿼리
                    # 비밀번호를 변경하는 update 쿼리문
                    cur.execute('update users set password_hash=sha2(%s, 224) where username=%s', (password, session['username']))
                    db.commit()
            except Exception as e: # 예상치 못 한 Error가 발생했을 시 처리하는 except문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

            session.pop('username', None) # 변경이 완료(update 쿼리가 끝)되면 저장된 session을 제거(pop) 한 후에 로그인 페이지로 리다이렉트한다.
            flash('비밀번호 변경이 성공했습니다.')
            return redirect('/login')
        flash('변경하실 비밀번호를 입력해주세요.')
        return render_template('reset_password.html')
    else:
        return redirect('/')