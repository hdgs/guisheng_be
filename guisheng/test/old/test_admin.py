
#coding:utf-8
import unittest
from flask import current_app, url_for,jsonify
from guisheng_app import create_app
from flask_sqlalchemy import SQLAlchemy
import random
import json

TOKEN = str(0)
ID = int(0)
ADMIN_ID = int(1)
ADMIN_PSWORD = int(535)
db = SQLAlchemy()

class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_app_exist(self):
        self.assertFalse(current_app is None)
   
    #login
    def test_admin_a_login(self):
        reponse = self.client.post(
                url_for('api.login',_external=True),
                data = json.dumps({
                    "password":str(ADMIN_PSWORD),
                    "email":str(ADMIN_PSWORD)
                    }),
                content_type = 'application/json')
        s = json.loads(reponse.data)['token']
        global TOKEN
        TOKEN = s
        self.assertTrue(reponse.status_code == 200)
    
