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
number = random.randint(10000,99999)

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
   
    #login & register
    def test_a_register(self):
        reponse = self.client.post(
                url_for('api.register',_external=True),
                data = json.dumps({
                    "username":str(number),
                    "email":str(number),
                    "password":str(number)}),
                content_type = 'application/json')
        self.assertTrue(reponse.status_code == 200)
        global ID 
        ID = json.loads(reponse.data)['created']

    def test_b_login(self):
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
    
    #Profile Methods
    def test_c_get_profile(self):
        reponse = self.client.post(
                url_for('api.get_profile',id=ID,_external=True),
                data = json.dumps({
                    "my_id":ID
                }),
                content_type = 'application/json')
        self.assertTrue(reponse.status_code == 200)   
    
    def test_c_edit_profile(self):
        response = self.client.put(
            url_for('api.edit_profile',id=ID,_external=True),
            data=json.dumps({
                "img_url":"test",
                "bg_url":"test",
                "name":str(number),
                "introduction":"test"
                }),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200)   
                
    def test_c_get_works(self):
        response = self.client.get(
            url_for('api.get_works',id=ID,_external=True),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200)   
    
    def test_c_get_collections(self):
        response = self.client.get(
            url_for('api.get_collections',id=ID,_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

    def test_c_get_suggestions(self):
        response = self.client.post(
            url_for('api.suggeston',id=ID,_external=True),
            data=json.dumps({
                "body":"test",
                "contact_information":"test"
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Pictures Methods
    
    
    def test_c_add_pics(self):
        response = self.client.post(
            url_for('api.add_pics',_external=True),
            data=json.dumps({
                "title":str(number),
                "tags":["test"],
                "authors":"test",
                "img_url":str(number),
                "description":"test",
                "editor":"test"
                }),
            content_type = 'application/json')
        print response.status_code
        #self.assertTrue(response.status_code == 201)

    

    def test_c_post_pic(self):
        response = self.client.post(
            url_for('api.get_pic',id=ID,_external=True),
                data = json.dumps({"my_id":ID}),
            content_type = 'application/json')
        #No Pictures so it's 404
        self.assertTrue(response.status_code == 404)

    #Feed 
    def test_z_feed_get(self):
        reponse = self.client.get(
                url_for('api.main_page',_external=True,kind=0,page=0,count=0),
                content_type = 'application/json')
        self.assertTrue(reponse.status_code == 200)
    

    '''    
    def test_z_everydaypic(self):
        reponse = self.client.get(
                url_for('api.main'
    '''
                
'''    
    def test_z_feed_search(self):
        reponse = self.client.post(
            url_for('api.search',_external=True),
            data=json.dumps({
                        "content":"test"
                        }),
            content_type = 'application/json')
        self.assertTrue(reponse.status_code == 200)
'''

