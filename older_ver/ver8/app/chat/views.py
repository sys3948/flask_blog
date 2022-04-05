from flask import abort, current_app, flash, url_for, redirect, render_template, request, session
from . import chat
from .. import db
from ..models import User, MachingChat, ChatContent, Follow
from sqlalchemy.orm import aliased


@chat.route('/chattingroom')
def chattingroom():
    mach = MachingChat.query.filter_by(author_id = session['id']).all()
    return render_template('chatroom.html', chats = mach)


@chat.route('/createroom', methods=['GET', 'POST'])
def createroom():
    if request.method == 'POST':
        mach_users_id = request.form.getlist('userId')
        if not mach_users_id:
            flash('채팅할 대상자를 선택하지 않았습니다. 선택해주세요.')
            return redirect(url_for('.createroom'))

        else:
            title = session['username'] + ', '
            for id in mach_users_id:
                user = User.query.filter_by(id = id).first()
                title = title + user.username + ', '

            create_mach = MachingChat.query.order_by(MachingChat.room_id.desc()).first()
            if not create_mach:
                create_mach_id = 1
            else:
                create_mach_id = create_mach.room_id + 1

            mach = MachingChat(author_id = session['id'], title = title, room_id = create_mach_id, gp = True)
            db.session.add(mach)

            mach = [MachingChat(author_id = id, title = title, room_id = create_mach_id, gp = True) for id in mach_users_id]
            db.session.add_all(mach)

            db.session.commit()

        
        return redirect('/chatting?roomId=' + str(create_mach_id))
    users = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == session['id'], Follow.followed_id != session['id']).order_by(Follow.timestamp.desc()).all()
    return render_template('createroom.html', users = users)


@chat.route('/maching/<int:userId>')
def maching(userId):
    # mach1 = aliased(MachingChat)
    # mach2 = aliased(MachingChat)
    # mach = db.session.query(mach1, mach2).join(mach2, mach1.room_id == mach2.room_id).\
    #                     filter(mach1.author_id == session['id'], mach1.gp == False, mach2.author_id == userId, mach2.gp == False).\
    #                     first()
    machaliased = aliased(MachingChat)
    mach = MachingChat.query.join(machaliased, MachingChat.room_id == machaliased.room_id).\
                filter(MachingChat.author_id == session['id'], MachingChat.gp == False, machaliased.author_id == userId, machaliased.gp == False).\
                first()


    if not mach:
        create_mach = MachingChat.query.order_by(MachingChat.room_id.desc()).first()
        if not create_mach:
            create_mach_id = 1
        else:
            create_mach_id = create_mach.room_id + 1

        print(create_mach_id)

        other = User.query.filter_by(id = userId).first_or_404()
        create_maching_me = MachingChat(author_id = session['id'], room_id = create_mach_id, title = other.username, gp = False)
        create_maching_outhor = MachingChat(author_id = userId, room_id = create_mach_id, title = session['username'], gp = False)
        db.session.add_all([create_maching_me, create_maching_outhor])
        db.session.commit()

        room_id = create_mach_id

    else:
        room_id = mach.room_id

    print(room_id)

    return redirect(url_for('.chatting', roomId = room_id))


@chat.route('/chatting')
def chatting():
    roomId = int(request.args.get('roomId'))
    mach_me = MachingChat.query.filter_by(author_id = session['id'], room_id = roomId).first()
    mach_outher = MachingChat.query.filter(MachingChat.author_id != session['id'], MachingChat.room_id == roomId).first()
    chat = ChatContent.query.filter_by(room_id = roomId).order_by(ChatContent.timestamp).all()
    if chat:
        return render_template('chatting.html', chats = chat, roomId = roomId, me = mach_me)
    return render_template('chatting.html', roomId = roomId, me = mach_me)