from flask import abort, current_app, flash, make_response, redirect, render_template, request, session, url_for
from . import main
from .. import db
from ..models import User, Post, Comment, Follow, DeleteComment, DeletePost
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from .file_func import change_filename, create_file
import os


# 메인 페이지 라우트 & 뷰함수
@main.route('/')
def transmit_index():
    if 'username' in session and 'id' in session:
        # 로그인이 되어있으면 메인 페이지로 리다이렉션
        return redirect(url_for('.index', username = session['username']))
    else:
        # 로그인이 되어있지 않으면 로그인 페이지로 리다이렉션
        flash('로그인을 해주세요.')
        return redirect(url_for('auth.login'))

# 메인 페이지의 라우트 & 뷰함수
@main.route('/<username>', methods = ['GET', 'POST'])
@main.route('/<username>/<int:num>', methods = ['GET', 'POST'])
def index(username, num = 1):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        if session['username'] == username:
            # 해당 유저와 로그인 한 유저가 같은경우 유저의 메인 페이지로 접속.
            user = User.query.filter_by(username = username).first_or_404() # 해당 유저의 유저 이름이 존재하지 않으면 404 에러를 발생

            if request.method == 'POST': # method가 POST지 확인하는 조건문
                # 게시글 검색을 했을 경우
                search = request.form['search']
                # pagination = Post.query.join(User, Post.author_id == User.id).join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == user.id, or_(Post.body_text.like("%{}%".format(search)), User.username.like("%{}%".format(search)))).order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)
                pagination = Post.query.join(Follow, Follow.followed_id == Post.author_id).\
                             filter(Follow.follower_id == user.id, \
                                    or_(Post.body_text.like("%{}%".format(search)), \
                                        User.username.like("%{}%".format(search)))). \
                             order_by(Post.timestamp.desc()).paginate(page = 1, per_page = 10, error_out = True)

                # GET method일 시에 해당 검색한 결과의 게시글을 출력하기 위한 page url을 저장하는 변수(url에는 검색 값, 총 페이지 수 등의 값이 저장되어있다.)
                pageUrl = url_for('.index', username = username, search = True, result = search, paging = pagination.pages)

                return render_template('index.html', username = username, datas = pagination.items, paging = pagination.pages,
                                        current_page = num, pageUrl = pageUrl, checkSearch = True)

            # method가 GET일 때
            if request.args.get('search'):
                # 검색한 결과의 게시글을 볼 경우
                num = int(request.args.get('paging').split('/')[1]) # 현제 페이지를 저장하는 변수
                paging = int(request.args.get('paging').split('/')[0]) # 총 페이지 수를 저장하는 변수
                search = request.args.get('result') # 검색 값을 저장한 변수
                # 검색 값에 맞는 게시글들을 출력하는 검색 쿼리
                # pagination = Post.query.join(User, Post.author_id == User.id).join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == user.id, or_(Post.body_text.like("%{}%".format(search)), User.username.like("%{}%".format(search)))).order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)
                pagination = Post.query.join(Follow, Follow.followed_id == Post.author_id). \
                             filter(Follow.follower_id == user.id, or_(Post.body_text.like("%{}%".format(search)), \
                                                                       User.username.like("%{}%".format(search)))). \
                             order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

                # 해당 검색한 결과의 다음 게시글들을 출력하기 위한 page url을 저장하는 변수(url에는 검색 값, 총 페이지 수 등의 값이 저장되어있다.)
                pageUrl = url_for('.index', username = username, search = True, result = search, paging = paging)
                        
            else:
                # 게시글을 볼 경우
                # 게시글을 출력하는 검색 쿼리
                # pagination = Post.query.join(User, Post.author_id == User.id).join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == user.id).order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)
                pagination = Post.query.join(Follow, Follow.followed_id == Post.author_id).\
                             filter(Follow.follower_id == user.id). \
                             order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

                # 전체 게시글에서 다음 게시글을 출력하기 위한 page url을 저장하는 변수
                pageUrl = url_for('.index', username = username)

            posts = pagination.items
                    
            return render_template('index.html', username = username, datas = posts, paging = pagination.pages, current_page = num,
                                    pageUrl = pageUrl, checkSearch = True)

        else:
            # 같지 않는 경우 프로필 페이지로 리다이렉션
            return redirect(url_for('.profile', username = username))

    else: # 로그인이 되지 않는 상태의 조건문(else 문)
        flash('로그인을 해주세요.')
        return redirect(url_for('auth.login')) # 로그인 페이지로 이동


# home 라우트 & 뷰함수
@main.route('/home', methods = ['GET', 'POST'])
@main.route('/home/<int:num>', methods = ['GET', 'POST'])
def home(num = 1):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문

        # 게시글 목록을 보여줄 지 유저 목록을 보여줄 지 정하는 조건문
        show_page = True
        if request.cookies.get('show_page') == '':
            show_page = False # 전체 유저 목록을 보여주기
        else:
            show_page = True # 전체 게시글들을 보여주기

        # POST 일 시(검색)
        if request.method == 'POST':
            search = request.form['search']
            if show_page:
                # 게시글 검색(조인 조건으로 수정해야한다.)
                pagination = Post.query.join(User, Post.author_id == User.id).\
                             filter(or_(Post.body_text.like("%{}%".format(search)), \
                                        User.username.like("%{}%".format(search)))). \
                             order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

                datas = pagination.items

                # 검색한 게시글 목록에서 다음 게시글 목록을 보기 위한 url을 저장한 변수
                url = url_for('.home', search = True, result = search, paging = pagination.pages)

                return render_template('home.html', datas = datas, paging = pagination.pages, show_page = show_page, current_page = num,
                                        pageUrl = url, checkSearch = True)
            else:
                # 유저 검색
                login_user = User.query.filter_by(username = session['username']).first()
                pagination = User.query.filter(User.username.like("%{}%".format(search))). \
                             order_by(User.username, User.member_since.desc()).paginate(page = num, per_page = 10, error_out = True)

                datas = pagination.items

                # 검색한 유저 목록에서 다음 유저 목록을 보기 위한 url을 저장한 변수
                url = url_for('.home', search = True, result = search, paging = pagination.pages)

                return render_template('home.html', datas = datas, paging = pagination.pages, show_page = show_page, current_page = num,
                                        pageUrl = url, login_user = login_user)

        # GET일 시
        if show_page:
            # 게시글을 볼 때
            if request.args.get('search'):
                # 검색한 게시글 목록(조인 조건으로 수정해야한다.)

                search = request.args.get('result') # 검색 값을 저장한 변수
                paging = request.args.get('paging').split('/')[0] # 총 페이지 수를 저장한 변수
                num = int(request.args.get('paging').split('/')[1]) # 현재 페이지를 저장한 변수
                url = url_for('.home', search = True, result = search, paging = paging) # 다음 게시글들을 보기 위한 url을 저장한 변수

                # 검색한 게시글 목록
                pagination = Post.query.filter(or_(Post.body_text.like("%{}%".format(search)), \
                                                   User.username.like("%{}%".format(search)))). \
                             order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)
            else:
                # 전체 게시글 목록
                pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

                url = url_for('.home')

            datas = pagination.items

            return render_template('home.html', datas = datas, paging = pagination.pages, show_page = show_page, current_page = num,
                                    pageUrl = url, checkSearch = True)

        else:
            # 유저 목록을 볼 때
            login_user = User.query.filter_by(username = session['username']).first()
            if request.args.get('search'):
                # 검색한 유저 목록
                search = request.args.get('result') # 검색 값을 저장한 변수
                paging = request.args.get('paging').split('/')[0] # 총 페이지 수를 저장한 변수
                num = int(request.args.get('paging').split('/')[1]) # 현제 페이지를 저장한 변수
                url = url_for('.home', search = True, result = search, paging = paging) # 다음 유저 목록들을 보기 위한 url을 저장한 변수(검색)

                # 검색한 유저 목록을 출력하는 쿼리문
                pagination = User.query.filter(User.username.like("%{}%".format(search))). \
                             order_by(User.username.asc()).paginate(page = num, per_page = 10, error_out = True)
            else:
                # 전제 유저 목록
                pagination = User.query.order_by(User.username, User.member_since.desc()).paginate(page = num, per_page = 10, error_out = True)

                url = url_for('.home') # 다음 유저 목록들을 보기 위한 url을 저장한 변수(전체)

            datas = pagination.items

            return render_template('home.html', datas = datas, paging = pagination.pages, show_page = show_page, current_page = num,
                                    pageUrl = url, login_user = login_user)

    else:
        flash('로그인을 해주세요.')
        return redirect(url_for('auth.login'))


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
            old_password_hash = db.session.query(func.sha2(old_password, 224))
            user = User.query.filter_by(username = session['username'], password_hash = old_password_hash).first_or_404()

            password = request.form['password'] # 변경할 비밀번호
            password2 = request.form['password2'] # 변경할 비밀번호를 확인하기 위한 두 번째 비밀번호
            if password != password2:
                # 변경할 두개의 비밀번호가 맞지 않을 경우
                flash('변경하실 비밀번호와 비밀번호 확인 값이 맞지 않습니다. 다시 입력해주세요.')
                return redirect(url_for('.change_pw'))

            # 두개의 비밀번호가 맞는 경우
            password_hash = db.session.query(func.sha2(password, 224)) # 비밀번호 해쉬
            user.password_hash = password_hash # 비밀번호 변경
            db.session.commit()
            flash('비밀번호 변경이 성공했습니다.')
            return redirect(url_for('.index', username = session['username']))
            
        return render_template('change_password.html')
    else:
        flash('로그인이 되어있지 않아 비밀번호 변경을 못 합니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 프로필 페이지의 라우트 & 뷰함수
@main.route('/profile/<username>', methods = ['GET', 'POST'])
@main.route('/profile/<username>/<int:num>', methods = ['GET', 'POST'])
def profile(username, num = 1):
    if 'username' in session and 'id' in session: # 로그인 되었는지 확인하는 조건문
        show_follow = False # Follow or Unfollow 버튼 활성화를 하기 위한 변수
        user = User.query.filter_by(username = username).first_or_404()

        if user.username != session['username']:
            # 로그인한 유저의 프로필이 아닌 경우 로그인한 유저가 팔로우를 했는지 않했는지 확인하는 부분
            follow = Follow.query.filter_by(followed_id = user.id, follower_id = session['id']).first()

            if follow:
                # 팔로우를 한 경우
                show_follow = True
            else:
                # 팔로우를 하지 않는 경우
                show_follow = False

        if request.method == 'POST':
            # 게시글 검색을 시작하는 부분
            search = request.form['search']

            pagination = user.posts.filter(Post.body_text.like('%{}%'.format(search))). \
                         order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

            pageUrl = url_for('.profile', username = username, search = True, result = search, paging = pagination.pages)

            return render_template('profile.html', profile_user = username, location = user.location, about_me = user.about_me,
                                    member_since = user.member_since, image_name = user.profile_filename, posts_count = user.post_count,
                                    show_follow = show_follow, followers_count = user.follow_count, following_count = user.following_count,
                                    datas = pagination.items, paging = pagination.pages, current_page = num, url = pageUrl, checkSearch = True)

        if request.args.get('search'):
            # 검색한 게시글 목록
            num = int(request.args.get('paging').split('/')[1]) # 현제 페이지를 저장하는 변수
            paging = int(request.args.get('paging').split('/')[0]) # 총 페이지 수를 저장하는 변수
            search = request.args.get('result') # 검색 값을 저장한 변수

            # 검색 값에 따른 게시글 검색 쿼리
            pagination = user.posts.filter(Post.body_text.like('%{}%'.format(search))). \
                         order_by(Post.timestamp.desc()).paginate(page=num, per_page = 10, error_out = True)

            # 해당 페이지의 url
            pageUrl = url_for('.index', username = username, search = True, result = search, paging = request.args.get('paging'))

            posts = pagination.items # 검색한 게시글들
        else:
            # 전체 게시글 목록

            # 프로필의 유저가 작성한 게시글 검색 쿼리
            pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

            posts = pagination.items # 게시글들

            pageUrl = url_for('.profile', username = username) # 해당 페이지의 url

        return render_template('profile.html', profile_user = username, location = user.location, about_me = user.about_me,
                               member_since = user.member_since, image_name = user.profile_filename, posts_count = user.post_count,
                               show_follow = show_follow, followers_count = user.follow_count, following_count = user.following_count,
                               profile_id = user.id, datas = posts, paging = pagination.pages, current_page = num, url = pageUrl, checkSearch = True)
        
    else:
        # 로그인이 되어있지 않는 경우
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 프로필 수정 라우트 & 뷰함수
@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        user = User.query.filter_by(username = session['username']).first_or_404()
        if request.method == 'POST': # method가 POST일 때의 조건문

            username = request.form['username'] # Client에서 입력한 username의 값을 저장하는 변수

            if not username.strip():
                # 닉네임에 공백만 입력된 경우.
                flash('닉네임이 작성되어있지 않습니다. 다시 작성해주세요.')
                return redirect(url_for('.edit_profile'))
                    
            location = request.form['location'] # Client에서 입력한 location의 값을 저장하는 변수
            about_me = request.form['about_me'].strip() # Client에서 입력한 about_me의 값을 저장하는 변수 이 값은 textarea 값이라 빈 공백이 많아 앞 뒤 공백을 제거 했다.

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
                        user.username = username
                        user.location = location
                        user.about_me = about_me
                        user.profile_filename = filename
                        profile_img.save(os.path.join(current_app.config['UPLOAD_FOLDERS'], filename))

                    else:
                        # 파일이 존재한다면 아래로 처리한다.
                        # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                        user.username = username
                        user.location = location
                        user.about_me = about_me
                        user.profile_filename = filename

                    db.session.commit()
                    flash('프로필이 수정되었습니다.')
                    session['username'] = username
                else: # 파일이 확장자 또는 '.'이 존재하지 않을 때 처리하는 조건문(else 문)
                    flash('이미지 파일이 맞지 않아 프로필 수정을 실패합니다.')
                                
                    return redirect(url_for('.profile', username = session['username']))
            else: 
                # 파일이 존재하지 않을 경우에 해당하는 조건문
                # Client에서 입력한 내용을 users 테이블에 update하는 쿼리
                user.username = username
                user.location = location
                user.about_me = about_me
                db.session.commit()

                flash('프로필이 수정되었습니다.')
                session['username'] = username
            return redirect(url_for('.profile', username = session['username']))

        # method가 GET일 때

        return render_template('edit_profile.html', username = user.username, location = user.location,
                                about_me = user.about_me, image_name = user.profile_filename)
    else:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 팔로우를 하는 것에 해당하는 라우트 & 뷰함수
@main.route('/follow/<username>')
def follow(username):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        if username != session['username']:
            # 팔로우 하기
            login_user = User.query.filter_by(username = session['username']).first() # 로그인한 유저
            user = User.query.filter_by(username = username).first() # 팔로우 할 유저
            login_user.follow(user)
            login_user.following_count = login_user.following_count + 1
            user.follow_count = user.follow_count + 1
            db.session.commit()
            flash('팔로우 했습니다.')

        else:
            flash('본인입니다.')
    else:
        flash('로그인이 되지 않는 상태입니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))

    return redirect(request.referrer)


# 언팔로우 하는 것에 해당하는 라우트 & 뷰함수
@main.route('/unfollow/<username>')
def unfollow(username):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        if username != session['username']:
            # 언팔로우 하기
            login_user = User.query.filter_by(username = session['username']).first() # 로그인한 유저
            user = User.query.filter_by(username = username).first() # 언팔로우 할 유저
            login_user.unfollow(user)
            login_user.following_count = login_user.following_count - 1
            user.follow_count = user.follow_count - 1
            db.session.commit()
            flash('언팔로우 했습니다.')

        else:
            flash('본인입니다.')
        
        return redirect(request.referrer)
    else:
        flash('로그인 되지 않는 상태입니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 팔로워들 또는 팔로잉을 한 유저들의 목록을 보는 라우트 & 뷰함수
@main.route('/follow_list/<username>', methods=['GET', 'POST'])
@main.route('/follow_list/<username>/<jf>', methods=['GET', 'POST'])
@main.route('/follow_list/<username>/<jf>/<int:num>', methods=['GET', 'POST'])
def follow_list(username, jf = 'follow', num = 1):
    # 해당 username의 팔로우와 팔로잉
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문

        if jf == 'follow':
            # 팔로워 목록을 볼 경우
            show_follow = True
        elif jf == 'following':
            # 팔로잉 목록을 볼 경우
            show_follow = False
        else:
            return redirect(url_for('.follow_list', username = username, jf = 'follow'))

        login_user = User.query.filter_by(username = session['username']).first() # 로그인 한 유저
        user = User.query.filter_by(username = username).first() # 해당 페이지 유저

        if request.method == 'POST':
            search = request.form['search']
            if show_follow:
                # 팔로우 부분
                pagination = User.query.join(Follow, Follow.follower_id == User.id). \
                             filter(Follow.followed_id == user.id, Follow.follower_id != user.id, \
                                    User.username.like("%{}%".format(search))). \
                             order_by(Follow.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)
            else:
                # 팔로잉 부분
                pagination = User.query.join(Follow, Follow.followed_id == User.id). \
                             filter(Follow.follower_id == user.id, Follow.followed_id != user.id, \
                                    User.username.like("%{}%".format(search))). \
                             order_by(Follow.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

            # 해당 페이지 url
            url = url_for('.follow_list', username = username, jf = jf, search = True, result = search, paging = pagination.pages)

            follow_datas = pagination.items # 유저 목록

            return render_template('followers.html', username = username, show_follow = show_follow, datas = follow_datas, paging = pagination.pages,
                                    current_page = num, pageUrl = url, login_user = login_user)

        # method GET
        if show_follow:
            # 팔로우 부분
            if request.args.get('search'):
                # 검색한 팔로워 목록 결과 쿼리
                num = int(request.args.get('paging').split('/')[1]) # 현제 페이지 넘버
                pagination = User.query.join(Follow, Follow.follower_id == User.id). \
                             filter(Follow.followed_id == user.id, Follow.follower_id != user.id, \
                                    User.username.like("%{}%".format(request.args.get('result')))). \
                             order_by(Follow.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)
                
            else:
                # 검색하지 않은 팔로워 목록 쿼리
                pagination = User.query.join(Follow, Follow.follower_id == User.id). \
                             filter(Follow.followed_id == user.id, Follow.follower_id != user.id). \
                             paginate(page = num, per_page = 10, error_out = True)

        else:
            # 팔로잉 부분
            if request.args.get('search'):
                # 검색한 팔로잉 목록 결과 쿼리
                num = int(request.args.get('paging').split('/')[1]) # 현제 페이지 넘버
                pagination = User.query.join(Follow, Follow.followed_id == User.id). \
                             filter(Follow.follower_id == user.id, Follow.followed_id != user.id, \
                                    User.username.like("%{}%".format(request.args.get('result')))). \
                             order_by(Follow.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

            else:
                # 검색하지 않는 일반 팔로잉 목록 쿼리
                pagination = User.query.join(Follow, Follow.followed_id == User.id). \
                             filter(Follow.follower_id == user.id, Follow.followed_id != user.id). \
                             order_by(Follow.timestamp.desc()).paginate(page = num, per_page = 10, error_out = True)

        # 해당 페이지 별 url 구현 하기.
        if request.args.get('paging'):
            url = url_for('.follow_list', username = username, jf = jf, search = request.args.get('search'), \
                          result = request.args.get('result'), paging = request.args.get('paging').strip('/')[0])
        else:
            url = url_for('.follow_list', username = username, jf = jf)

        return render_template('followers.html', username = username, show_follow = show_follow, datas = pagination.items, paging = pagination.pages,
                                current_page = num, pageUrl = url, login_user = login_user)
    else:
        flash('로그인이 되어있지 않는 상태입니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 게시글 수정 라우트 & 뷰함수
@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문

        post = Post.query.filter_by(id = id).first_or_404() # 수정할 게시글 검색 쿼리 존재하지 않을 시 404 에러 발생

        if request.method == 'POST':
            # method가 POST일 시(submit을 할 시) 게시글 수정하기.
            body = request.form['body']
            body_text = request.form['searchBody']

            filePath = current_app.config['UPLOAD_POST_PATH_DEFAULT'] + post.name # 수정할 파일의 경로 /app/templates/postFiles/id value/파일 명

            # 파일 수정
            f = open(filePath, 'wt', encoding = 'utf-8')
            f.write(body)
            f.close()

            # 검색 컬럼 값 update
            post.body_text = body_text
            db.session.commit()

            return redirect(url_for('.index', username = session['username']))
            
        if post.author.username != session['username']:
            flash('수정하는 게시글의 작성한 유저가 아닙니다.')
            return redirect(request.referrer)
                
        filePath = current_app.config['UPLOAD_POST_PATH_DEFAULT'] + post.name

        # 수정할 게시글의 html 파일 불러오기.
        f = open(filePath, 'rt', encoding = 'utf-8')
        content = f.read()

        if content: # 게시글의 내용이 존재했을 때 작동하는 조건문
            return render_template('edit_post.html', body=content)
        else: # 게시글의 내용이 존재하지 않을 때 작동하는 조건문
            flash('수정할 게시글이 존재하지 않습니다.')
            return redirect(url_for('.index', username = session['username']))
    else:
        flash('로그인을 해주시길 바라겠습니다.')
        return redirect(url_for('auth.login'))


# 게시글 삭제 라우트 & 뷰함수
@main.route('/delete_post/<int:id>')
def delete_post(id):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문

        post = Post.query.filter_by(id = id).first_or_404() # 삭제할 포스트를 가져오는 쿼리 존재하지 않을 시 404 에러 발생

        if post.author.username != session['username']:
            # 삭제할 작성자와 로그인한 유저가 같지 않을 경우
            flash('해당 게시글의 작성한 유저가 아닙니다.')
            return redirect(request.referrer)

        # 삭제할 포스트와 그 포스트에 속해있는 댓글들을 deletepost, delcomments 테이블에 저장.
        delete_post = DeletePost(id = post.id, author_id = post.author_id, name = post.name, \
                                 timestamp = post.timestamp, comment_count = post.comment_count, body_text = post.body_text)
        comments = Comment.query.filter_by(post_id = post.id).all()
        db.session.bulk_insert_mappings(
            # 다수의 entity를 insert 위해 SQLALchemy에서 bulk_insert_mappings()를 지원해준다.
            DeleteComment,
            [
                dict(id = comment.id, author_id = comment.author_id, post_id = comment.post_id, body = comment.body, \
                     timestamp = comment.timestamp, groupnum = comment.groupnum, parent = comment.parent)
                for comment in comments
            ]
        )
        db.session.add(delete_post)

        db.session.delete(post)
        db.session.query(Comment).filter(Comment.post_id == post.id).delete() # 다수의 entity를 delete하기 위한 방식.
        post.author.post_count = post.author.post_count - 1

        db.session.commit()
        flash('삭제 완료했습니다.')

        return redirect(request.referrer)
    else:
        flash('로그인이 되지 않았습니다. 로그인 해주세요.')
        return redirect(url_for('auth.login'))


# 게시글 작성 라우트 & 뷰함수
@main.route('/write', methods = ['GET', 'POST'])
def write():
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        if request.method == 'POST':
            user = User.query.filter_by(username = session['username']).first()
            body = request.form['body'] # 게시글 내용
            body_text = request.form['searchBody'] # 게시글 검색하기 위한 게시글 내용

            name = create_file(body) # html 파일 생성.

            post = Post(name = name, body_text = body_text, author_id = session['id'])
            user.post_count = user.post_count + 1

            db.session.add(post)
            db.session.commit()

            flash('게시글 작성을 완료했습니다.')
            return redirect(url_for('.index', username = session['username']))
        else:
            return render_template('write.html')
    else:
        flash('로그인이 되어있지 않습니다.')
        return redirect(url_for('auth.login'))


# 게시글의 내용 및 댓글을 다는 라우트 & 뷰함수
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문
        post = Post.query.filter_by(id = id).first_or_404() # 게시글을 가져오는 쿼리 존재하지 않을 시 404에러 발생
        if request.method == 'POST':
            # POST 일 시(submit을 할 때)
            if request.form['comment-classfiy'] == 'comment': # 댓글 작성을 처리하는 조건문
                body = request.form['body'] # 작성한 댓글의 내용을 저장하는 변수

                comments = post.comments.order_by(Comment.groupnum.desc()).first()
                if not comments:
                    # 처음 다는 댓글일 경우
                    groupnum = 0
                else:
                    # 처음 다는 댓글이 아닐 경우
                    groupnum = comments.groupnum + 1
                comment = Comment(author_id = session['id'], post_id = id, body = body, groupnum = groupnum)

                post.comment_count = post.comment_count + 1

            elif request.form['comment-classfiy'] == 'recomment': # 답 댓글 작성을 처리하는 조건문
                parent_id = request.form['parent_id'] # 작성한 답 댓글의 부모 댓글의 id 컬럼 값을 저장한 변수
                groupnum = request.form['group_id'] # 답글의 그룹 번호 값을 저장한 변수
                body = request.form['body'] # 작성한 답 댓글의 내용을 저장한 변수

                comment = Comment(author_id = session['id'], post_id = id, body = body, groupnum = groupnum, parent = parent_id)

                post.comment_count = post.comment_count + 1

            else:
                # 댓글을 수정하는 경우
                editCommentId = request.form['editComment_id']
                body = request.form['body']

                comment = Comment.query.filter_by(id = editCommentId).first()

                if comment.author.username != session['username']:
                    # 수정할 댓글 작성자와 해당 댓글 작성자가 맞지 않을 경우.
                    flash('작성한 유저가 아닙니다.')
                    return redirect(url_for('.post', id = id))

                comment.body = body

            db.session.add(comment)
            db.session.commit()

            return redirect(url_for('.post', id = id))

        # method가 GET 일 시                

        post = Post.query.filter_by(id = id).first_or_404()
        comments = post.comments.order_by(Comment.groupnum, Comment.timestamp).all()

        return render_template('post.html', datas = [post], id = id, comments = comments)
        
    else:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# 댓글 삭제 라우트 & 뷰함수
@main.route('/delComment/<int:comment_id>')
def delComment(comment_id):
    if 'username' in session and 'id' in session: # 로그인이 되어있는지 확인하는 조건문

        comment = Comment.query.filter_by(id = comment_id).first()

        if comment.author.username != session['username']:
            flash('해당 댓글을 작성한 유저가 아닙니다.')
            return redirect(request.referrer)

        delete_comment = DeleteComment(id = comment.id, author_id = comment.author_id, post_id = comment.post_id, body = comment.body, \
                                       timestamp = comment.timestamp, groupnum = comment.groupnum, parent = comment.parent)

        if comment.parent == 0:
            # 삭제할 댓글이 최상위 댓글일 경우.
            count = Comment.query.filter_by(post_id = comment.post.id, groupnum = comment.groupnum).count()
            if count > 1:
                # 답 댓글이 존재하는 경우. 해당 최상위 댓글은 작성자와 내용 작성시간을 Null 처리
                comment.author_id = None
                comment.body = None
                comment.timestamp = None
            else:
                # 답글이 존재하지 않는 경우. 댓글 삭제
                db.session.delete(comment)
                comment.post.comment_count = comment.post.comment_count - 1

        else:
            # 최상위 댓글이 아닐 경우(답 댓글일 경우). 댓글 삭제.
            db.session.delete(comment)
            comment.post.comment_count = comment.post.comment_count - 1


        db.session.add(delete_comment)
        db.session.commit()

        return redirect(url_for('.post', id=delete_comment.post_id))
        
    else:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect(url_for('auth.login'))


# /follow_list 페이지에서 팔로우 nav-tab을 클릭할 시 팔로워 목록을 출력하는 라우트 & 뷰함수
@main.route('/follower/<username>')
def follower(username):
    try:
        return redirect(url_for('.follow_list', username = username, jf = 'follow'))
    except Exception as e:
        flash(str(e) + '라는 문제가 발생했습니다.')
        abort(500)


# /follow_list 페이지에서 팔로잉 nav-tab을 클릭할 시 팔로잉 목록을 출력하는 라우트 & 뷰함수
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