from flask import abort, current_app, flash, make_response, redirect, render_template, request, session, url_for
from . import main
from .. import db, all_post_count, all_user_count
from .file_func import change_filename, create_file
from .db_query_func import follow_query, follow_search_query, following_query, following_search_query
import os


# 메인 페이지 라우트 & 뷰함수
@main.route('/')
def transmit_index():
    if 'username' in session and 'id' in session:
        # 로그인이 되어있으면 게시글 작성 페이지로 리다이렉션
        return redirect(url_for('.index', username = session['username']))
    else:
        # 로그인이 되어있지 않으면 로그인 페이지로 리다이렉션
        flash('로그인을 해주세요.')
        return redirect(url_for('auth.login'))

# 게시글 작성 페이지의 라우트 & 뷰함수
@main.route('/<username>', methods = ['GET', 'POST'])
@main.route('/<username>/<int:num>', methods = ['GET', 'POST'])
def index(username, num = 1):
    try:
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
            if session['username'] == username:
                # 해당 게시글 작성 페이지의 유저와 로그인 한 유저가 같은경우 해당 페이지로 접속.
                rnum = (num - 1) * 10 # limit 절의 offset을 지정하는 변수
                if request.method == 'POST': # method가 POST지 확인하는 조건문
                    if 'search' in request.form:
                        # 게시글 검색을 했을 경우
                        search = request.form['search']
                        with db.cursor() as cur: # 커서 연결
                            cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id, p.body_text \
                                         from ( \
                                           select id, username, profile_filename \
                                           from users \
                                           where username = %s \
                                         ) as u inner join posts as p \
                                         on u.id = p.author_id \
                                         where u.username like %s or p.body_text like %s \
                                         order by p.timestamp desc', (username, "%"+search+"%", "%"+search+"%"))

                        posts = cur.fetchall()
                        post_count = len(posts) # 검색한 페이지의 pagination을 구현하기 위한 검색 결과의 게시글의 수를 정장하는 변수
                        posts = posts[0:10] # 검색한 결과의 게시글 최초 10개를 저장하는 변수

                        # paginagion 구현
                        paging = post_count // 10
                        if post_count % 10 > 0:
                            paging = paging + 1

                        # GET method일 시에 해당 검색한 결과의 게시글을 출력하기 위한 page url을 저장하는 변수(url에는 검색 값, 총 페이지 수 등의 값이 저장되어있다.)
                        pageUrl = url_for('.index', username = username, search = True, result = search, paging = paging)

                        return render_template('index.html', username = username, datas = posts, paging = paging,
                                                current_page = num, pageUrl = pageUrl)
                    else:
                        # 게시글 작성할 경우
                        body = request.form['body'] # 작성한 게시글의 내용을 받는 변수
                        bodytext = request.form['searchBody'] # 검색하기 위해 작성한 글의 텍스트 부분만 받는 변수
                        # html 파일 생성하기.
                        name = create_file(body)
                        with db.cursor() as cur: # 커서 연결
                            # html 파일을 생성하면 해당 파일 이름과 작성자의 id column값을 posts 테이블에 삽입한다.
                            cur.execute('insert into posts(author_id, name, body_text) values(%s, %s, %s)', (session['id'], name, bodytext))
                            # 작성한 user의 post_count를 1 증가한다.
                            cur.execute('update users set post_count = post_count + 1 \
                                         where id = %s', (session['id']))

                        db.commit() # 위 쿼리들(insert, update) 저장하는 부분

                        # 게시글 작성이 완료되었으면 전체 게시글의 수를 저장하는 변수의 값을 1증가한다.
                        global all_post_count
                        all_post_count = all_post_count + 1

                        flash('작성 완료했습니다.')
                        return redirect(url_for('.index', username = session['username'])) # 작업이 끝났으면 GET method로 /<username> route로 redirect 한다.

                # method가 GET일 때
                if request.args.get('search'):
                    # 검색한 결과의 게시글을 볼 경우
                    num = int(request.args.get('paging').split('/')[1]) # 현제 페이지를 저장하는 변수
                    paging = int(request.args.get('paging').split('/')[0]) # 총 페이지 수를 저장하는 변수
                    rnum = (num - 1) * 10 # limit 절의 offset을 지정하는 변수
                    search = request.args.get('result') # 검색 값을 저장한 변수

                    with db.cursor() as cur: # 커서 연결
                        # 검색 값에 맞는 게시글들을 출력하는 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id \
                                     from ( \
                                      select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id, p.body_text \
                                      from ( \
                                        select id, username, profile_filename \
                                        from users \
                                        where id = %s \
                                      ) as u inner join posts as p \
                                      on u.id = p.author_id \
                                      order by p.timestamp desc \
                                     ) \
                                     where u.username like %s and p.body_text like %s \
                                     limit %s, 10', (check_user[0], "%"+search+"%", "%"+search+"%", rnum))

                        posts = cur.fetchall()

                    # 해당 검색한 결과의 다음 게시글들을 출력하기 위한 page url을 저장하는 변수(url에는 검색 값, 총 페이지 수 등의 값이 저장되어있다.)
                    pageUrl = url_for('.index', username = username, search = True, result = search, paging = request.args.get('paging'))
                        
                else:
                    # 전체 게시글을 볼 경우
                    with db.cursor() as cur: # 커서 연결
                        # 전체 게시글을 출력하는 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id\
                                    from ( \
                                      select id, username, profile_filename \
                                      from users \
                                      where username = %s \
                                    ) u inner join posts p \
                                    on u.id = p.author_id \
                                    order by timestamp desc \
                                    limit %s, 10', (username, rnum))

                        posts = cur.fetchall() # 위 검색 쿼리의 값을 저장하는 변수

                        cur.execute('select post_count from users where username = %s', (username))
                        post_count = cur.fetchone()

                    # 전체 게시글에서 다음 게시글을 출력하기 위한 page url을 저장하는 변수
                    pageUrl = url_for('.index', username = username)

                    # pagination 구현하는 로직
                    paging = post_count[0] // 10
                    if post_count[0] % 10 > 0: # 10으로 나누어 나머지가 존재하면 페이지의 수 + 1를 하는 조건문
                        paging = paging + 1
                    
                return render_template('index.html', username = username, datas = posts, paging = paging, current_page = num, pageUrl = pageUrl)

            else:
                # 같지 않는 경우 프로필 페이지로 리다이렉션
                return redirect(url_for('.profile', username = username))

        else: # 로그인이 되지 않는 상태의 조건문(else 문)
            flash('로그인을 해주세요.')
            return redirect(url_for('auth.login')) # 로그인 페이지로 이동
    except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# home 라우트 & 뷰함수
@main.route('/home', methods = ['GET', 'POST'])
@main.route('/home/<int:num>', methods = ['GET', 'POST'])
def home(num = 1):
    try:
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
            rnum = (num - 1) * 10 # limit 절의 offset 수를 저장한 변수

            # posts를 보여줄 지 users를 보여줄 지 정하는 구문
            show_page = True
            if request.cookies.get('show_page') == '':
                show_page = False # 등록된 유저 목록을 보여주기
            else:
                show_page = True # 작성한 게시글들을 보여주기

            # POST 일 시(검색)
            if request.method == 'POST':
                search = request.form['search']
                if show_page:
                    # 게시글 검색
                    with db.cursor() as cur:
                        # 검색한 값에 맞는 게시글을 출력하는 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id\
                                     from users as u inner join posts as p \
                                     on u.id = p.author_id \
                                     where u.username like %s or p.body_text like %s \
                                     order by p.timestamp desc', ("%"+search+"%", "%"+search+"%"))

                        datas = cur.fetchall()
                else:
                    # 유저 검색
                    with db.cursor() as cur:
                        # 검색한 값에 맞는 유저들을 출려학는 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, u.member_since, f.followed_id\
                                     from users as u \
                                     left outer join ( \
                                       select * \
                                       from follows \
                                       where follower_id = %s \
                                     ) as f \
                                     on u.id  = f.followed_id \
                                     where u.username like %s \
                                     order by u.member_since desc', (session['id'], "%"+search+"%"))

                        datas = cur.fetchall()

                data_count = len(datas) # 검색 결과(게시글 or 유저 목록)들의 수를 저장하는 변수
                datas = datas[0:10] # 검색 결과의 최초 10개를 저장하는 변수

                # pagination 구현 로직
                paging = data_count // 10
                if data_count % 10 > 0:
                    paging = paging + 1

                # 검색한 게시글들의 다음 게시글들을 보기 위한 url을 저장한 변수
                url = url_for('.home', search = True, result = search, paging = paging)

                return render_template('home.html', datas = datas, paging = paging, show_page = show_page, current_page = num, pageUrl = url)

            # GET일 시
            if show_page:
                # 게시글을 볼 때
                if request.args.get('search'):
                    # 검색한 게시글 목록

                    search = request.args.get('result') # 검색 값을 저장한 변수
                    paging = request.args.get('paging').split('/')[0] # 총 페이지 수를 저장한 변수
                    num = int(request.args.get('paging').split('/')[1]) # 현재 페이지를 저장한 변수
                    rnum = (num - 1) * 10 # limit 절의 offset 값을 저장한 변수
                    url = url_for('.home', search = True, result = search, paging = paging) # 다음 게시글들을 보기 위한 url을 저장한 변수

                    with db.cursor() as cur:
                        # 검색 값에 맞는 게시글을 출력하는 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id\
                                     from ( select id, username, profile_filename from users ) as u inner join posts p \
                                     on u.id = p.author_id \
                                     where u.username like %s or p.body_text like %s \
                                     order by p.timestamp desc \
                                     limit %s, 10', ("%"+search+"%", "%"+search+"%", rnum))

                        datas = cur.fetchall()
                else:
                    # 전체 게시글 목록
                    with db.cursor() as cur:
                        # 작성된 전체 게시글 출력하기 위한 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id \
                                    from posts p inner join (select id, username, profile_filename \
                                                       from users) u \
                                    on p.author_id = u.id \
                                    order by p.timestamp desc \
                                    limit %s, 10', (rnum))
                        
                        datas = cur.fetchall()

                    # paginstion 구현 로직
                    paging = all_post_count // 10
                    if paging % 10 > 0:
                        paging = paging + 1

                    url = url_for('.home')

            else:
                # 유저 목록을 볼 때
                if request.args.get('search'):
                    # 검색한 유저 목록
                    search = request.args.get('result') # 검색 값을 저장한 변수
                    paging = request.args.get('paging').split('/')[0] # 총 페이지 수를 저장한 변수
                    num = int(request.args.get('paging').split('/')[1]) # 현제 페이지를 저장한 변수
                    rnum = (num - 1) * 10 # limit 절의 offset 값을 저장한 변수
                    url = url_for('.home', search = True, result = search, paging = paging) # 다음 유저 목록들을 보기 위한 url을 저장한 변수(검색)

                    with db.cursor() as cur:
                        # 검색 값에 맞는 유저목록을 출력하는 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, u.member_since, f.followed_id\
                                     from ( \
                                       select id, username, profile_filename, member_since \
                                       from users \
                                     ) as u left outer join ( \
                                       select followed_id, follower_id \
                                       from follows \
                                       where follower_id = %s \
                                     ) as f \
                                     on u.id = f.followed_id \
                                     where u.username like %s \
                                     order by member_since desc \
                                     limit %s, 10', (session['id'], "%"+search+"%", rnum))

                        datas = cur.fetchall()
                else:
                    # 전제 유저 목록
                    with db.cursor() as cur:
                        # 등록된 전체 유저들을 출력하기 위한 검색 쿼리
                        cur.execute('select u.username, u.profile_filename, u.member_since, f.followed_id\
                                    from ( \
                                      select id, username, profile_filename, member_since \
                                      from users \
                                    ) as u left outer join ( \
                                      select followed_id, follower_id \
                                      from follows \
                                      where follower_id = %s and followed_id != %s \
                                    ) as f \
                                    on u.id = f.followed_id \
                                    order by u.member_since desc \
                                    limit %s, 10', (session['id'], session['id'], rnum))
                        
                        datas = cur.fetchall()

                    # pagination 구현 로직
                    paging = all_user_count // 10
                    if paging % 10 > 0:
                        paging = paging + 1

                    url = url_for('.home') # 다음 유저 목록들을 보기 위한 url을 저장한 변수(전체)

            return render_template('home.html', datas = datas, paging = paging, show_page = show_page, current_page = num, pageUrl = url)

        else:
            flash('로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e:
        flash(str(e) + '라는 문재가 발생했습니다.')
        abort(500)


# 게시글을 불러오는 라우트
@main.route('/postFiles/<id>/<name>')
@main.route('/<username>/postFiles/<id>/<name>')
@main.route('/profile/postFiles/<id>/<name>')
@main.route('/profile/<username>/postFiles/<id>/<name>')
@main.route('/home/postFiles/<id>/<name>')
def postFiles(id, name, username = None):
    # jquery.load()로 호출하는 url을 templates/postFiles/users table의 id column value/filname 의 file을 return한다.
    return render_template('postFiles/%s/%s' %(id, name))


# 비밀번호 변경하는 라우트 & 뷰함수
@main.route('/change_password', methods=['GET', 'POST'])
def change_pw():
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        if request.method == 'POST':
            old_password = request.form['old_password'] # Client에서 입력한 값을 저장하는 변수(현재 지정된 비밀번호 값)
            try:
                with db.cursor() as cur:
                    # 로그인 된 session값과 Client에서 입력한 현재 비밀번호 값이 맞는지 확인하는 검색 쿼리
                    cur.execute('select id from users where username=%s and password_hash=sha2(%s, 224)', (session['username'], old_password))
                    selected_id = cur.fetchone() # 위 검색 쿼리를 저장하는 변수
                    if selected_id: # 저장된 변수가 존재하는지 확인하는 조건문. 존재하면 아래와 같이 변경할 비밀번호 값으로 password_hash 열의 값을 session값을 이용하여 update한다.
                        password = request.form['password'] # 비밀번호 값을 저장한 변수
                        password2 = request.form['password2'] # 비밀번호 확인 값을 저장한 변수
                        if password != password2:
                            # 두 값(비밀번호, 비밀번호 확인)이 맞지 않으면 비밀번호 변경 페이지로 리다이렉션.
                            flash('변경하실 비밀번호와 비밀번호 확인 값이 맞지 않습니다. 다시 입력해주세요.')
                            return redirect(url_for('.change_password'))

                        # 비밀번호 변경하기 위한 update query
                        cur.execute('update users set password_hash=sha2(%s, 224) where username=%s', (password, session['username']))

                    else: # 존재하지 않는다면 비밀번호 변경 페이지로 리다이렉트 한다.
                        flash('Old Password(현재 비밀번호)가 맞지 않습니다. 다시 입력해주세요.')
                        return redirect(url_for('.change_pw'))

                db.commit()
                flash('비밀번호 변경이 성공했습니다.')
                return redirect(url_for('.index', username = session['username']))
            except Exception as e: # 예상치 못한 Error가 발생했을 시 처리하는 except문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

        return render_template('change_password.html')
    else:
        flash('로그인이 되어있지 않아 비밀번호 변경을 못 합니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 프로필 페이지의 라우트 & 뷰함수
@main.route('/profile/<username>')
@main.route('/profile/<username>/<int:num>')
def profile(username, num = 1):
    try:
        if 'username' in session and 'id' in session: # 로그인 되었는지 확인하는 조건문
            rnum = (num - 1) * 10 # limit offset의 값을 지정하는 변수
            show_follow = False # Follow or Unfollow 버튼 활성화를 하기 위한 변수
            with db.cursor() as cur:
                # 해당 프로필의 username에 해당하는 사용자 정보를 출력하는 검색 쿼리
                cur.execute('select location, about_me, member_since, profile_filename, post_count, follow_count, following_count \
                             from users where username = %s', (username))
                select_data = cur.fetchone()

                if not select_data: # 검색한 쿼리의 값이 존재하지 않는다면 메인 페이지로 리다이렉트 하는 조건문
                    flash('존재하지 않는 사용자 닉네임입니다.')
                    return redirect(url_for('.transmit_index'))

                # 로그인한 유저와 해당 프로필 페이지의 유저와 같지 않을 시에 팔로우 또는 언팔로우 버튼 생성하기.
                if username != session['username']:
                    # 프로필의 유저를 로그인 한 유저가 팔로우를 했는지 확인하는 검색 쿼리
                    cur.execute('select followed_id from follows \
                                where followed_id = (select id from users where username = %s) \
                                and follower_id = %s', (username, session['id']))
                    follow_activation = cur.fetchone()
                    if follow_activation: # 해당 변수 값이 존재하면 팔로우를 했다는 의미이다.
                        show_follow = True
                    else: # 존재하지 않으면 팔로우를 안 했다는 의미이다.
                        show_follow = False
                else:
                    # 로그인 한 유저의 프로필 페이지.
                    show_follow = None

                # 해당 프로필의 유저가 작성한 게시글 10개를 출력하는 검색 쿼리
                cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count, p.id\
                             from (select id, username, profile_filename \
                                   from users \
                                   where username = %s) u join posts p\
                             on u.id = p.author_id \
                             order by p.timestamp desc \
                             limit %s, 10', (username, rnum))

                posts = cur.fetchall()

            # pagination 구현 로직
            paging = select_data[4]//10
            if select_data[4] % 10 > 0:
                paging = paging + 1


            return render_template('profile.html', profile_user = username, location = select_data[0], about_me = select_data[1],
                            member_since = select_data[2], image_name = select_data[3], posts_count = select_data[4],
                            show_follow = show_follow, followers_count = select_data[5], following_count = select_data[6], 
                            datas = posts, paging = paging, current_page = num, url = url_for('.profile', username = username))
        
        else:
            # 로그인이 되어있지 않는 경우
            flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e: # 예상치 못한 에러를 처리하는 except문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 프로필 수정 라우트 & 뷰함수
@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    try:
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
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
                    if '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['EXTENTION_FILES']: # 파일 이름에 '.' 와 확장자 명이 존재하는가? 에대한 조건문
                        filename = change_filename(filename) # 파일 이름이 문제가 되지 않게 변경해주는 함수
                        if not os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDERS'], filename)): # 위의 파일이름이 해당 디렉토리에 저장되어있는지 확인하는 조건문
                            # 해당 파일이 지정한 디렉토리 내에 존재하지 않는다면 아래를 처리한다.

                            # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                            with db.cursor() as cur:
                                cur.execute('update users set username=%s, location=%s, about_me=%s, profile_filename=%s where username=%s',
                                        (username, location, about_me, filename, session['username']))
                            #  해당 파일을 저장하는 디렉토리에다 저장하기
                            profile_img.save(os.path.join(current_app.config['UPLOAD_FOLDERS'], filename))
                            db.commit()

                        else:
                            # 파일이 존재한다면 아래로 처리한다.
                            # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                            with db.cursor() as cur:
                                cur.execute('update users set username=%s, location=%s, about_me=%s, profile_filename=%s where username=%s',
                                        (username, location, about_me, filename, session['username']))
                            db.commit()

                        flash('프로필이 수정되었습니다.')
                        session['username'] = username
                    else: # 파일이 확장자 또는 '.'이 존재하지 않을 때 처리하는 조건문(else 문)
                        flash('이미지 파일이 맞지 않아 프로필 수정을 실패합니다.')
                            
                    return redirect(url_for('.profile', username = session['username']))
                else: # 파일이 존재하지 않을 경우에 해당하는 조건문
                    # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                    with db.cursor() as cur:
                        cur.execute('update users set username=%s, location=%s, about_me=%s where username=%s',
                                (username, location, about_me, session['username']))
                    db.commit()

                    flash('프로필이 수정되었습니다.')
                    session['username'] = username
                    return redirect(url_for('.profile', username = session['username']))

            # method가 GET일 때
            # 로그인 한 유저의 정보를 출력하기 위한 검색 쿼리
            with db.cursor() as cur:
                cur.execute('select location, about_me, profile_filename from users where username=%s',(session['username']))
                selected_data = cur.fetchone()

            return render_template('edit_profile.html', username = session['username'], location = selected_data[0],
                                    about_me = selected_data[1], image_name = selected_data[2])
        else:
            flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 팔로우를 하는 것에 해당하는 라우트 & 뷰함수
@main.route('/follow/<username>')
def follow(username):
    try:
        if 'username' in session and 'id' in session:
            if username != session['username']:
                with db.cursor() as cur:
                    # 해당 username과 로그인 한 유저의 id 값을 followers 테이블에 삽입하는 쿼리.
                    cur.execute('insert into follows(follower_id, followed_id) \
                                select u1.id, u2.id from (select %s as id) u1 join (select id from users where username=%s) u2', 
                                (session['id'], username))
                    # 해당 username의 follower의 수를 증가하는 update 쿼리
                    cur.execute('update users set follow_count = follow_count + 1 \
                                where username = %s', (username))
                    # 로그인한 유저의 following의 수를 증가하는 update 쿼리
                    cur.execute('update users set following_count = following_count + 1 \
                                where id = %d' %(session['id']))

                db.commit()
                flash('팔로우 했습니다.')

            else:
                flash('본인입니다.')
        else:
            flash('로그인이 되지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

        return redirect(request.referrer)

    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 언팔로우 하는 것에 해당하는 라우트 & 뷰함수
@main.route('/unfollow/<username>')
def unfollow(username):
    try:
        if 'username' in session and 'id' in session:
            if username != session['username']:
                with db.cursor() as cur:
                    # 해다 username을 언팔로우 하니 로그인한 유저의 followers 테이블에서 제거하는 쿼리
                    cur.execute('delete from follows where follower_id = %s and followed_id = (select id from users where username = %s)',
                                (session['id'], username))

                    # username에 해당하는 유저의 팔로워 수를 감소하는( - 1) update 쿼리
                    cur.execute('update users set follow_count = follow_count - 1 \
                                where username = %s', (username))
                    
                    # 로그인 한 유저의 팔로잉 수를 감소하는( - 1) update 쿼리
                    cur.execute('update users set following_count = following_count - 1 \
                                where id = %d' %(session['id']))

                db.commit()
                flash('언팔로우 했습니다.')

            else:
                flash('본인입니다.')
        else:
            flash('로그인 되지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

        return redirect(request.referrer)

    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 팔로워들 또는 팔로잉을 한 유저들의 목록을 보는 라우트 & 뷰함수
@main.route('/follow_list/<username>', methods=['GET', 'POST'])
@main.route('/follow_list/<username>/<jf>', methods=['GET', 'POST'])
@main.route('/follow_list/<username>/<jf>/<int:num>', methods=['GET', 'POST'])
def follow_list(username, jf = 'follow', num = 1):
    # 해당 username의 팔로우와 팔로잉
    try:
        if 'username' in session and 'id' in session:
            rnum = (num - 1) * 10

            if jf == 'follow':
                show_follow = True
            elif jf == 'following':
                show_follow = False
            else:
                return redirect(url_for('.follow_list', username = username, jf = 'follow'))

            if request.method == 'POST':
                search = request.form['search']
                if show_follow:
                    # 팔로우 부분
                    follow_datas = follow_search_query(username, session['id'], search)
                else:
                    # 팔로잉 부분
                    follow_datas = following_search_query(username, session['id'], search)

                # pagination 구현부분
                paging = len(follow_datas) // 10
                if paging % 10 > 0:
                    paging = paging + 1

                follow_datas = follow_datas[rnum:rnum+10]

                url = url_for('.follow_list', username = username, jf = jf, search = True, result = search, paging = paging)

                print(url)

                return render_template('followers.html', username = username, show_follow = show_follow, datas = follow_datas, paging = paging,
                                       current_page = num, pageUrl = url)

            # method GET
            if show_follow:
                # 팔로우 부분
                if request.args.get('search'):

                    num = int(request.args.get('paging').split('/')[1])
                    rnum = (num - 1) * 10
                    follow_datas = follow_search_query(username, session['id'], search = request.args.get('result'), rnum = rnum, limit = True)
                
                else:
                    follow_datas, user_count = follow_query(username, session['id'], rnum)

            else:
                # 팔로잉 부분
                if request.args.get('search'):
                    # 검색한 팔로잉 목록 결과 출력
                    
                    num = int(request.args.get('paging').split('/')[1])
                    rnum = (num - 1) * 10
                    follow_datas = following_search_query(username, session['id'], request.args.get('result'), limit = True, rnum = rnum)

                else:
                    # 검색하지 않는 일반 팔로잉 목록 출력

                    follow_datas, user_count = following_query(username, session['id'], rnum)

            # 페이지네이션 구현 하기.
            if request.args.get('paging'):
                paging = int(request.args.get('paging').split('/')[0])
                url = url_for('.follow_list', username = username, jf = jf, search = request.args.get('search'), result = request.args.get('result'), paging = paging)
            else:
                paging = user_count // 10
                url = url_for('.follow_list', username = username, jf = jf)

                if paging % 10 > 0:
                    paging = paging + 1

            return render_template('followers.html', username = username, show_follow = show_follow, datas = follow_datas, paging = paging,
                                   current_page = num, pageUrl = url)
        else:
            flash('로그인이 되어있지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        return abort(500)


# 게시글 수정 라우트 & 뷰함수
@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                if request.method == 'POST':
                    body = request.form['body']
                    
                    # Client에서 작성한 내용을 해당 파일에 덮어 쓰는 로직
                    cur.execute('select name from posts where id = %s', (id))
                    edit_posts = cur.fetchone()
                    filePath = current_app.config['UPLOAD_POST_PATH_DEFAULT'] + edit_posts[0]

                    f = open(filePath, 'wt', encoding = 'utf-8')
                    f.write(body)
                    f.close()

                    return redirect(url_for('.post', id = id))

                # 메소드가 GET일 때
                # 해당 게시글의 파일을 출력하는 검색 쿼리
                cur.execute('select username from users where id = (select author_id from posts where id = %s)', (id))
                data = cur.fetchone()

                if data[0] != session['username']:
                    flash('작성한 유저가 아닙니다.')
                    return redirect(request.referrer)

                cur.execute('select name from posts where id = %s', (id))
                edit_posts = cur.fetchone()
                filePath = current_app.config['UPLOAD_POST_PATH_DEFAULT'] + edit_posts[0]

                f = open(filePath, 'rt', encoding = 'utf-8')
                content = f.read()
            if content: # 게시글의 내용이 존재했을 때 작동하는 조건문
                return render_template('edit_post.html', body=content)
            else: # 게시글의 내용이 존재하지 않을 때 작동하는 조건문
                flash('수정할 게시글이 존재하지 않습니다.')
                return redirect(url_for('.index'))
        else:
            flash('로그인을 해주시길 바라겠습니다.')
            return redirect(url_for('auth.login'))
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 게시글 삭제 라우트 & 뷰함수
@main.route('/delete_post/<int:id>')
def delete_post(id):
    try:
        if 'username' in session:
            with db.cursor() as cur:
                cur.execute('select username \
                             from users \
                             where id = (select author_id from posts where id = %s)', (id))

                data = cur.fetchone()

                if data[0] != session['username']:
                    flash('작성한 유저가 아닙니다.')
                    return redirect(request.referrer)

                else:
                    cur.execute('insert into deletepost select * from posts where id=%s', (id))
                    cur.execute('delete from posts where id = %s', (id))
                    cur.execute('update users set post_count = post_count - 1 where username = %s', (data[0]))

            db.commit()
            flash('삭제 완료했습니다.')

            return redirect(request.referrer)
        else:
            flash('로그인이 되지 않았습니다. 로그인 해주세요.')
            return redirect(url_for('auth.login'))
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 게시글의 내용 및 댓글을 다는 라우트 & 뷰함수
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    try:
        if 'username' in session and 'id' in session:
                if request.method == 'POST':
                    if request.form['comment-classfiy'] == 'comment': # 댓글 작성을 처리하는 조건문
                        body = request.form['body'] # 작성한 댓글의 내용을 저장하는 변수
                        with db.cursor() as cur:
                            # 댓글의 내용 및 작성자 그리고 해당 게시글의 id 컬럼 값을 저장하는 삽입 쿼리
                            cur.execute('insert into comments(body, author_id, post_id, groupnum) \
                                        select %s, %s, %s, coalesce(max(groupnum) + 1, 1) from comments', (body, session['id'], id))
                            # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
                            cur.execute('update posts set comment_count = comment_count + 1 \
                                        where id = %d' %(id))

                    elif request.form['comment-classfiy'] == 'recomment': # 답 댓글 작성을 처리하는 조건문
                        parent_id = request.form['parent_id'] # 작성한 답 댓글의 부모 댓글의 id 컬럼 값을 저장한 변수
                        group_id = request.form['group_id']
                        body = request.form['body'] # 작성한 답 댓글의 내용을 저장한 변수
                        with db.cursor() as cur:
                            # 답 댓글의 내용 및 작성자, 게시글 id 컬럼 값 그리고 부모 댓글의 id 컬럼 값을 저장하는 삽입 쿼리
                            cur.execute('insert into comments(body, author_id, post_id, parent, groupnum) values(%s, %s, %s, %s, %s)',
                                        (body, session['id'], id, parent_id, group_id))
                            # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
                            cur.execute('update posts set comment_count = comment_count + 1 \
                                        where id = %d' %(id))

                    else:
                        editCommentId = request.form['editComment_id']
                        body = request.form['body']
                        with db.cursor() as cur:
                            cur.execute('select username from users where id = (select author_id comments where id = %s)', (editCommentId))
                            data = cur.fetchone()

                        if data[0] != session['username']:
                            flash('작성한 유저가 아닙니다.')
                            return redirect(url_for('.post', id = id))

                        with db.cursor() as cur:
                            cur.execute('update comments set body = %s where id = %s', (body, editCommentId))

                    db.commit()
                    return redirect(url_for('.post', id = id))

                # method가 GET 일 시
                with db.cursor() as cur:
                    # 해당 게시글의 정보들 출력하는 검색 쿼리
                    cur.execute('select u.username, u.profile_filename, p.name, p.timestamp, p.comment_count \
                                from (select id, username, profile_filename from users) u \
                                join (select * from posts where id = %s) p \
                                on u.id = p.author_id', (id))
                    posts = cur.fetchall()

                    # 댓글의 수를 다른 변수에다 저장하기.

                    # 해당 게시글의 댓글들의 정보를 출력하는 검색 쿼리
                    cur.execute('select c.id, c.body, c.timestamp, u.username, u.profile_filename, c.groupnum, c.parent \
                                from (select id, author_id, body, timestamp, groupnum, parent from comments where post_id = %s) c \
                                left outer join \
                                (select id, username, profile_filename from users) u \
                                on u.id = c.author_id \
                                order by c.groupnum, c.timestamp', (id))

                    comments = cur.fetchall()

                return render_template('post.html', datas = posts, id = id, comments = comments)
        
        else:
            flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e: # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 댓글 삭제 라우트 & 뷰함수
@main.route('/delComment/<int:comment_id>')
def delComment(comment_id):
    try:
        if 'username' in session:
            with db.cursor() as cur:
                cur.execute('select username from users where id = (select author_id from comments where id = %s)', (comment_id))
                data = cur.fetchone()

            if data[0] != session['username']:
                flash('작성한 유저가 아닙니다.')
                return redirect(request.referrer)

            with db.cursor() as cur:
                cur.execute('select * from comments where id = %s', (comment_id))# 해당 comment_id 값으로 삭제할 댓글의 정보를 검색
                commentData = cur.fetchone()
                cur.execute('insert into delcomments value(%s, %s, %s, %s, %s, %s, %s)', commentData)# 삭제한 댓글을 따로 기록하기 위한 삽입쿼리

                # comments table의 parents column의 값이 0(답 댓글을 달기 위한 최상위 댓글)인지 확인하는 조건문
                if commentData[6] == 0:
                    # 최상위 댓글이면 해당 댓글을 그냥 지우거나 '삭제된 댓글 입니다.'라고 표기하기.
                    cur.execute('select count(id) from comments where post_id=%s and groupnum = %s', (commentData[2], commentData[5]))
                    count = cur.fetchone()

                    # 최상위 댓글에 답 댓글이 달려있는지 확인하는 조건문
                    if count[0] > 1:
                        # 답 댓글이 달려있으면 '삭제된 댓글입니다.'라고 표기하기 위해 변경하는 로직.
                        cur.execute('update comments set author_id=%s, body=%s, timestamp=%s where id=%s', (None, None, None, commentData[0]))

                    else:
                        # 답 댓글이 달려있지 않으면 그냥 삭제(지우기)
                        cur.execute('delete from comments where id=%s', (commentData[0]))
                else:
                    # 답 댓글인 경우 그냥 삭제.
                    cur.execute('delete from comments where id=%s', (comment_id))
            
            db.commit()
            return redirect(url_for('.post', id=commentData[2]))
        
        else:
            flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# /follow_list 페이지에서 팔로우 nav-tab을 클릭할 시 쿠키에 저장하는 라우트 & 뷰함수
@main.route('/follower/<username>')
def follower(username):
    try:
        return redirect(url_for('.follow_list', username = username, jf = 'follow'))
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# /follow_list 페이지에서 팔로잉 nav-tab을 클릭할 시 쿠키에 저장하는 라우트 & 뷰함수
@main.route('/following/<username>')
def following(username):
    try:
        return redirect(url_for('.follow_list', username = username, jf = 'following'))
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# /home 페이지에서 Posts nav-tab을 클릭할 시 쿠케에 저장하는 라우트 & 뷰함수
@main.route('/posts')
def posts():
    try:
        resp = make_response(redirect(url_for('.home')))
        resp.set_cookie('show_page', 'True')
        return resp
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# /home 페이지에서 Users nav-tab을 클릭할 시 쿠케에 저장하는 라우트 & 뷰함수
@main.route('/users')
def users():
    try:
        resp = make_response(redirect(url_for('.home')))
        resp.set_cookie('show_page', '')
        return resp
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)