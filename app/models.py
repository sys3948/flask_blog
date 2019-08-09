from flask import current_app, request, url_for
from . import db
from datetime import datetime


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)
    timestamp = db.Column(db.DateTime(), default = datetime.now)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True, index = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(225))
    location = db.Column(db.Text)
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default = datetime.now)
    profile_filename = db.Column(db.String(200), default = 'information.png')
    post_count = db.Column(db.Integer, default = 0)
    follow_count = db.Column(db.Integer, default = 0)
    following_count = db.Column(db.Integer, default = 0)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    deleteposts = db.relationship('DeletePost', backref = 'author', lazy = 'dynamic')
    comments = db.relationship('Comment', backref = 'author', lazy = 'dynamic')
    deletecomments = db.relationship('DeleteComment', backref = 'author', lazy = 'dynamic')
    followed = db.relationship('Follow',
                               foreign_keys = [Follow.follower_id],
                               backref=db.backref('follower', lazy = 'joined'),
                               lazy = 'dynamic',
                               cascade = 'all, delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys = [Follow.followed_id],
                               backref=db.backref('followed', lazy = 'joined'),
                               lazy = 'dynamic',
                               cascade = 'all, delete-orphan')

    def __init__(self, **kwargs):
        # self.email = email
        # self.username = username
        # self.password_hash = password_hash
        print(kwargs)
        print(kwargs['email'])
        super().__init__(**kwargs)
        self.follow(self)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower = self, followed = user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id = user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False

        return self.followed.filter_by(followed_id = user.id).first() is not None

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime(), default = datetime.now)
    comment_count = db.Column(db.Integer, default = 0)
    body_text = db.Column(db.Text)
    comments = db.relationship('Comment', backref = 'post', lazy = 'dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), default = datetime.now)
    groupnum = db.Column(db.Integer, default = 0)
    parent = db.Column(db.Integer, default = 0)


class DeletePost(db.Model):
    __tablename__ = 'deletepost'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime(), default = datetime.now)
    comment_count = db.Column(db.Integer, default = 0)
    body_text = db.Column(db.Text)
    deletecomments = db.relationship('DeleteComment', backref = 'post', lazy = 'dynamic')


class DeleteComment(db.Model):
    __tablename__ = 'delcomments'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('deletepost.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), default = datetime.now)
    groupnum = db.Column(db.Integer, default = 0)
    parent = db.Column(db.Integer, default = 0)
    