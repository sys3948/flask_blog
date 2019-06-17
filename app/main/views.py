from flask import abort, current_app, flash, make_response, redirect, render_template, request, session, url_for
from . import main
from .. import db, all_count
from datetime import datetime
import os


# file 저장시에 해당 file의 이름을 문제없이 저장하기 위해 변경해주는 함수
def change_filename(name):
    if ' ' in name:
        name = name.replace(' ', '_')
    return name


# 메인 페이지 라우트 & 뷰함수
@main.route('/', methods = ['GET', 'POST'])
@main.route('/<int:num>', methods = ['GET', 'POST'])
def index(num = 1):
    try:
        if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
            global all_count
            show_follower = False # 전체 게시글 또는 follow한 게시글들을 출력하기 위해 구분하는 변수. True면 팔로우한 게시글 출력 False면 전체 게시글 출력
            rnum = (num - 1) * 10
            if request.method == 'POST': # method가 POST지 확인하는 조건문
                body = request.form['body'] # 작성한 게시글의 내용을 받는 변수
                dt = datetime.now() # 현재 시간
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S') # 현재 시간을 mysql datetime type에 맞게 문자열 포맷팅
                with db.cursor() as cur: # 커서 연결
                    # 작성한 게시글을 posts 테이블에 삽입하기. 삽입하는 데이터는 작성한 게시글의 내용을 저장한 body변수, 현재 로그인한 사용자의 id열 값,
                    # 현재 시간을 문자열 포맷한 timestamp 변수.
                    cur.execute('insert into posts(body, author_id, timestamp) values(%s, %s, %s)', (body, session['id'], timestamp))
                    # 작성한 유저의 게시글 수를 기록한 user_work_count.posts_count 열의 수에서 + 1 하는 update 쿼리문
                    cur.execute('update works_count set posts = posts + 1, follow_posts = follow_posts + 1 \
                                 where id = %s', (session['id']))

                    # 작성한 유저의 팔로워들을 검색하는 쿼리
                    cur.execute('select follower_id from follows where followed_id=%s', (session['id']))
                    followeds_id = cur.fetchall()

                    # followeds_id 변수의 값이 있는지 확인하는 조건문
                    if followeds_id:
                        for followed_id in followeds_id:
                            # 팔로우 한 유저들의 게시글의 수에 + 1 해주는 update 쿼리 문
                            cur.execute('update works_count set follow_posts = follow_posts + 1 \
                                         where id = %s', (followed_id))

                    db.commit() # 위 쿼리들(insert, update) 저장하는 부분
                    all_count = all_count + 1
                flash('작성 완료했습니다.')
                return redirect(url_for('.index')) # 작업이 끝났으면 GET method로 / route로 redirect 한다.
            # method가 GET일 때
            show_follower = bool(request.cookies.get('show_follower')) # 쿠키 'show_follower'의 값으로 전체 게시글 출력인지 follow한 게시글을 출력인지 구분해주는 변수
            with db.cursor() as cur:
                # show_follower변수가 True이면 팔로우한 게시글을 출력하는 조건문
                if show_follower:
                    # Following한 유저들의 Posts를 가져오는 검색 쿼리
                    # posts.id = comments_count.post_id and followers.followed_id = posts.author_id and f.follower_id = u.id
                    cur.execute("set @rownum = 0")
                    cur.execute("select id, body, timestamp, username, profile_filename, count \
                                 from ( \
                                  select @rownum := @rownum +1 as num, b.* \
                                  from ( \
                                   select pc.id, pc.body, pc.timestamp, pc.count, uf.username, uf.profile_filename \
                                   from ( \
                                    select p.*, count(c.id) as count \
                                    from posts p left outer join comments c \
                                    on p.id = c.post_id \
                                    group by p.id \
                                   ) as pc \
                                   join ( \
                                    select u.id, u.username, u.profile_filename \
                                    from users u join follows f \
                                    on u.id = f.followed_id \
                                    where f.follower_id = %s \
                                   ) as uf \
                                   on pc.author_id = uf.id \
                                   order by pc.timestamp desc \
                                  ) as b \
                                 ) as board \
                                 where num >= %s \
                                 limit 10", (session['id'], rnum)) #num은 해당 페이지의 시작 값

                    posts = cur.fetchall() # 게시글의 값을 저장하는 변수

                    # 로그인한 유저의 follow한 게시글들의 수를 출력하는 검색 쿼리
                    cur.execute('select follow_posts from works_count where id = %s', (session['id']))
                    selected_num = cur.fetchone() # 위의 검색 쿼리의 값을 저장하는 변수
                    paging = selected_num[0]//10 # 페이지의 수를 계산하는 변수(10개의 게시글들을 한 페이지에 출력하는 페이지에서 페이지의 수를 계산하는 변수)
                    if selected_num[0] % 10 > 0: # 10으로 나누어 나머지가 존재하면 페이지의 수 + 1를 하는 조건문
                        paging = paging + 1

                else: # 팔로우한 게시글이 아닌 전체 게시글을 출려하는 조건문(else 문)
                    # 전체 Posts를 가져오기
                    # posts join users join comments_count
                    # on posts.author_id = users.id and posts.id = comments_count.post_id
                    cur.execute("set @rownum = 0")
                    cur.execute("select id, body, timestamp, username, profile_filename, count \
                                 from ( \
                                  select @rownum := @rownum + 1 as num, b.* \
                                  from ( \
                                   select pc.id, pc.body, pc.timestamp, pc.count, u.username, u.profile_filename \
                                   from ( \
                                    select p.*, count(c.id) as count \
                                    from posts p left outer join comments c \
                                    on p.id = c.post_id \
                                    group by p.id\
                                   ) as pc join users u \
                                   on pc.author_id = u.id \
                                   order by pc.timestamp desc\
                                  ) as b \
                                 ) as board \
                                 where num >= %s \
                                 limit 10", (rnum)) #num은 해당 페이지의 글 번호의 시작값

                    posts = cur.fetchall() # 위 검색 쿼리의 값을 저장하는 변수

                    paging = all_count//10
                    if all_count % 10 > 0: # 10으로 나누어 나머지가 존재하면 페이지의 수 + 1를 하는 조건문
                        paging = paging + 1

        else: # 로그인이 되지 않는 상태의 조건문(else 문)
            return redirect(url_for('auth.login')) # 로그인 페이지로 이동
    except Exception as e: # 예상치 못 한 Error가 발생할 시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


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
                        password = request.form['password']
                        cur.execute('update users set password_hash=sha2(%s, 224) where username=%s', (password, session['username']))
                        db.commit()
                    else: # 존재하지 않는다면 비밀번호 변경 페이지로 리다이렉트 한다.
                        flash('Old Password(현재 비밀번호)가 맞지 않습니다. 다시 입력해주세요.')
                        return redirect(url_for('.change_pw'))
                    flash('비밀번호 변경이 성공했습니다.')
                    return redirect(url_for('.index'))
            except Exception as e: # 예상치 못한 Error가 발생했을 시 처리하는 except문
                flash(str(e) + '라는 문제가 발생했습니다.')
                abort(500)

        return render_template('change_password.html')
    else:
        flash('로그인이 되어있지 않아 비밀번호 변경을 못 합니다. 로그인을 해주세요.')
        return redirect(url_for('.index'))


# 프로필 페이지의 라우트 & 뷰함수
@main.route('/profile/<username>')
@main.route('/profile/<username>/<int:num>')
def profile(username, num = 1):
    try:
        if 'username' in session and 'id' in session:
            rnum = (num - 1) * 10 # limit offset의 값을 지정하는 변수
            show_follow = False # Follow or Unfollow 버튼 활성화를 하기 위한 변수
            with db.cursor() as cur:
                # 해당 프로필의 username에 해당하는 사용자 정보를 출력하는 검색 쿼리
                cur.execute('select u.location, u.about_me, u.member_since, u.profile_filename, w.posts, w.comments \
                            from users u join works_count w\
                            on u.id = w.id \
                            where u.username = %s', (username))
                select_data = cur.fetchone()
                if not select_data: # 검색한 쿼리의 값이 존재하지 않는다면 메인 페이지로 리다이렉트 하는 조건문
                    flash('존재하지 않는 사용자 닉네임입니다.')
                    return redirect(url_for('.index'))

                # 팔로워 수와 팔로잉 한 수를 찾는 검색쿼리
                cur.execute('select followed, following from follows_count \
                            where user_id = (select id from users where username=%s)', (username))
                count = cur.fetchone()

                if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인 하는 조건문
                    # 로그인이 되어있으면 해당 session값과 username 값을 이용하여 로그인한 유저가 해당 프로파일의 유저를 팔로우 했는지 확인하는 검색 쿼리
                    cur.execute('select followed_id from follows \
                                where followed_id = (select id from users where username = %s) \
                                and follower_id = %s', (username, session['id']))
                    follow_activation = cur.fetchone()
                    if follow_activation: # 해당 변수 값이 존재하면 팔로우를 했다는 의미이다.
                        show_follow = True
                    else: # 존재하지 않으면 팔로우를 안 했다는 의미이다.
                        show_follow = False

                # 해당 프로필의 유저가 작성한 게시글 10개를 출력하는 검색 쿼리
                cur.execute("set @rownum := 0")
                cur.execute("select id, body, timestamp, username, profile_filename, count\
                            from ( \
                            select @rownum := @rownum + 1 as num, b.* \
                            from ( \
                            select pc.id, pc.body, pc.timestamp, pc.count, u.username, u.profile_filename \
                            from ( \
                                select p.*, count(c.id) as count \
                                from posts p left outer join comments c \
                                on p.id = c.post_id \
                                group by p.id \
                            ) as pc join users u \
                            on pc.author_id = u.id \
                            where u.username = %s \
                            order by pc.timestamp desc \
                            ) as b \
                            ) as board \
                            where num > %s \
                            limit 10", (username, rnum)) #num은 해당 페이지의 게시글 시작하는 수이다.

                posts = cur.fetchall()

                # 해당 프로필의 페이징 작업을 위해 해당 프로필의 유저의 pagination.my_posts_count 열을 출력하는 검색 쿼리
                cur.execute('select posts from works_count where id=(select id from users where username = %s)', (username))
                selected_num = cur.fetchone()
                paging = selected_num[0]//10
                if selected_num[0] % 10 > 0:
                    paging = paging + 1
        
        else:
            flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e: # 예상치 못한 에러를 처리하는 except문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)

    return render_template('profile.html', profile_user = username, location = select_data[0], about_me = select_data[1],
                            member_since = select_data[2], image_name = select_data[3], posts_count = select_data[4],
                            comments_count = select_data[5], show_follow = show_follow, followers_count = count[0],
                            following_count = count[1], posts = posts, paging = paging, current_page = num, url = 'profile/' + username)


# 프로필 수정 라우트 & 뷰함수
@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
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
                        # 해당 파일이 존재하지 않는다면 아래를 처리한다.
                        try:
                            with db.cursor() as cur:
                                # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                                cur.execute('update users set username=%s, location=%s, about_me=%s, profile_filename=%s where username=%s', \
                                    (username, location, about_me, filename, session['username']))
                                #  해당 파일을 저장하는 디렉토리에다 저장하기
                                profile_img.save(os.path.join(current_app.config['UPLOAD_FOLDERS'], filename))
                                db.commit()
                        except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
                            flash(str(e) + '라는 문제가 발생했습니다.')
                            abort(500)

                    else:
                        # 파일이 존재한다면 아래로 처리한다.
                        try:
                            with db.cursor() as cur:
                                # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                                cur.execute('update users set username=%s, location=%s, about_me=%s, profile_filename=%s where username=%s', \
                                    (username, location, about_me, filename, session['username']))
                                db.commit()
                        except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
                            flash(str(e) + '라는 문제가 발생했습니다.')
                            abort(500)

                    flash('프로필이 수정되었습니다.')
                    session['username'] = username
                else: # 파일이 확장자 또는 '.'이 존재하지 않을 때 처리하는 조건문(else 문)
                    flash('이미지 파일이 맞지 않아 프로필 수정을 실패합니다.')
                    
                return redirect(url_for('.profile', username = session['username']))
            else: # 파일이 존재하지 않을 경우에 해당하는 조건문
                try:
                    with db.cursor() as cur:
                        # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                        cur.execute('update users set username=%s, location=%s, about_me=%s where username=%s', \
                                    (username, location, about_me, session['username']))
                        db.commit()
                except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
                    flash(str(e) + '라는 문제가 발생했습니다.')
                    abort(500)

                flash('프로필이 수정되었습니다.')
                session['username'] = username
                return redirect(url_for('.profile', username = session['username']))
        # method가 GET일 때
        try:
            with db.cursor() as cur:
                # 로그인 한 유저의 정보를 출력하기 위한 검색 쿼리
                cur.execute('select location, about_me, profile_filename from users where username=%s',(session['username']))
                selected_data = cur.fetchone()
        except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
            flash(str(e) + '라는 문제가 발생했습니다.')
            abort(500)

        return render_template('edit_profile.html', username = session['username'], location = selected_data[0], \
                               about_me = selected_data[1], image_name = selected_data[2])
    else:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 팔로우를 하는 것에 해당하는 라우트 & 뷰함수
@main.route('/follow/<username>')
def follow(username):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                # 해당 username과 로그인 한 유저의 id 값을 followers 테이블에 삽입하는 쿼리.
                cur.execute('insert into follows(follower_id, followed_id) \
                            select u1.id, u2.id from (select %s as id) u1 join (select id from users where username=%s) u2', 
                            (session['id'], username))
                # 해당 username의 follower의 수를 증가하는 update 쿼리
                cur.execute('update follows_count set followed = followed + 1 \
                            where user_id = (select id from users where username = %s)', (username))
                # 로그인한 유저의 following의 수를 증가하는 update 쿼리
                cur.execute('update follows_count set following = following + 1 \
                            where user_id = %d' %(session['id']))

                # username이 작성한 posts의 수를 검색하는 쿼리
                cur.execute('select posts from works_count where id = (select id from users where username = %s)', (username))
                posts_count = cur.fetchone()

                if posts_count[0] > 0: # 위 검색 쿼리의 값이 0보다 크면 처리하는 조건문
                    # 로그인 한 유저의 팔로우 게시글의 수를 username의 작성한 게시글의 수만큼 증가하는 update 쿼리
                    cur.execute('update works_count set follow_posts = follow_posts + %s \
                                 where id = %s', (posts_count[0], session['id']))

            db.commit()
            flash('팔로우 했습니다.')
        else:
            flash('로그인이 되지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)
    
    return redirect(url_for('.index'))


# 언팔로우 하는 것에 해당하는 라우트 & 뷰함수
@main.route('/unfollow/<username>')
def unfollow(username):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                # 해다 username을 언팔로우 하니 로그인한 유저의 followers 테이블에서 제거하는 쿼리
                cur.execute('delete from follows where follower_id = %s and followed_id = (select id from users where username = %s)',
                             (session['id'], username))

                # username에 해당하는 유저의 팔로워 수를 감소하는( - 1) update 쿼리
                cur.execute('update follows_count set followed = followed - 1 \
                            where user_id = (select id from users where username = %s)', (username))
                
                # 로그인 한 유저의 팔로잉 수를 감소하는( - 1) update 쿼리
                cur.execute('update follows_count set following = following - 1 \
                            where user_id = %d' %(session['id']))

                # username이 작성한 게시글들의 수를 출력하는 검색 쿼리
                cur.execute('select posts from works_count where id = (select id from users where username = %s)', (username))
                posts_count = cur.fetchone()

                if posts_count[0] > 0: # 위 검색 쿼리의 값이 0 이상이면 그 수만큼 로그인한 유저의 팔로잉 게시글의 수를 감소하는 update 쿼리
                    cur.execute('update works_count set follow_posts = follow_posts - %s \
                                 where id = %s', (posts_count[0], session['id']))

            db.commit()
            flash('언팔로우 했습니다.')
        else:
            flash('로그인 되지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)
    
    return redirect(url_for('.index'))


# 팔로워들의 목록을 보는 라우트 & 뷰함수
@main.route('/followers/<username>')
def followers(username):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                # 해당 username의 팔로워들의 정보를 출력하기 위한 검색 쿼리
                cur.execute('select u.username, u.profile_filename, f.timestamp \
                            from users u join follows f \
                            on u.id = f.follower_id \
                            where f.followed_id = (select id from users where username = %s) \
                            and f.follower_id != (select id from users where username = %s) \
                            order by f.timestamp desc', (username, username))
                follower_datas = cur.fetchall()

        else:
            flash('로그인 되지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

        return render_template('followers.html', username = username, follow_kind = 'Followers',
                                follow_datas = follower_datas)
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 해당 유저가 팔로잉한 유저들의 목록을 보는 라우트 & 뷰함수
@main.route('/following/<username>')
def following(username):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                # username이 팔로잉을 한 유저들의 정보를 출력하는 검색 쿼리
                cur.execute('select u.username, u.profile_filename, f.timestamp \
                            from users u join follows f \
                            on u.id = f.followed_id \
                            where f.follower_id = (select id from users where username = %s) \
                            and f.followed_id != (select id from users where username = %s) \
                            order by f.timestamp desc', (username, username))
                follower_datas = cur.fetchall()

        else:
            flash('로그인 되지 않는 상태입니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

        return render_template('followers.html', username = username, follow_kind = 'Following',
                                follow_datas = follower_datas)
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 게시글 수정 라우트 & 뷰함수
@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                if request.method == 'POST':
                    body = request.form['body']
                    # Client에서 입력한 값으로 수정하는 update 쿼리
                    cur.execute('update posts set body=%s where id=%s', (body, id))
                    db.commit()
                    return redirect(url_for('.index'))
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
                return redirect(url_for('.index'))
        else:
            flash('로그인을 해주시길 바라겠습니다.')
            return redirect(url_for('auth.login'))
    except Exception as e: # 예상치 못 한 Error가 발생시 처리하는 except 문
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 게시글의 내용 및 댓글을 다는 라우트 & 뷰함수
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    try:
        if 'username' in session and 'id' in session:
            with db.cursor() as cur:
                if request.method == 'POST':
                    if request.form['comment-classfiy'] == 'comment': # 댓글 작성을 처리하는 조건문
                        body = request.form['body'] # 작성한 댓글의 내용을 저장하는 변수
                        # 댓글의 내용 및 작성자 그리고 해당 게시글의 id 컬럼 값을 저장하는 삽입 쿼리
                        cur.execute('insert into comments(body, author_id, post_id, groupnum) \
                                    select %s, %s, %s, coalesce(max(groupnum) + 1, 1) from comments', (body, session['id'], id))
                        # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
                        cur.execute('update works_count set comments = comments + 1 \
                                    where id = %d' %(session['id']))

                    else: # 답 댓글 작성을 처리하는 조건문
                        parent_id = request.form['parent_id'] # 작성한 답 댓글의 부모 댓글의 id 컬럼 값을 저장한 변수
                        group_id = request.form['group_id']
                        print(group_id)
                        body = request.form['body'] # 작성한 답 댓글의 내용을 저장한 변수
                        # 답 댓글의 내용 및 작성자, 게시글 id 컬럼 값 그리고 부모 댓글의 id 컬럼 값을 저장하는 삽입 쿼리
                        cur.execute('insert into comments(body, author_id, post_id, parent, groupnum) values(%s, %s, %s, %s, %s)',
                                    (body, session['id'], id, parent_id, group_id))
                        # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
                        cur.execute('update works_count set comments = comments + 1 \
                                    where id = %d' %(session['id']))

                    db.commit()
                    return redirect(url_for('.post', id = id))

                # method가 GET 일 시
                # 해당 게시글의 정보들 출력하는 검색 쿼리
                cur.execute('select pc.id, pc.body, pc.timestamp, u.username, u.profile_filename, pc.count \
                            from ( \
                            select p.id, p.body, p.timestamp, p.author_id, count(c.id) as count \
                            from posts p left outer join comments c \
                            on p.id = c.post_id \
                            where p.id = %s \
                            group by p.id \
                            ) as pc join users u \
                            on pc.author_id = u.id', (id))
                posts = cur.fetchall()

                # 해당 게시글의 댓글들의 정보를 출력하는 검색 쿼리
                cur.execute('select c.id, c.body, c.timestamp, u.username, u.profile_filename, c.groupnum, c.parent \
                            from comments as c join users as u \
                            on c.author_id = u.id \
                            where post_id = %s \
                            order by groupnum, timestamp', (id))

                comments = cur.fetchall()

                return render_template('post.html', posts = posts, comments = comments)
        
        else:
            flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e: # 작성자(로그인한 유저)가 댓글을 작성했으니 작성자가 작성한 댓글의 수를 증가( + 1)를 해주는 update 쿼리
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# 전체 게시글들을 선택할 시 쿠키에 저장하는 라우트 & 뷰함수
@main.route('/all')
def all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_follower', '')
    return resp


# 팔로우한 게시글들을 선택할 시 쿠키에 저장하는 라우트 & 뷰함수
@main.route('/followed')
def followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_follower', 'True')
    return resp