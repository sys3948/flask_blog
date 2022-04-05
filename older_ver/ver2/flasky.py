from flask import Flask, flash, make_response, redirect, render_template, request, session, url_for
from datetime import datetime
import pymysql as mysql
import os


app = Flask(__name__)
conn = mysql.connect(host='192.168.111.139', port=3306, \
                    user='sys3948', passwd='Tlsdbstjr1+', \
                    db="FlaskyDB1", charset='utf8')

app.config['SECRET_KEY'] = 'secret key in flasky example ver1'
app.config['EXTENTION_FILES'] = set({'png', 'jpg', 'jpeg', 'gif'})
app.config['UPLOAD_FOLDERS'] = 'static/icon/'


def change_filename(name):
    if ' ' in name:
        name = name.replace(' ', '_')
    return name

# 메인 페이지 라우트 & 뷰함수
@app.route('/', methods = ['GET', 'POST'])
@app.route('/<int:num>', methods = ['GET', 'POST'])
def index(num = 1):
    try:
        limit_num = (num - 1) * 10 # 페이징을 구현하기 위해 limit 절의 offset 번호를 의미하는 변수
        show_follower = False # 전체 게시글 또는 follow한 게시글들을 출력하기 위해 구분하는 변수. True면 팔로우한 게시글 출력 False면 전체 게시글 출력
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
            if request.method == 'POST': # method가 POST지 확인하는 조건문
                body = request.form['body'] # 작성한 게시글의 내용을 받는 변수
                dt = datetime.now() # 현재 시간
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S') # 현재 시간을 mysql datetime type에 맞게 문자열 포맷팅
                with conn.cursor() as cur: # 커서 연결
                    # 작성한 게시글을 posts 테이블에 삽입하기. 삽입하는 데이터는 작성한 게시글의 내용을 저장한 body변수, 현재 로그인한 사용자의 id열 값,
                    # 현재 시간을 문자열 포맷한 timestamp 변수.
                    cur.execute('insert into posts(body, author_id, timestamp) values(%s, %s, %s)', (body, session['id'], timestamp))
                    # 작성한 유저의 게시글 수를 기록한 user_work_count.posts_count 열의 수에서 + 1 하는 update 쿼리문
                    print('test1')
                    cur.execute('update user_work_count set posts_count = posts_count + 1 \
                                 where user_id = %s', (session['id']))
                    print('test2')
                    # 방금 작성한 게시글의 id 컬럼 값을 검색하는 쿼리
                    cur.execute('select id from posts where author_id=%s and timestamp=%s', (session['id'], timestamp))
                    selected_id = cur.fetchone()
                    # 위에서 검색한 id 컬럼 값으로 comments_count 테이블에 해당 id 컬럼 값을 삽입하는 쿼리
                    cur.execute('insert into comments_count(post_id) values(%s)', (selected_id[0]))

                    # 작성한 유저를 팔로잉 한 유저를 검색하는 쿼리
                    cur.execute('select follower_id from followers where followed_id=%s', (session['id']))
                    followeds_id = cur.fetchall() #위 쿼리의 값을 저장하는 변수

                    # followeds_id 변수의 값이 있는지 확인하는 조건문
                    if followeds_id:
                        # followeds_id 변수에 값이 존재하는 경우(한 개 이상) for 루프문으로 값을 출력하여 아래의 쿼리를 실행한다.
                        for followed_id in followeds_id:
                            # 팔로우 한 유저들의 게시글의 수에 + 1 해주는 update 쿼리 문
                            cur.execute('update pagination set posts_count = posts_count + 1 \
                                         where id = %s', (followed_id))
                    # 본인의 게시글의 수에 + 1 해주는 update 쿼리 문 -- 수정(제거해도 된다.)
                    cur.execute('update pagination set my_posts_count = my_posts_count + 1 \
                                 where id = %s', (session['id']))

                    # 전체 게시글의 수에 + 1 해주는 update 쿼리 문
                    cur.execute('update pagination set posts_count = posts_count + 1 \
                                 where id = %s', ('0'))

                    conn.commit() # 위 쿼리들(insert, update) 저장하는 부분
                flash('작성 완료했습니다.')
                return redirect('/') # 작업이 끝났으면 GET method로 / route로 redirect 한다.
            # method가 GET일 때
            show_follower = bool(request.cookies.get('show_follower')) # 쿠키 'show_follower'의 값으로 전체 게시글 출력인지 follow한 게시글을 출력인지 구분해주는 변수
            with conn.cursor() as cur:
                # show_follower변수가 True이면 팔로우한 게시글을 출력하는 조건문
                if show_follower:
                    # Following한 유저들의 Posts를 가져오는 검색 쿼리
                    # posts.id = comments_count.post_id and followers.followed_id = posts.author_id and f.follower_id = u.id
                    cur.execute('select p.id, p.body, p.timestamp, u.username, u.profile_name, c.comments_count \
                                 from posts p join followers f join users u join comments_count c \
                                 on p.id = c.post_id and f.followed_id = p.author_id and f.followed_id = u.id \
                                 where f.follower_id = %d \
                                 order by p.timestamp desc \
                                 limit %d, 10' %(session['id'], limit_num))
                    posts = cur.fetchall() # 게시글의 값을 저장하는 변수

                    # 로그인한 유저의 follow한 게시글들의 수를 출력하는 검색 쿼리
                    cur.execute('select posts_count from pagination where id = %s', (session['id']))
                    selected_num = cur.fetchone() # 위의 검색 쿼리의 값을 저장하는 변수
                    paging = selected_num[0]//10 # 페이지의 수를 계산하는 변수(10개의 게시글들을 한 페이지에 출력하는 페이지에서 페이지의 수를 계산하는 변수)
                    if selected_num[0] % 10 > 0: # 10으로 나누어 나머지가 존재하면 페이지의 수 + 1를 하는 조건문
                        paging = paging + 1

                else: # 팔로우한 게시글이 아닌 전체 게시글을 출려하는 조건문(else 문)
                    # 전체 Posts를 가져오기
                    # posts join users join comments_count
                    # on posts.author_id = users.id and posts.id = comments_count.post_id
                    cur.execute('select p.id, p.body, p.timestamp, u.username, u.profile_name, c.comments_count \
                                 from posts p join users u join comments_count c \
                                 on p.author_id = u.id and p.id = c.post_id \
                                 order by p.timestamp desc \
                                 limit %d, 10' %(limit_num))
                    posts = cur.fetchall() # 위 검색 쿼리의 값을 저장하는 변수

                    cur.execute('select posts_count from pagination where id=0') # 전체 게시글의 수를 저장한 값을 가져오는 검색 쿼리
                    selected_num = cur.fetchone() # 위 검색 쿼리의 값을 저장하는 변수
                    paging = selected_num[0]//10 # 페이지의 수를 계산하는 변수(10개의 게시글들을 한 페이지에 출력하는 페이지에서 페이지의 수를 계산하는 변수)
                    if selected_num[0] % 10 > 0: # 10으로 나누어 나머지가 존재하면 페이지의 수 + 1를 하는 조건문
                        paging = paging + 1

        else: # 로그인이 되지 않는 상태의 조건문(else 문)
            with conn.cursor() as cur:
                # 전체 Posts를 가져오기
                # posts join users join comments_count
                # on posts.author_id = users.id and posts.id = comments_count.posts_id
                cur.execute('select p.id, p.body, p.timestamp, u.username, u.profile_name, c.comments_count \
                             from posts p join users u join comments_count c\
                             on p.author_id = u.id and p.id = c.post_id \
                             order by p.timestamp desc \
                             limit %d, 10' %(limit_num))
                posts = cur.fetchall() # 위 검색 쿼리의 값을 저장하는 변수

                cur.execute('select posts_count from pagination where id=0') # 전체 게시글의 수를 저장한 값을 가져오는 검색 쿼리
                selected_num = cur.fetchone() # 위 검색 쿼리의 값을 저장하는 변수
                paging = selected_num[0]//10 # 페이지의 수를 계산하는 변수(10개의 게시글들을 한 페이지에 출력하는 페이지에서 페이지의 수를 계산하는 변수)
                if selected_num[0] % 10 > 0: # 10으로 나누어 나머지가 존재하면 페이지의 수 + 1를 하는 조건문
                    paging = paging + 1

        print(paging)

        return render_template('index.html', show_follower = show_follower, posts = posts, paging = paging, current_page = num)
    except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except 문
        print(e)
        flash(str(e) + '라는 문제가 발생하여 실패했습니다.')
        return redirect('/')


# 로그인 라우트 & 뷰함수
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not 'username' in session: # 로그인이 안 되어있는 상태를 확인 하는 조건문
        if request.method == 'POST': # method가 POST인 경우(로그인을 하기위해 로그인 submit 버튼을 클릭 했을 때 발생하는 method)
            email = request.form['email'] # Client에서 입력한 email 값을 저장하는 변수
            password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
            try:
                with conn.cursor() as cur:
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
                print(e)
                flash(str(e)+'라는 문제로 인해 로그인이 실패했숩니다.')
                return redirect('/login')
            flash('로그인을 성공했습니다.')
            return redirect('/')
        return render_template('login.html')
    else: # 로그인 되어있는 상태에서 로그인 페이지로 들어갈시(강제적으로) 메인 페이지로 리다이렉트 하는 조건문(else 문)
        flash('예상치 못한 문제로 로그아웃 합니다.')
        session.pop('username', None)
        return redirect('/')


# 로그 아웃 라우트 & 뷰함수
@app.route('/logout')
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
        print(e)
        return redirect('/')


# 회원가입 라우트 & 뷰함수
@app.route('/register', methods=['GET', 'POST'])
def register():
    if  not'username' in session and not 'id' in session: # 로그인이 되어있지 않는 상태를 확인하는 조건문
        if request.method == 'POST': # method가 POST인지 확인하는 조건문
            email = request.form['email'] # Clinet에서 입력한 email 값을 저장하는 변수
            username = request.form['username'] # Clinet에서 입력한 username 값을 저장하는 변수
            password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수

            # user table에 email 또는 username이 존재하는 가? 만일 존재한다면 flash처리로 회원가입 하지 못하게 하기.
            try:
                with conn.cursor() as cur:
                    # 이메일과 닉네임 중복처리하는 쿼리 좀더 효율적으로 구현할 수 있는지 생각해보기.
                    # 입력한 email 값이 users.email에 존재하는지 확인하는 검색 쿼리
                    cur.execute('select email from users where email=%s', (email))
                    selected_email = cur.fetchone()
                    print(selected_email)
                    # 검색한 쿼리(email)의 값이 존재하는지 확인하는 조건문이며 존재하면 다시 회원 가입 페이지로 리다이렉트한다.
                    if selected_email:
                        flash('존재하는 이메일 입니다.')
                        return redirect('/register')
                    # 입력한 username 값이 users.username에 존재하는지 확인하는 검색 쿼리
                    cur.execute('select username from users where username=%s', (username))
                    select_username = cur.fetchone()
                    print(select_username)
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
                    cur.execute('insert into followers(follower_id, followed_id) values(%d, %d)' %(selected_id[0], selected_id[0]))
                    cur.execute('insert into follows_count(user_id) values(%s)', (selected_id[0]))
                    cur.execute('insert into user_work_count(user_id) values(%s)', (selected_id[0]))
                    cur.execute('insert into pagination(id) values(%s)', (selected_id[0]))
                    conn.commit()
            except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except문
                print(e)
                print(type(e))
                flash(str(e)+'라는 문제로 인해 회원가입이 실패했숩니다.')
                return redirect('/register')
            flash('가입완료 됬습니다.')
            return redirect('/login')
        return render_template('register.html')
    else: # 로그인이 되어있는 상태면 저장된 session을 제거(pop)한 후에 메인페이지로 리다이렉트 한다.
        session.pop('username', None)
        session.pop('id', None)
        flash('예상치 못한 문제로 로그아웃 합니다.')
        return redirect('/')


# 비밀번호 초기화하는 라우트 & 뷰함수
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if not 'username' in session and not 'id' in session: # 로그인이 되어있지 않는 상태를 확인하는 조건문
        if request.method == 'POST': # method가 POST인지 확인하는 조건문
            try:
                email = request.form['email'] # Client에서 입력한 값을 저장하는 변수
                with conn.cursor() as cur:
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
                print(e)
                flash(str(e) + '라는 문제로 비밀번호 찾기를 실패했습니다.')
                return redirect('/')
        return render_template('reset.html')
    else: # 로그인이 되어있는 상태에서 강제적으로 해당 페이지로 들어왔을 시 저장된 session값을 제거(pop)한 후 메인페이지로 리다이렉트 한다.
        flash('예상치 못한 접근으로 로그아웃 합니다.')
        session.pop('username', None)
        session.pop('id', None)
        return redirect('/')


# 초기화 하여 비밀번호를 변경하는 라우트 & 뷰함수
@app.route('/reset_password', methods = ['GET', 'POST'])
def reset_password():
    if 'username' in session and not 'id' in session: # reset 뷰함수에서 저장된 session이 존재하는지 확인하는 조건문 단 id가 저장되어있으면 안된다. id가 저장이 되어있으면 로그인이 되어있다는 의미이다.
        if request.method == 'POST':
            try:
                password = request.form['password'] # Client에서 입력한 password 값을 저장하는 변수
                with conn.cursor() as cur:
                    # 저장한 password 변수를 session username에 해당하는 users 행의 password_hash열에다 update하는 쿼리
                    # 비밀번호를 변경하는 update 쿼리문
                    cur.execute('update users set password_hash=sha2(%s, 224) where username=%s', (password, session['username']))
                    conn.commit()
            except Exception as e: # 예상치 못 한 Error가 발생했을 시 처리하는 except문
                print(e)
                flash(str(e) + '라는 문제가 발생해서 비밀번호 변경이 실패되었습니다.')
                session.pop('username', None)
                return redirect('/')

            session.pop('username', None) # 변경이 완료(update 쿼리가 끝)되면 저장된 session을 제거(pop) 한 후에 로그인 페이지로 리다이렉트한다.
            flash('비밀번호 변경이 성공했습니다.')
            return redirect('/login')
        flash('변경하실 비밀번호를 입력해주세요.')
        return render_template('reset_password.html')
    else:
        return redirect('/')


# 비밀번호 변경하는 라우트 & 뷰함수
@app.route('/change_password', methods=['GET', 'POST'])
def change_pw():
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        if request.method == 'POST':
            old_password = request.form['old_password'] # Client에서 입력한 값을 저장하는 변수(현재 지정된 비밀번호 값)
            try:
                with conn.cursor() as cur:
                    # 로그인 된 session값과 Client에서 입력한 현재 비밀번호 값이 맞는지 확인하는 검색 쿼리
                    cur.execute('select id from users where username=%s and password_hash=sha2(%s, 224)', (session['username'], old_password))
                    selected_id = cur.fetchone() # 위 검색 쿼리를 저장하는 변수
                    if selected_id: # 저장된 변수가 존재하는지 확인하는 조건문. 존재하면 아래와 같이 변경할 비밀번호 값으로 password_hash 열의 값을 session값을 이용하여 update한다.
                        password = request.form['password']
                        cur.execute('update users set password_hash=sha2(%s, 224) where username=%s', (password, session['username']))
                        conn.commit()
                    else: # 존재하지 않는다면 비밀번호 변경 페이지로 리다이렉트 한다.
                        flash('Old Password(현재 비밀번호)가 맞지 않습니다. 다시 입력해주세요.')
                        return redirect('/change_password')
                    flash('비밀번호 변경이 성공했습니다.')
                    return redirect('/')
            except Exception as e: # 예상치 못한 Error가 발생했을 시 처리하는 except문
                print(e)
                flash(str(e) + '라는 문제로 비밀번호 변경을 실패했습니다.')
                return redirect('/')
        return render_template('change_password.html')
    else:
        return redirect('/')


# 프로필 페이지의 라우트 & 뷰함수
@app.route('/profile/<username>')
@app.route('/profile/<username>/<int:num>')
def profile(username, num = 1):
    try:
        limit_num = (num - 1) * 10 # limit offset의 값을 지정하는 변수
        show_follow = False # Follow or Unfollow 버튼 활성화를 하기 위한 변수
        print(username)
        with conn.cursor() as cur:
            # 해당 프로필의 username에 해당하는 사용자 정보를 출력하는 검색 쿼리
            cur.execute('select u1.location, u1.about_me, u1.member_since, u1.profile_name, u2.posts_count, u2.comments_count \
                         from users u1 join user_work_count u2\
                         on u1.id = u2.user_id \
                         where username = %s', (username))
            select_data = cur.fetchone()
            if not select_data: # 검색한 쿼리의 값이 존재하지 않는다면 메인 페이지로 리다이렉트 하는 조건문
                flash('존재하지 않는 사용자 닉네임입니다.')
                return redirect('/')

            # 팔로워 수와 팔로잉 한 수를 찾는 검색쿼리
            cur.execute('select followed_count, follower_count from follows_count \
                         where user_id = (select id from users where username=%s)', (username))
            count = cur.fetchone()

            if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인 하는 조건문
                # 로그인이 되어있으면 해당 session값과 username 값을 이용하여 로그인한 유저가 해당 프로파일의 유저를 팔로우 했는지 확인하는 검색 쿼리
                cur.execute('select followed_id from followers \
                             where followed_id = (select id from users where username = %s) \
                             and follower_id = %s', (username, session['id']))
                follow_activation = cur.fetchone()
                if follow_activation: # 해당 변수 값이 존재하면 팔로우를 했다는 의미이다.
                    show_follow = True
                else: # 존재하지 않으면 팔로우를 안 했다는 의미이다.
                    show_follow = False

            # 해당 프로필의 유저가 작성한 게시글 10개를 출력하는 검색 쿼리
            cur.execute('select p.id, p.body, p.timestamp, u.username, u.profile_name, c.comments_count \
                         from posts p join users u join comments_count c \
                         on p.author_id = u.id and p.id = c.post_id \
                         where u.username=%s \
                         order by p.timestamp desc \
                         limit %s, 10', (username, limit_num))
            posts = cur.fetchall()

            # 해당 프로필의 페이징 작업을 위해 해당 프로필의 유저의 pagination.my_posts_count 열을 출력하는 검색 쿼리
            cur.execute('select my_posts_count from pagination where id=(select id from users where username = %s)', (username))
            selected_num = cur.fetchone()
            paging = selected_num[0]//10
            print(paging)
            if selected_num[0] % 10 > 0:
                paging = paging + 1
    except Exception as e: # 예상치 못한 에러를 처리하는 except문
        print(e)
        flash(str(e) + '로인한 프로필 접속 에러 발생')
        return redirect('/')
    return render_template('profile.html', profile_user = username, location = select_data[0], about_me = select_data[1],
                            member_since = select_data[2], image_name = select_data[3], posts_count = select_data[4],
                            comments_count = select_data[5], show_follow = show_follow, followers_count = count[0] - 1,
                            following_count = count[1] - 1, posts = posts, paging = paging, current_page = num, url = 'profile/' + username)


# 프로필 수정 라우트 & 뷰함수
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        print('test1')
        if request.method == 'POST': # method가 POST일 때의 조건문
            print(request.form)
            print(request.files)
            username = request.form['username'] # Client에서 입력한 username의 값을 저장하는 변수
            location = request.form['location'] # Client에서 입력한 location의 값을 저장하는 변수
            about_me = request.form['about_me'] # Client에서 입력한 about_me의 값을 저장하는 변수
            # 이미지 파일을 넣지 않을 시에 input type="file"은 request.files가 아닌 request.form으로 들어가는 문제가 발생한다.
            # 처리하는 조건문
            if 'file' in request.form:
                profile_img = None
            else:
                profile_img = request.files['file']


            if location == 'None': # location 값이 없을 때 처리하는 조건문
                location = None
            if about_me == 'None': # about_me 값이 없을 때 처리하는 조건문
                about_me = None
            if profile_img: # profile_img(프로필 이미지) 값이 존재하면 처리하는 조건문
                filename = profile_img.filename # 파일의 이름을 저장하는 변수
                if '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['EXTENTION_FILES']: # 파일 이름에 '.' 와 확장자 명이 존재하는가? 에대한 조건문
                    filename = change_filename(filename) # 파일 이름이 문제가 되지 않게 변경해주는 함수
                    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDERS'], filename)): # 위의 파일이름이 해당 디렉토리에 저장되어있는지 확인하는 조건문
                        # 해당 파일이 존재하지 않는다면 아래를 처리한다.
                        try:
                            with conn.cursor() as cur:
                                # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                                cur.execute('update users set username=%s, location=%s, about_me=%s, profile_name=%s where username=%s', \
                                    (username, location, about_me, filename, session['username']))
                                #  해당 파일을 저장하는 디렉토리에다 저장하기
                                profile_img.save(os.path.join(app.config['UPLOAD_FOLDERS'], filename))
                                conn.commit()
                        except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
                            print(e)
                            flash(str(e) + '라는 문제로 인해 프로필 편집을 실패합니다.')
                            return redirect(url_for('profile', username = session['username']))
                    else:
                        # 파일이 존재한다면 아래로 처리한다.
                        try:
                            with conn.cursor() as cur:
                                # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                                cur.execute('update users set username=%s, location=%s, about_me=%s, profile_name=%s where username=%s' \
                                    (username, location, about_me, filename, session['username']))
                                conn.commit()
                        except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
                            print(e)
                            flash(str(e) + '라는 문제로 인해 프로필 편집을 실패합니다.')
                            return redirect(url_for('profile', username = session['username']))
                    flash('프로필이 수정되었습니다.')
                    session['username'] = username
                else: # 파일이 확장자 또는 '.'이 존재하지 않을 때 처리하는 조건문(else 문)
                    flash('이미지 파일이 맞지 않아 프로필 수정을 실패합니다.')
                    
                return redirect(url_for('profile', username = session['username']))
            else: # 파일이 존재하지 않을 경우에 해당하는 조건문
                try:
                    with conn.cursor() as cur:
                        # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                        cur.execute('update users set username=%s, location=%s, about_me=%s where username=%s', \
                                    (username, location, about_me, session['username']))
                        print('test6')
                        conn.commit()
                except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
                    print(e)
                    flash(str(e) + '라는 문제로 인해 프로필 편집을 실패합니다.')
                    return redirect(url_for('profile', username = session['username']))

                flash('프로필이 수정되었습니다.')
                session['username'] = username
                return redirect(url_for('profile', username = session['username']))
        # method가 GET일 때
        try:
            with conn.cursor() as cur:
                # 로그인 한 유저의 정보를 출력하기 위한 검색 쿼리
                cur.execute('select location, about_me, profile_name from users where username=%s',(session['username']))
                selected_data = cur.fetchone()
        except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
            print(e)
            print(type(e))
            flash(str(e) + '라는 문제로 프로필 편집이 중단됨.')
            return redirect('/')
        return render_template('edit_profile.html', username = session['username'], location = selected_data[0], \
                               about_me = selected_data[1], image_name = selected_data[2])
    else:
        return redirect('/')


# 팔로우를 하는 것에 해당하는 라우트 & 뷰함수
@app.route('/follow/<username>')
def follow(username):
    try:
        if 'username' in session and 'id' in session:
            with conn.cursor() as cur:
                # 해당 username과 로그인 한 유저의 id 값을 followers 테이블에 삽입하는 쿼리.
                cur.execute('insert into followers(follower_id, followed_id) \
                            select u1.id, u2.id from (select %s as id) u1 join (select id from users where username=%s) u2', 
                            (session['id'], username))
                # 해당 username의 follower의 수를 증가하는 update 쿼리
                cur.execute('update follows_count set followed_count = followed_count + 1 \
                            where user_id = (select id from users where username = %s)', (username))
                # 로그인한 유저의 following의 수를 증가하는 update 쿼리
                cur.execute('update follows_count set follower_count = follower_count + 1 \
                            where user_id = %d' %(session['id']))

                # username이 작성한 posts의 수를 검색하는 쿼리
                cur.execute('select my_posts_count from pagination where id = (select id from users where username = %s)', (username))
                posts_count = cur.fetchone()

                if posts_count[0] > 0: # 위 검색 쿼리의 값이 0보다 크면 처리하는 조건문
                    # 로그인 한 유저의 팔로우 게시글의 수를 username의 작성한 게시글의 수만큼 증가하는 update 쿼리
                    cur.execute('update pagination set posts_count = posts_count + %s \
                                 where id = %s', (posts_count[0], session['id']))

            conn.commit()
            flash('팔로우 했습니다.')
        else:
            flash('로그인이 되지 않는 상태입니다. 로그인을 해주세요.')
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        print(e)
        flash(str(e) + '라는 문제로 팔로우를 실패했습니다.')
    finally:
        return redirect('/')


# 언팔로우 하는 것에 해당하는 라우트 & 뷰함수
@app.route('/unfollow/<username>')
def unfollow(username):
    try:
        if 'username' in session and 'id' in session:
            with conn.cursor() as cur:
                # 해다 username을 언팔로우 하니 로그인한 유저의 followers 테이블에서 제거하는 쿼리
                cur.execute('delete from followers where follower_id = %s and followed_id = (select id from users where username = %s)',
                             (session['id'], username))

                # username에 해당하는 유저의 팔로워 수를 감소하는( - 1) update 쿼리
                cur.execute('update follows_count set followed_count = followed_count - 1 \
                            where user_id = (select id from users where username = %s)', (username))
                
                # 로그인 한 유저의 팔로잉 수를 감소하는( - 1) update 쿼리
                cur.execute('update follows_count set follower_count = follower_count - 1 \
                            where user_id = %d' %(session['id']))

                # username이 작성한 게시글들의 수를 출력하는 검색 쿼리
                cur.execute('select my_posts_count from pagination where id = (select id from users where username = %s)', (username))
                posts_count = cur.fetchone()

                if posts_count[0] > 0: # 위 검색 쿼리의 값이 0 이상이면 그 수만큼 로그인한 유저의 팔로잉 게시글의 수를 감소하는 update 쿼리
                    cur.execute('update pagination set posts_count = posts_count - %s \
                                 where id = %s', (posts_count[0], session['id']))

            conn.commit()
            flash('언팔로우 했습니다.')
        else:
            flash('로그인 되지 않는 상태입니다. 로그인을 해주세요.')
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        print(e)
        flash(str(e) + '라는 문제로 언팔로우를 실패했습니다.')
    finally:
        return redirect('/')


# 팔로워들의 목록을 보는 라우트 & 뷰함수
@app.route('/followers/<username>')
def followers(username):
    try:
        with conn.cursor() as cur:
            # 해당 username의 팔로워들의 정보를 출력하기 위한 검색 쿼리
            cur.execute('select u.username, u.profile_name, f.timestamp from users u join followers f on u.id = f.follower_id \
                         where f.followed_id = (select id from users where username = %s) \
                         and f.follower_id != (select id from users where username = %s) \
                         order by f.timestamp desc', (username, username))
            follower_datas = cur.fetchall()

        return render_template('followers.html', username = username, follow_kind = 'Followers', follow_datas = follower_datas)
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        print(e)
        flash(str(e) + '라는 문제가 발생하여 팔로우 리스트 페이지에 에러가 발생했습니다.')
        return redirect('/')


# 해당 유저가 팔로잉한 유저들의 목록을 보는 라우트 & 뷰함수
@app.route('/following/<username>')
def following(username):
    try:
        with conn.cursor() as cur:
            # username이 팔로잉을 한 유저들의 정보를 출력하는 검색 쿼리
            cur.execute('select u.username, u.profile_name, f.timestamp from users u join followers f on u.id = f.followed_id \
                         where f.follower_id = (select id from users where username = %s) \
                         and f.followed_id != (select id from users where username = %s) \
                         order by f.timestamp desc', (username, username))
            follower_datas = cur.fetchall()

        return render_template('followers.html', username = username, follow_kind = 'Following', follow_datas = follower_datas)
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        print(e)
        flash(str(e) + '라는 문제가 발생하여 팔로우 리스트 페이지에 에러가 발생했습니다.')
        return redirect('/')


# 게시글 수정 라우트 & 뷰함수
@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    try:
        if 'username' in session and 'id' in session:
            with conn.cursor() as cur:
                if request.method == 'POST':
                    body = request.form['body']
                    # Client에서 입력한 값으로 수정하는 update 쿼리
                    cur.execute('update posts set body=%s where id=%s', (body, id))
                    conn.commit()
                    return redirect('/')
                # 해당 게시글의 내용을 출력하는 검색 쿼리
                cur.execute('select body \
                             from posts join users \
                             on posts.author_id = users.id \
                             where posts.id = %d and users.id = %d' %(id, session['id']))
                edit_posts = cur.fetchone()
            if edit_posts: # 게시글의 내용이 존재했을 때 작동하는 조건문
                return render_template('edit_post.html', body=edit_posts[0])
            else: # 게시글의 내용이 존재하지 않을 때 작동하는 조건문
                flash('수정할 게시글이 존재하지 않습니다.')
                return redirect('/')
        else:
            flash('edit_post 문제 발생!')
            return redirect('/')
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        print(e)
        flash(str(e) + '라는 문제로 인해 실패했습니다.')
        return redirect('/')


# 게시글의 내용 및 댓글을 다는 라우트 & 뷰함수
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    try:
        with conn.cursor() as cur:
            if request.method == 'POST':
                body = request.form['body'] # 작성한 댓글의 내용을 저장하는 변수
                # 댓글의 내용 및 작성자 그리고 해당 게시글의 id 컬럼 값을 저장하는 삽입 쿼리
                cur.execute('insert into comments(body, author_id, post_id) values(%s, %s, %s)', (body, session['id'], id))
                # 해당 게시글에 댓글을 작성했으니 게시글에 작성된 댓글의 수를 증가( + 1)를 해주는 update 쿼리
                cur.execute('update comments_count set comments_count = comments_count + 1 \
                             where post_id = %d' %(id))
                # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
                cur.execute('update user_work_count set comments_count = comments_count + 1 \
                             where user_id = %d' %(session['id']))
                conn.commit()
                return redirect('/post/'+str(id))

            # method가 GET 일 시
            # 해당 게시글의 정보들 출력하는 검색 쿼리
            cur.execute('select p.id, p.body, p.timestamp, u.username, u.profile_name, c.comments_count \
                         from posts p join users u join comments_count c \
                         on p.author_id = u.id and p.id = c.post_id \
                         where p.id = %d ' %(id))
            posts = cur.fetchall()

            # 해당 게시글의 댓글들의 정보를 출력하는 검색 쿼리
            cur.execute('select c.body, c.timestamp, u.username, u.profile_name \
                         from comments c join users u \
                         on c.author_id = u.id \
                         where c.post_id = %d \
                         order by c.timestamp desc' %(id))

            comments = cur.fetchall()
    except Exception as e: # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
        print(e)
        flash(str(e) + '라는 문제로 게시글 읽는 것을 실패했습니다.')
        return redirect('/')
    return render_template('post.html', posts = posts, comments = comments)


# 전체 게시글들을 선택할 시 쿠키에 저장하는 라우트 & 뷰함수
@app.route('/all')
def all():
    resp = make_response(redirect('/'))
    resp.set_cookie('show_follower', '')
    return resp


# 팔로우한 게시글들을 선택할 시 쿠키에 저장하는 라우트 & 뷰함수
@app.route('/followed')
def followed():
    resp = make_response(redirect('/'))
    resp.set_cookie('show_follower', 'True')
    return resp
