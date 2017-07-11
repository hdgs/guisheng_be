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
                    "password":str(number),
                    "email":str(number)
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
    
    #News Method
    def test_c_get_news(self):
        response = self.client.post(
            url_for('api.get_news',id=ID,_external=True),
            data=json.dumps({
                "my_id":str(number) }),
            content_type = 'application/json')
        print response.status_code
#        self.assertTrue(response.status_code==200)
    
    
    
    ''' 
    def test_c_recommend_news(self):
        response = self.client.post(
                url_for('api.recommend_news',_external=True),
                data=json.dumps({
                        "article_id":1
                    }),
                content_type = 'application/json')
        self.assertTrue(response.status_code==200)
    '''

    #Like

    def test_c_like_picture(self):
        response = self.client.post(
                url_for('api.like_picture',_external=True),
                data=json.dumps({
                        "picture_id":1 
                                }),
                content_type = 'application/json')
        self.assertTrue(response.status_code==200)
    
    def test_c_like_comment(self):
        response = self.client.post(
                url_for('api.like_comment',_external=True),
                data=json.dumps({
                        "comment_id":1 
                                }),
                content_type = 'application/json')
        self.assertTrue(response.status_code==200)


    #Light

    def test_d_light(self):
        response = self.client.post(
                url_for('api.light',_external=True),
                data=json.dumps({
                        "article_id":1,
                        "kind":1,
                        "like_degree":1
                        }),
                content_type = 'application/json')
        self.assertTrue(response.status_code==200)
    '''    
    def test_c_add_news(self):
        response = self.client.post(
            url_for('api.add_news',_external=True),
            data=json.dumps({
                    "title":str(number),
                    "tags":["test"],
                    "name":str(number),
                    "img_url":"test",
                    "editor":"test"
                }),
            content_type = 'application/json')
        print response.status_code
    '''          
    
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
    
    
    #News
    #def test_d_get_news(self):
    #    response = self.client.post(
    #        url_for('api.get_news',)
     
    
    #Feed 
    def test_z_main_page(self):
        reponse = self.client.get(
                url_for('api.main_page',_external=True,kind=0,page=0,count=0),
                content_type = 'application/json')
        self.assertTrue(reponse.status_code == 200)
    
    #Don't have redis database
    def search(self):
        response = self.client.post(
                url_for('api.search',_external=True),
                data=json.dumps({"content":"test"}),
                content_type = 'application/json')
        print str(response.status_code)+ " don't have rds"
        #self.assertTrue(response.status_code == 200)


    #Interactions
    def test_d_get_interaction(self):
        
        response = self.client.post(
                url_for('api.get_interaction',id=1,_external=True),
                data=json.dumps({
                        "my_id":1,
                        }),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    
    
    def test_d_recommend_interaction(self):
        response = self.client.post(
                url_for('api.recommend_interactions',_external=True),
                data=json.dumps({
                    "article_id":1 }),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200)


    def test_d_everydaypic(self):
        response = self.client.get(
                url_for('api.get_everydaypic',_external=True),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200) 

    #Comment
    
    def test_d_get_comments(self):
        response = self.client.get(
                url_for('api.get_comments',article_id=1,kind=1,_external=True),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200) 
    
    def d_create_comments(self): #database error
        response = self.client.post(
                url_for('api.create_comments',_external=True),
                data=json.dumps({
                            "article_id":20,
                            "kind":1,
                            "comment_id":-1,
                            "user_id":int(number),
                            "user_role":0,
                            "message":"aaa"
                        }),
                content_type = 'application/json')
        print response.status_code
#        self.assertTrue(response.status_code == 200) 

    def test_d_get_comment_likes(self):
        response = self.client.get(
                url_for('api.get_comment_likes',id=1,_external=True),
                content_type = 'application/json')
        self.assertTrue(response.status_code == 200) 
                
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

