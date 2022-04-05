from flask import request, session
from flask_socketio import emit, join_room, leave_room
from .. import socketio, db
from ..models import ChatContent
import json

@socketio.on('joined', namespace = '/chatting')
def joined(data):
    room = data['roomId']
    print(room)
    join_room(room)


@socketio.on('text', namespace = '/chatting')
def text(message):
    print('test')
    print(message)
    room = message['roomId']
    content = ChatContent(author_id = session['id'], body = message['msg'], room_id = room)
    db.session.add(content)
    db.session.commit()
    emit('message', {'userId':session['id'], 'username':session['username'], 'image':content.author.profile_filename, 'msg':message['msg'], 'timestamp':content.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, room = room)


@socketio.on('left', namespace ='/chatting')
def left(message):
    room = message['roomId']
    leave_room(room)
