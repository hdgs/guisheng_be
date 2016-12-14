# 桂声移动版-后端

### 运行：

```
$ git clone https://github.com/Muxi-Studio/guisheng_be.git
$ cd guisheng_be/guisheng
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py runserver
```

### 初始化数据库：

```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
$ python manage.py shell
```

进入shell后：

```
>>> Role.insert_roles()
>>> db.create_all()
>>> User.generate_fake(100)
>>> Everydaypic.generate_fake(100)
>>> News.generate_fake(100)
>>> Article.generate_fake(100)
>>> Picture.generate_fake(100)
>>> Interaction.generate_fake(100)
>>> Comment.generate_fake(100)
>>> Collect.generate_fake(100)
>>> Tag.generate_fake(100)
>>> PostTag.generate_fake(100)
>>> quit()
```
