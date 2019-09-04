from flask import request, session
from flask_socketio import emit, join_room, leave_room
from .. import socketio, db
from ..models import ChatContent
import json


# Client에서 전송한 room id value를 받아 room을 생성하거나 연결하는 joined 이벤트
@socketio.on('joined', namespace = '/chatting')
def joined(data):
    room = data['roomId']
    join_room(room)


# Client에서 작성한 채팅 내용을 받아 데이터베이스에 내용을 저장한 후 Client의 message 이벤트로 전송하는 text 이벤트
@socketio.on('text', namespace = '/chatting')
def text(message):
    room = message['roomId']
    content = ChatContent(author_id = session['id'], body = message['msg'], room_id = room)
    db.session.add(content)
    db.session.commit()
    emit('message', {'userId':session['id'], 'username':session['username'], 'image':content.author.profile_filename, 'msg':message['msg'], 'timestamp':content.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, room = room)


# 채팅방을 나가기 위한 left 이벤트
@socketio.on('left', namespace ='/chatting')
def left(message):
    room = message['roomId']
    leave_room(room)
