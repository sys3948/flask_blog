from flask import abort, current_app, flash, url_for, redirect, render_template, request, session
from . import chat
from .. import db
from ..models import User, MachingChat, ChatContent, Follow
from sqlalchemy.orm import aliased


# 채팅방 목록 페이지의 라우트 & 뷰함수
@chat.route('/chattingroom')
def chattingroom():
    # 로그인한 유저의 채팅방 목록을 검색하는 쿼리
    mach = MachingChat.query.filter_by(author_id = session['id']).all()
    return render_template('chatroom.html', chats = mach)


# 채팅방 생성 페이지의 라우트 & 뷰함수
@chat.route('/createroom', methods=['GET', 'POST'])
def createroom():
    if request.method == 'POST':
        # POST일 경우(submit할 경우)
        mach_users_id = request.form.getlist('userId') # 채팅할 유저들의 id value의 목록
        if not mach_users_id:
            # 목록이 존재하지 않을(빈 목록) 경우
            flash('채팅할 대상자를 선택하지 않았습니다. 선택해주세요.')
            return redirect(url_for('.createroom'))

        else:
            # 목록이 존재할(비어있지 않을) 경우
            title = session['username'] + ', ' # 생성할 채팅방의 제목(Ex: username, username, ....)
            for id in mach_users_id:
                user = User.query.filter_by(id = id).first()
                title = title + user.username + ', '

            create_mach = MachingChat.query.order_by(MachingChat.room_id.desc()).first() # 생성할 채팅방의 번호를 생성하기 위해 최신 번호를 검색하는 쿼리
            if not create_mach:
                # 채팅 방이 존재하지 않을 경우 생성할 채팅방의 번호는 1
                create_mach_id = 1
            else:
                # 채팅 방이 존재할 경우 생성할 채팅방의 번호는 최근 채팅방의 번호 + 1
                create_mach_id = create_mach.room_id + 1

            # 생성할 채팅방에 대한 정보(채팅 유저, 제목, 채팅방번호, 개인 채팅 & 단체 채팅 식별)
            mach = MachingChat(author_id = session['id'], title = title, room_id = create_mach_id, gp = True)
            db.session.add(mach)

            mach = [MachingChat(author_id = id, title = title, room_id = create_mach_id, gp = True) for id in mach_users_id]
            db.session.add_all(mach)

            db.session.commit()

        
        return redirect('/chatting?roomId=' + str(create_mach_id))
    # GET일 경우(submit을 안 할 경우)
    users = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == session['id'], Follow.followed_id != session['id']).order_by(Follow.timestamp.desc()).all()
    return render_template('createroom.html', users = users)


# 개인별 채팅 매칭 페이지의 라우트 & 뷰함수
@chat.route('/maching/<int:userId>')
def maching(userId):
    # mach1 = aliased(MachingChat)
    # mach2 = aliased(MachingChat)
    # mach = db.session.query(mach1, mach2).join(mach2, mach1.room_id == mach2.room_id).\
    #                     filter(mach1.author_id == session['id'], mach1.gp == False, mach2.author_id == userId, mach2.gp == False).\
    #                     first()

    # 해당 유저들 끼리 매칭한 채팅방을 찾는 self join 쿼리 
    machaliased = aliased(MachingChat)
    mach = MachingChat.query.join(machaliased, MachingChat.room_id == machaliased.room_id).\
                filter(MachingChat.author_id == session['id'], MachingChat.gp == False, machaliased.author_id == userId, machaliased.gp == False).\
                first()


    if not mach:
        # 매칭한 채팅방이 존재하지 않을 경우 채팅방 생성.
        create_mach = MachingChat.query.order_by(MachingChat.room_id.desc()).first()
        if not create_mach:
            create_mach_id = 1
        else:
            create_mach_id = create_mach.room_id + 1

        other = User.query.filter_by(id = userId).first_or_404()
        create_maching_me = MachingChat(author_id = session['id'], room_id = create_mach_id, title = other.username, gp = False)
        create_maching_outhor = MachingChat(author_id = userId, room_id = create_mach_id, title = session['username'], gp = False)
        db.session.add_all([create_maching_me, create_maching_outhor])
        db.session.commit()

        room_id = create_mach_id

    else:
        # 매칭한 채팅방이 존재할 경우 해당 채팅방의 room_id 값 가져오기.
        room_id = mach.room_id

    # 매칭한 방으로 리다이렉션하기.
    return redirect(url_for('.chatting', roomId = room_id))


# 채팅 페이지의 라우트 & 뷰함수
@chat.route('/chatting')
def chatting():
    roomId = int(request.args.get('roomId')) # 해당 room id value가 있는 url을 가져와서 room maching하기
    mach_me = MachingChat.query.filter_by(author_id = session['id'], room_id = roomId).first() # 로그인 유저가 접속한 채팅방에 대한 정보를 검색하는 쿼리
    chat = ChatContent.query.filter_by(room_id = roomId).order_by(ChatContent.timestamp).all() # 해당 채팅방에 대한 채팅 내용들을 검색하는 쿼리
    if chat:
        # 채팅 내용이 존재하는 경우
        return render_template('chatting.html', chats = chat, roomId = roomId, me = mach_me)
    # 그렇지 않는 경우
    return render_template('chatting.html', roomId = roomId, me = mach_me)