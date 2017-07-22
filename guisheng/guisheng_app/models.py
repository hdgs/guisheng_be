# coding: utf-8
"""
sql models

    use: Flask-SQLAlchemy
    -- http://flask-sqlalchemy.pocoo.org/2.1/

"""
from flask import current_app,request
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from itsdangerous import JSONWebSignatureSerializer as Serializer
from datetime import datetime
from markdown import markdown
import bleach


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
    User: id=3
    Moderator: id=1
    Administrator: id=2
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
    email = db.Column(db.String(164), unique=True, index=True)
    password_hash = db.Column(db.String(164))
    img_url = db.Column(db.String(164),default="")
    bg_url = db.Column(db.String(164),default="")
    name = db.Column(db.String(64),default="",unique=True,index=True)
    weibo = db.Column(db.String(164),default="")
    introduction = db.Column(db.Text,default="")
    news = db.relationship('News', backref='author', lazy='dynamic',cascade='all')
    pictures = db.relationship('Picture', backref='author', lazy='dynamic',cascade='all')
    articles = db.relationship('Article', backref='author', lazy='dynamic',cascade='all')
    interactions = db.relationship('Interaction', backref='author', lazy='dynamic',cascade='all')
    collection = db.relationship('Collect', backref='author', lazy='dynamic',cascade='all')
    comments = db.relationship('Comment', backref='author', lazy='dynamic',cascade='all')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'),default=3)
    user_role = db.Column(db.Integer,default=0)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        if self.role_id == 2:
            return True
        return False

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_auth_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u=User(name=forgery_py.internet.user_name(True),
                   email=forgery_py.internet.email_address(),
                   img_url=forgery_py.internet.email_address(),
                   bg_url=forgery_py.internet.email_address(),
                   weibo=forgery_py.internet.email_address(),
                   introduction=forgery_py.lorem_ipsum.paragraph(),
                   password_hash=forgery_py.lorem_ipsum.word())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return "<User %r>" % self.name


class AnonymousUser(AnonymousUserMixin):
    """ anonymous user """
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def generate_auth_token(self, expiration):
        return None

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#新闻
class News(db.Model):
    __tablename__ = 'news'
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),default="",unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"))
    body = db.Column(db.Text,default="")
    comments = db.relationship('Comment', backref='news', lazy='dynamic',cascade='all')
    light = db.relationship('Light', backref='news', lazy='dynamic',cascade='all')
    collect = db.relationship('Collect', backref='news', lazy='dynamic',cascade='all')
    tag = db.relationship("PostTag", backref="news",lazy="dynamic", cascade='all')
    views = db.Column(db.Integer,default=0)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    img_url = db.Column(db.String(164),default="")
    description = db.Column(db.Text,default="")
    editor = db.Column(db.String(64),default="")
    kind = 1
    published = db.Column(db.Integer,default=0)
    body_html = db.Column(db.Text,default="")
    tea = db.Column(db.Integer,default=0)

    #Special And its ChildTopic
    special_id = db.Column(db.Integer,db.ForeignKey('specials.id'),default=-1)
    childtopic_id = db.Column(db.Integer,db.ForeignKey('childtopics.id'),default=-1)

    @staticmethod
    def from_json(json_news):
        if User.query.filter_by(name=json_news.get('author')).first():
            u=User.query.filter_by(name=json_news.get('author')).first()
            title = json_news.get('title')
            img_url = json_news.get('img_url')
            editor = json_news.get('editor')
            return News(title=title, author=u,
                        img_url=img_url,editor=editor)
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            n = News(title=forgery_py.lorem_ipsum.title(randint(1,4)),
                     author=u,
                     body=forgery_py.lorem_ipsum.paragraphs(randint(1,4)),
                     views=randint(0,100),
                     time=forgery_py.date.date(True),
                     img_url=forgery_py.internet.email_address(),
                     description="",
                     published=randint(0,1))
            db.session.add(n)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


    def __repr__(self):
        return "<News %r>" % self.id

db.event.listen(News.body, 'set', News.on_changed_body)


#每日一图
class Everydaypic(db.Model):
    __tablename__ = 'everydaypics'
    id = db.Column(db.Integer,primary_key=True)
    img_url = db.Column(db.String(164),default="")
    climate = db.Column(db.Integer,default=1)
    date = db.Column(db.String(164),default="")
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    @staticmethod
    def from_json(json_everydaypic):
        img_url = json_everydaypic.get('img_url')
        climate = json_everydaypic.get('climate')
        date = json_everydaypic.get('date')
        return Everydaypic(img_url=img_url,
                           climate=climate,date=date)

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            e = Everydaypic(img_url=forgery_py.internet.email_address(),
                            climate = 1,
                            date = forgery_py.date.date(True),
                            time=forgery_py.date.date(True))
            db.session.add(e)
            db.session.commit()

    def __repr__(self):
        return "<Everydaypic %r>" % self.id

#图片集
class Picture(db.Model):
    __tablename__ = 'pictures'
    __searchable__ = ['title']
    id = db.Column(db.Integer,primary_key=True)
    img_url = db.relationship('Image', backref='picture', lazy='dynamic',cascade='all')
    title = db.Column(db.String(64),default="",unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tag = db.relationship("PostTag", backref="pictures",lazy="dynamic", cascade='all')
    views = db.Column(db.Integer, default=0)
    description = db.Column(db.Text,default="")
    like = db.relationship('Like',backref='picture', lazy='dynamic',cascade='all')
    comments = db.relationship('Comment',backref='picture', lazy='dynamic',cascade='all')
    collect = db.relationship('Collect',backref='picture', lazy='dynamic',cascade='all')
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    editor = db.Column(db.String(64),default="")
    kind = 2
    published = db.Column(db.Integer,default=0)
    tea = db.Column(db.Integer,default=0)

    #Special And its ChildTopic
    special_id = db.Column(db.Integer,db.ForeignKey('specials.id'),default=-1)
    childtopic_id = db.Column(db.Integer,db.ForeignKey('childtopics.id'),default=-1)
    
    @staticmethod
    def from_json(json_pic):
        if User.query.filter_by(name=json_pic.get('author')).first():
            u = User.query.filter_by(name=json_pic.get('author')).first()
            title = json_pic.get('title')
            editor = json_pic.get('editor')
            return Picture(title=title, author=u, editor=editor)

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Picture(title=forgery_py.lorem_ipsum.title(randint(1,4)),
                        author=u,
                        views=randint(0,100),
                        description="",
                        time=forgery_py.date.date(True),
                        published=randint(0,1))
            db.session.add(p)
            db.session.commit()

    def __repr__(self):
        return "<Picture %r>" % self.id

#水墨文章
class Article(db.Model):
    __tablename__ = 'articles'
    __searchable__ = ['title']
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(164),default="",unique=True, index=True)
    img_url = db.Column(db.String(164),default="")
    author_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"))
    body = db.Column(db.Text,default="")
    comments = db.relationship('Comment',backref='article', lazy='dynamic',cascade='all')
    light = db.relationship('Light',backref='article', lazy='dynamic',cascade='all')
    collect = db.relationship('Collect',backref='article', lazy='dynamic',cascade='all')
    views = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    description = db.Column(db.Text,default="")
    tag = db.relationship("PostTag", backref="articles",lazy="dynamic", cascade='all')
    music_url = db.Column(db.String(164),default="")
    music_title = db.Column(db.String(164),default="")
    music_img_url = db.Column(db.String(164),default="")
    singer = db.Column(db.String(64),default="")
    film_url = db.Column(db.String(164),default="")
    film_img_url = db.Column(db.String(164),default="")
    scores = db.Column(db.Float,default=0.0)
    editor = db.Column(db.String(64),default="")
    kind = 3
    published = db.Column(db.Integer,default=0)
    body_html = db.Column(db.Text,default="")
    tea = db.Column(db.Integer,default=0)
    flag = db.Column(db.Integer,default=1)

    @staticmethod
    def from_json(json_article):
        if User.query.filter_by(name=json_article.get('author')).first():
            u = User.query.filter_by(name=json_article.get('author')).first()
            title = json_article.get('title')
            img_url = json_article.get('img_url')
            description = json_article.get('description')
            music_url = json_article.get('music_url')
            music_title = json_article.get('music_title')
            music_img_url = json_article.get('music_img_url')
            singer = json_article.get('singer')
            film_url = json_article.get('film_url')
            film_img_url = json_article.get('film_img_url')
            editor = json_article.get('editor')
            flag = json_article.get('flag')
            scores = json_article.get('scores')
            return Article(title=title, author=u,
                        description=description,img_url=img_url,
                        music_url=music_url,music_title=music_title,
                        music_img_url=music_img_url, film_url=film_url,singer=singer,
                        film_img_url=film_img_url, editor=editor, flag=flag,scores=scores)

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            a = Article(title=forgery_py.lorem_ipsum.title(randint(1,4)),
                        img_url=forgery_py.internet.email_address(),
                        author=u,
                        body=forgery_py.lorem_ipsum.paragraphs(randint(1,4)),
                        time=forgery_py.date.date(True),
                        description=forgery_py.lorem_ipsum.paragraph(),
                        music_url=forgery_py.internet.email_address(),
                        music_title=forgery_py.lorem_ipsum.word(),
                        music_img_url=forgery_py.internet.email_address(),
                        singer = forgery_py.lorem_ipsum.title(randint(1,4)),
                        film_url=forgery_py.internet.email_address(),
                        film_img_url=forgery_py.internet.email_address(),
                        views = randint(0,100),
                        published=randint(0,1))
            db.session.add(a)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def __repr__(self):
        return "<Article %r>" % self.id

db.event.listen(Article.body, 'set', Article.on_changed_body)

#互动话题
class Interaction(db.Model):
    __tablename__ = 'interactions'
    __searchable__ = ['title']
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(164), default="",unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"))
    views = db.Column(db.Integer,default=0)
    comments = db.relationship('Comment',backref='interaction', lazy='dynamic',cascade='all')
    light = db.relationship('Light',backref='interaction', lazy='dynamic',cascade='all')
    collect = db.relationship('Collect',backref='interaction', lazy='dynamic',cascade='all')
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    description = db.Column(db.Text,default="")
    tag = db.relationship("PostTag", backref="interactions",lazy="dynamic", cascade='all')
    body = db.Column(db.Text,default="")
    img_url = db.Column(db.String(164),default="")
    editor = db.Column(db.String(64),default="")
    kind = 4
    published = db.Column(db.Integer,default=0)
    tea = db.Column(db.Integer,default=0)
    flag = db.Column(db.Integer,default=0)

    @staticmethod
    def from_json(json_interaction):
        if User.query.filter_by(name=json_interaction.get('author')).first():
            u = User.query.filter_by(name=json_interaction.get('author')).first()
            title = json_interaction.get('title')
            description = json_interaction.get('description')
            editor = json_interaction.get('editor')
            img_url = json_interaction.get('img_url')
            flag = json_interaction.get('flag')
            return Interaction(title=title, author=u,img_url=img_url,
                               description=description, editor=editor,flag=flag)

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            t = Interaction(title=forgery_py.lorem_ipsum.title(randint(1,4)),
                            author=u,
                            time=forgery_py.date.date(True),
                            description=forgery_py.lorem_ipsum.paragraph(),
                            img_url=forgery_py.internet.email_address(),
                            body=forgery_py.lorem_ipsum.paragraphs(randint(1,4)),
                            views=randint(0,100),
                            published = randint(0,1))
            db.session.add(t)
            db.session.commit()


    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def __repr__(self):
        return "<Interaction %r>" % self.id

db.event.listen(Interaction.body, 'set', Interaction.on_changed_body)


class Special(db.Model):
    __tablename__ = 'specials'
    id=db.Column(db.Integer,primary_key=True)
    special_name=db.Column(db.String(164),nullable=False,unique=True)
    description = db.Column(db.String,default="",index=True)
    childtopics = db.relationship('ChildTopic',backref='specials',lazy='dynamic',cascade='all')
    articles = db.relationship('News',backref='specials',lazy='dynamic',cascade='all')
    pictures = db.relationship('Picture',backref='specials',lazy='dynamic',cascade='all')


class ChildTopic(db.Model):
    __tablename__ = 'childtopics'
    id = db.Column(db.Integer,primary_key=True)
    childtopic_name = db.Column(db.String(164),nullable=False,unique=True)
    special_id = db.Column(db.Integer,db.ForeignKey('specials.id'))
    articles = db.relationship('News',backref='childtopics',lazy='dynamic',cascade='all')
    pictures = db.relationship('Picture',backref='childtopics',lazy='dynamic',cascade='all')




#图片
class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(164),default="")
    introduction = db.Column(db.Text,default="")
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id',ondelete="CASCADE"))

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            img = Image(img_url=forgery_py.internet.email_address(),
                        introduction=forgery_py.lorem_ipsum.paragraph())
            db.session.add(img)
            db.session.commit()


    def __repr__(self):
        return "<Image %r>" % self.id

#评论
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text,default="")
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"))
    comment_id = db.Column(db.Integer,default=-1)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id',ondelete="CASCADE"))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id',ondelete="CASCADE"))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id',ondelete="CASCADE"))
    interaction_id = db.Column(db.Integer, db.ForeignKey('interactions.id',ondelete="CASCADE"))
    like = db.relationship('Like',backref='comment', lazy='dynamic',cascade='all')

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        news_count = News.query.count()
        pic_count = Picture.query.count()
        art_count = Article.query.count()
        int_count = Interaction.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            n = News.query.offset(randint(0,news_count-1)).first()
            p = Picture.query.offset(randint(0,pic_count-1)).first()
            a = Article.query.offset(randint(0,art_count-1)).first()
            t = Interaction.query.offset(randint(0,int_count-1)).first()
            c = Comment(body=forgery_py.lorem_ipsum.paragraphs(randint(1,4)),
                        time=forgery_py.date.date(True),
                        author=u,
                        news=n,
                        picture=p,
                        article=a,
                        interaction=t)
            db.session.add(c)
            db.session.commit()

    def __repr__(self):
        return "<Comment %r>" % self.id

#收藏
class Collect(db.Model):
    __tablename__ = 'collects'
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id',ondelete="CASCADE"))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id',ondelete="CASCADE"))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id',ondelete="CASCADE"))
    interaction_id = db.Column(db.Integer, db.ForeignKey('interactions.id',ondelete="CASCADE"))

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        news_count = News.query.count()
        art_count = Article.query.count()
        pic_count = Picture.query.count()
        int_count = Interaction.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            n = News.query.offset(randint(0,news_count-1)).first()
            a = Article.query.offset(randint(0,art_count-1)).first()
            p = Picture.query.offset(randint(0,pic_count-1)).first()
            t = Interaction.query.offset(randint(0,int_count-1)).first()
            c = Collect(author=u,
                        news=n,
                        article=a,
                        picture=p,
                        interaction=t)
            db.session.add(c)
            db.session.commit()

    def __repr__(self):
        return "<Collect %r>" % self.id

#点亮
class Light(db.Model):
    __tablename__ = 'lights'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id',ondelete="CASCADE"))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id',ondelete="CASCADE"))
    interaction_id = db.Column(db.Integer, db.ForeignKey('interactions.id',ondelete="CASCADE"))
    like_degree = db.Column(db.Integer)

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        news_count = News.query.count()
        art_count = Article.query.count()
        int_count = Interaction.query.count()
        for i in range(count):
            n = News.query.offset(randint(0,news_count-1)).first()
            a = Article.query.offset(randint(0,art_count-1)).first()
            t = Interaction.query.offset(randint(0,int_count-1)).first()
            l = Light(news=n,
                      article=a,
                      interaction=t,
                      like_degree=randint(1,5))
            db.session.add(l)
            db.session.commit()

    def __repr__(self):
        return "<Light %r>" % self.id

#点赞
class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id',ondelete="CASCADE"))
    comment_id = db.Column(db.Integer,db.ForeignKey('comments.id',ondelete="CASCADE"))

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        pic_count = Picture.query.count()
        com_count = Comment.query.count()
        for i in range(count):
            p = Picture.query.offset(randint(0,pic_count-1)).first()
            c = Comment.query.offset(randint(0,pic_count-1)).first()
            l = Like(picture=p,
                     comment=c)
            db.session.add(l)
            db.session.commit()

    def __repr__(self):
        return "<Like %r>" % self.id

class PostTag(db.Model):
    __tablename__ = 'posttags'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer,db.ForeignKey('tags.id', ondelete="CASCADE"))
    news_id = db.Column(db.Integer,db.ForeignKey('news.id',ondelete="CASCADE"))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id',ondelete="CASCADE"))
    picture_id = db.Column(db.Integer,db.ForeignKey('pictures.id',ondelete="CASCADE"))
    interaction_id = db.Column(db.Integer,db.ForeignKey('interactions.id',ondelete="CASCADE"))
    count = db.Column(db.Integer,default=0)

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        tag_count = Tag.query.count()
        news_count = News.query.count()
        art_count = Article.query.count()
        pic_count = Picture.query.count()
        int_count = Interaction.query.count()
        for j in range(count):
            nt = Tag.query.offset(randint(0,tag_count-1)).first()
            at = Tag.query.offset(randint(0,tag_count-1)).first()
            pt = Tag.query.offset(randint(0,tag_count-1)).first()
            it = Tag.query.offset(randint(0,tag_count-1)).first()
            n = News.query.offset(randint(0,news_count-1)).first()
            a = Article.query.offset(randint(0,art_count-1)).first()
            p = Picture.query.offset(randint(0,pic_count-1)).first()
            i = Interaction.query.offset(randint(0,int_count-1)).first()
            pt = PostTag(news_tags=nt,
                         article_tags=at,
                         picture_tags=pt,
                         interaction_tags=it,
                         news=n,
                         articles=a,
                         pictures=p,
                         interactions=i,
                         count=randint(0,100))
            db.session.add(pt)
            db.session.commit()


class Tag(db.Model):
    __tablename__ = 'tags'
    __searchable__ = ['body']
    id = db.Column(db.Integer,primary_key=True)
    count = db.Column(db.Integer,default=0)
    body = db.Column(db.String(64),default="")
    news = db.relationship("PostTag", backref="news_tags", lazy="dynamic",cascade='all')
    pictures = db.relationship("PostTag", backref="picture_tags", lazy="dynamic",cascade='all')
    articles = db.relationship("PostTag", backref="article_tags", lazy="dynamic",cascade='all')
    interactions = db.relationship("PostTag", backref="interaction_tags", lazy="dynamic",cascade='all')

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        for i in range(count):
            t = Tag(count=randint(0,100),
                  body=forgery_py.lorem_ipsum.title(1))
            db.session.add(t)
            db.session.commit()

    def __repr__(self):
        return "<Tag %r>" % self.id

class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text,default="")
    contact_information = db.Column(db.String(164),default="")

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        for i in range(count):
            s = Suggestion(body=forgery_py.lorem_ipsum.paragraphs(randint(1,4)),
                           contact_information=forgery_py.internet.email_address())
            db.session.add(s)
            db.session.commit()

    def __repr__(self):
        return "<Suggestion %r>" % self.id

