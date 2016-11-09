# coding: utf-8
"""
sql models

    use: Flask-SQLAlchemy
    -- http://flask-sqlalchemy.pocoo.org/2.1/

"""
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from datetime import datetime

# permissions
class Permission:
    """
    1. COMMENT: 0x01
    2. MODERATE_COMMENTS: 0x02
    3. ADMINISTER: 0x04
    """
    COMMENT = 0x01
    MODERATE_COMMENTS = 0x02
    ADMINISTER = 0x04


# user roles
class Role(db.Model):
    """
    1. User: COMMENT
    2. Moderator: MODERATE_COMMENTS
    3. Administrator: ADMINISTER
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT, True),
            'Moderator': (Permission.COMMENT |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (
                Permission.COMMENT |
                Permission.MODERATE_COMMENTS |
                Permission.ADMINISTER,
                False
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    """user"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(64))
    name = db.Column(db.String(64))
    weibo = db.Column(db.String(64))
    introduction = db.Column(db.Text)
    works = db.Column(db.Text)
    collects = db.relationship('Collect', backref='author', lazy='dynamic')
    suggestion = db.Column(db.Text)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    phonenumber = db.Column(db.String(164), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(164))

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def is_admin(self):
        if self.role_id == 2:
            return True
        return False

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser(AnonymousUserMixin):
    """ anonymous user """
    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser

# you can writing your models here:

#新闻
class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    comments = db.relationship('Comment', backref='news', lazy='dynamic')
    light = db.relationship('Light', backref='news', lazy='dynamic')
    collect = db.relationship('Collect', backref='news', lazy='dynamic')
    tag = db.Column(db.String(64))
    views = db.Column(db.Integer)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    img_url = db.Column(db.String(164))
    description = db.Column(db.Text)

    def __repr__(self):
        return "<News %r>" % self.id

#每日一图
class Everydaypic(db.Model):
    __tablename__ = 'everydaypics'
    id = db.Column(db.Integer,primary_key=True)
    img_url = db.Column(db.String(164))
    temperature = db.Column(db.Float)
    data = db.Column(db.String(64))
    place = db.Column(db.String(64))

    def __repr__(self):
        return "<Everydaypic %r>" % self.id

#图片集的单张图片
class Picture(db.Model):
    __tablename__ = 'pictures'
    id = db.Column(db.Integer,primary_key=True)
    img_url = db.Column(db.String(164))
    title = db.Column(db.String(64))
    tag = db.Column(db.String(64))
    views = db.Column(db.Integer)
    introduction = db.Column(db.Text)
    like = db.relationship('Like',backref='pictures', lazy='dynamic')
    comments = db.relationship('Comment',backref='pictures', lazy='dynamic')
    collect = db.relationship('Collect',backref='pictures', lazy='dynamic')
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Picture %r>" % self.id

#纯文章
class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    comments = db.relationship('Comment',backref='articles', lazy='dynamic')
    light = db.relationship('Light',backref='articles', lazy='dynamic')
    collect = db.relationship('Collect',backref='articles', lazy='dynamic')
    views = db.Column(db.Integer)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    img_url = db.Column(db.String(64))

    def __repr__(self):
        return "<Post %r>" % self.id

#带音乐分享的文章
class MusicArticle(db.Model):
    __tablename__ = 'musicarticles'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(164))
    img_url = db.Column(db.String(164))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    comments = db.relationship('Comment',backref='musicarticles', lazy='dynamic')
    light = db.relationship('Light',backref='musicarticles', lazy='dynamic')
    collect = db.relationship('Collect',backref='musicarticles', lazy='dynamic')
    views = db.Column(db.Integer)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    music_url = db.Column(db.String(164))
    music_title = db.Column(db.String(64))
    music_imgurl = db.Column(db.String(164))

    def __repr__(self):
        return "<Post %r>" % self.id

#带电影分享的文章
class FilmArticle(db.Model):
    __tablename__ = 'filmarticles'
    id = db.Column(db.Integer,primary_key=True)
    img_url = db.Column(db.String(164))
    title = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    comments = db.relationship('Comment',backref='filmarticles', lazy='dynamic')
    light = db.relationship('Light',backref='filmarticles', lazy='dynamic')
    collect = db.relationship('Collect',backref='filmarticles', lazy='dynamic')
    views = db.Column(db.Integer)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    film_url = db.Column(db.String(164))

    def __repr__(self):
        return "<Post %r>" % self.id

#互动话题
class Interaction(db.Model):
    __tablename__ = 'interactions'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64), unique=True)
    views = db.Column(db.Integer,primary_key=True)
    comments = db.relationship('Comment',backref='interactions', lazy='dynamic')
    commentnum = db.Column(db.Integer)
    light = db.relationship('Light',backref='interactions', lazy='dynamic')
    collect = db.relationship('Collect',backref='interactions', lazy='dynamic')
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Topic %r>" % self.id

#评论
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    musicarticle_id = db.Column(db.Integer, db.ForeignKey('musicarticles.id'))
    filmarticle_id = db.Column(db.Integer, db.ForeignKey('filmarticles.id'))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('interactions.id'))

    def __repr__(self):
        return "<Comment %r>" % self.id

#收藏
class Collect(db.Model):
    __tablename__ = 'collects'
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    musicarticle_id = db.Column(db.Integer, db.ForeignKey('musicarticles.id'))
    filmarticle_id = db.Column(db.Integer, db.ForeignKey('filmarticles.id'))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('interactions.id'))

    def __repr__(self):
        return "<Collect %r>" % self.id

#点亮
class Light(db.Model):
    __tablename__ = 'lights'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    musicarticle_id = db.Column(db.Integer, db.ForeignKey('musicarticles.id'))
    filmarticle_id = db.Column(db.Integer, db.ForeignKey('filmarticles.id'))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('interactions.id'))
    like_degree = db.Column(db.Integer,primary_key=True)

    def __repr__(self):
        return "<Light %r>" % self.id

#点赞
class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id'))

    def __repr__(self):
        return "<Like %r>" % self.id
