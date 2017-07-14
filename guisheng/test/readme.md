在测试前需要注册一个email和password一样的用户，然后在数据库内修改其`role_id` 为2, `user_role` 为 7.
然后在test.py中修改ADMIN_PSWORD为注册时用的psssword（password和email在注册时设置为一样的）．
之后便可以`python manage.py test`来测试了．
