import unittest
from guisheng_app import create_app,rds
from flask import current_app, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import json
import base64

TOKEN = str(0)
ID = int(0)
ADMIN_NAME = str('test1')
ADMIN_PSWORD = str('test1')
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

    
    #Test register
    def test_a_register(self):
        response = self.client.post(
            url_for('api.register',_external=True),
            data = json.dumps({
                    "username":str(number),
                    "email":str(number),
                    "password":str(number)}),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
        global ID 
        ID = json.loads(response.data)['created']
        
    #Test login
    def test_b_login(self):
        response = self.client.post(
            url_for('api.login',_external=True),
            data = json.dumps({
                    "password":ADMIN_PSWORD,
                    "email":ADMIN_PSWORD
                    }),
            content_type = 'application/json')
        s = json.loads(response.data)['token']
        global ID
        ID = json.loads(response.data)['uid']
        global TOKEN
        TOKEN = s
        global b64token
        b64token = str(base64.b64encode(TOKEN))
        self.assertTrue(response.status_code == 200)
    
    #Test get_news
    def test_d_get_news(self):
        response = self.client.post(
            url_for('api.get_news',id=news_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "my_id":int(ID) 
                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test recommend_news
    def test_d_recommend_news(self):
        response = self.client.post(
            url_for('api.recommend_news',_external=True),
            data = json.dumps({ 
                "article_id":int(news_id),
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

    #Test show_news
    def test_d_show_news(self):
        response = self.client.get(
            url_for('api.show_news',id=news_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_news
    def test_c_add_news(self):
        response = self.client.post(
            url_for('api.add_news',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
                "author":str(ADMIN_NAME),
                "title":str(number),
                "saver":ID,
                "tags":["test"],
                "img_url":"test",
                "editor":"test"
            }),
            content_type = 'application/json')
        global news_id
        news_id = json.loads(response.data)['id']
        self.assertTrue(response.status_code == 201)
    #Test update_news
    def test_d_update_news(self):
        response = self.client.put(
            url_for('api.update_news',id=news_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({
                    "title":"test2",
                    "author":ADMIN_NAME,
                    "editor":"test2",
                    "saver":ID,
                    "tags":["test"]
                    }),
            content_type = 'application/json')

    #Test get_news_body
    def test_d_get_news_body(self):
        response = self.client.get(
            url_for('api.get_news_body',id=news_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_news_body
    def test_d_update_news_body(self):
        response = self.client.put(
            url_for('api.update_news_body',id=news_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "saver":ID,
                "body":"testbody"
                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_news
    def test_k_delete_news(self):
        response = self.client.delete(
            url_for('api.delete_news',id=news_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_pic
    def test_d_get_pic(self):
        response = self.client.post(
            url_for('api.get_pic',id=pics_id,_external=True),
            data = json.dumps({
                "my_id":int(ID)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test recommend_pics
    def test_d_recommend_pics(self):
        response = self.client.post(
            url_for('api.recommend_pics',_external=True),
            data = json.dumps({
                "article_id":int(pics_id)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test show_pic
    def test_d_show_pic(self):
        response = self.client.get(
            url_for('api.show_pic',id=pics_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_pics
    def test_c_add_pics(self):
        response = self.client.post(
            url_for('api.add_pics',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "title":str(number),
                "tags":["test"],
                "author":ADMIN_NAME,
                "img_url":str(number),
                "description":"test",
                "saver":ID,
                "editor":"test"
                }),
            content_type = 'application/json')
        global pics_id
        pics_id = json.loads(response.data)['id']
        self.assertTrue(response.status_code == 201)
    #Test update_pics
    def test_d_update_pics(self):
        response = self.client.put(
            url_for('api.update_pics',id=pics_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "title":str(number),
                "tags":["test"],
                "author":ADMIN_NAME,
                "saver":ID,
                "editor":"test"
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_pics
    def test_f_delete_pics(self):
        response = self.client.delete(
            url_for('api.delete_pics',id=pics_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_one_pic
    def test_e_delete_one_pic(self):
        response = self.client.delete(
            url_for('api.delete_one_pic',id=pics_id,index=0,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_interaction
    def test_d_get_interaction(self):
        response = self.client.post(
            url_for('api.get_interaction',id=inte_id,_external=True),
            data=json.dumps({
                    "my_id":-1,
                 }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

    #Test recommend_interactions
    def test_d_recommend_interactions(self):
        response = self.client.post(
            url_for('api.recommend_interactions',_external=True),
            data = json.dumps({
                "article_id":inte_id,
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_tea
    def test_d_get_tea(self):
        response = self.client.get(
            url_for('api.get_tea',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test show_interaction
    def test_d_show_interaction(self):
        response = self.client.get(
            url_for('api.show_interaction',id=inte_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_interaction
    def test_c_add_interaction(self):
        response = self.client.post(
            url_for('api.add_interaction',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({
                "title":str(number),
                "tags":["test"],
                "author":ADMIN_NAME,
                "description":"test",
                "editor":"test",
                "saver":ID,
                "img_url":"test",
                "flag":1
            }),
            content_type = 'application/json')
        global inte_id
        inte_id = json.loads(response.data)['id']
        self.assertTrue(response.status_code == 201)
    #Test update_interaction
    def test_d_update_interaction(self):
        response = self.client.put(
            url_for('api.update_interaction',id=inte_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({
                "title":str(number),
                "author":ADMIN_NAME,
                "tags":["test"],
                "description":"test",
                "img_url":"test",
                "saver":ID,
                "editor":"Humbert",
                "flag":0
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_interaction_body
    def test_d_get_interaction_body(self):
        response = self.client.get(
            url_for('api.get_interaction_body',id=inte_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_interaction_body
    def test_d_update_interaction_body(self):
        response = self.client.put(
            url_for('api.update_interaction_body',id=inte_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({
                "saver":ID,
                "body":"test"
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_interaction
    def test_g_delete_interaction(self):
        response = self.client.delete(
            url_for('api.delete_interaction',id=inte_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test set_tea
    def test_c_set_tea(self):
        response = self.client.post(
            url_for('api.set_tea',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({
                "article_id":inte_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_profile
    def test_c_get_profile(self):
        response = self.client.post(
            url_for('api.get_profile',id=ID,_external=True),
            data = json.dumps({
                    "my_id":int(ID)
                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test edit_profile
    def test_c_edit_profile(self):
        response = self.client.put(
            url_for('api.edit_profile',id=int(ID),_external=True),
            data=json.dumps({
                "img_url":"test",
                "name":ADMIN_NAME,
                "weibo":"test",
                "introduction":"test"
                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_works
    def test_c_get_works(self):
        response = self.client.get(
            url_for('api.get_works',id=ID,_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_collections
    def test_d_get_collections(self):
        response = self.client.get(
            url_for('api.get_collections',id=ID,_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test suggeston
    def test_c_suggeston(self):
        response = self.client.post(
            url_for('api.suggeston',id=ID,_external=True),
            data=json.dumps({
                "body":"test",
                "contact_information":"test"
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test collect
    def test_d_collect(self):
        response = self.client.post(
            url_for('api.collect',_external=True),
            data = json.dumps({ 
                "my_id":ID,
                "kind":1,
                "article_id":news_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test collect_delete
    def test_e_collect_delete(self):
        response = self.client.post(
            url_for('api.collect_delete',_external=True),
            data = json.dumps({ 
                "my_id":ID,
                "kind":1,
                "article_id":news_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_comments
    def test_e_get_comments(self):
        response = self.client.get(
            url_for('api.get_comments',kind=1,article_id=news_id,_external=True),
            content_type = 'application/json')
        global comment_id
        comment_id = json.loads(response.data)[0]["comment_id"]
        self.assertTrue(response.status_code == 200)
    #Test create_comments
    def test_d_create_comments(self):
        response = self.client.post(
            url_for('api.create_comments',_external=True),
            data = json.dumps({
                "kind":1,
                "article_id":news_id,
                "comment_id":int(number),
                "message":"test",
                "user_id":int(ID)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_comment_likes
    def test_f_get_comment_likes(self):
        response = self.client.get(
            url_for('api.get_comment_likes',id=comment_id,_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_comment
    def test_h_delete_comment(self):
        response = self.client.delete(
            url_for('api.delete_comment',id=comment_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test main_page
    def test_c_main_page(self):
        response = self.client.get(
            url_for('api.main_page',_external=True,kind=0,page=0,count=0),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test list
    def test_c_list(self):
        response = self.client.get(
            url_for('api.list',kind=1,page=1,count=1,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test publish pic
    def test_c_z_publish_pics(self):
        response = self.client.post(
            url_for('api.publish',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
               "publisher":ID,
               "kind":2,
               "post_id":pics_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test publish news
    def test_c_z_publish_news(self):
        response = self.client.post(
            url_for('api.publish',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
                "publisher":ID,
                "kind":1,
                "post_id":news_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test publish interactions
    def test_c_z_publish_interactions(self):
        response = self.client.post(
            url_for('api.publish',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
                "publisher":ID,
                "kind":4,
                "post_id":inte_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test publish article
    def test_c_z_publish_articles(self):
        response = self.client.post(
            url_for('api.publish',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
               "publisher":ID,
               "kind":3,
               "post_id":art_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test unpublish
    def test_d_z_unpublish(self):
        response = self.client.post(
            url_for('api.unpublish',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({
                "kind":1,
                "post_id":news_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

    
    #Test change_to_author
    def test_c_a_change_to_author(self):
        response = self.client.post(
            url_for('api.change_to_author',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "id":int(ID)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test change_to_common_user
    def test_c_b_change_to_common_user(self):
        response = self.client.post(
            url_for('api.change_to_common_user',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "id":int(ID)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_article
    def test_f_get_article(self):
        response = self.client.post(
            url_for('api.get_article',id=art_id,_external=True),
            data = json.dumps({ 
                "my_id":-1
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test recommend_articles
    def test_f_recommend_articles(self):
        response = self.client.post(
            url_for('api.recommend_articles',_external=True),
            data = json.dumps({ 
                "article_id":art_id
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test show_article
    def test_f_show_article(self):
        response = self.client.get(
            url_for('api.show_article',id=art_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_article
    def test_c_add_article(self):
        response = self.client.post(
            url_for('api.add_article',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
                "title":str(number),
                "author":ADMIN_NAME,
                "author_id":int(ID),
                "tags":["test"],
                "img_url":"test",
                "description":"test",
                "music_url":"test",
                "music_title":"test",
                "music_img_url":"test",
                "singer":"Queen",
                "film_url":"Leon The Professor",
                "film_img_url":"test",
                "saver":ID,
                "editor":"test",
                "scores":float(1),
                "flag":int(1)
            }),
            content_type = 'application/json')
        global art_id
        art_id = json.loads(response.data)['id']
        self.assertTrue(response.status_code == 201)

    #Test update_article
    def test_f_update_article(self):
        response = self.client.put(
            url_for('api.update_article',id=art_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
                "title":str(number),
                "author":ADMIN_NAME,
                "author_id":int(ID),
                "tags":["test"],
                "img_url":"test",
                "description":"test",
                "music_url":"test",
                "music_title":"test",
                "music_img_url":"test",
                "singer":"Queen",
                "film_url":"Leon The Professor",
                "film_img_url":"test",
                "editor":"test",
                "saver":ID,
                "scores":float(2),
                "flag":int(1)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_article_body
    def test_f_get_article_body(self):
        response = self.client.get(
            url_for('api.get_article_body',id=art_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_article_body
    def test_f_update_article_body(self):
        response = self.client.put(
            url_for('api.update_article_body',id=art_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data=json.dumps({
                "saver":ID,
                "body":"test"
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_article
    def test_k_delete_article(self):
        response = self.client.delete(
            url_for('api.delete_article',id=art_id,_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test light
    def test_c_light(self):
        response = self.client.post(
            url_for('api.light',_external=True),
            data=json.dumps({
                        "article_id":news_id,
                        "kind":1,
                        "like_degree":1
                        }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test like_picture
    def test_c_like_picture(self):
        response = self.client.post(
            url_for('api.like_picture',_external=True),
            data=json.dumps({
                        "picture_id":pics_id
                        }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test like_comment
    def test_f_like_comment(self):
        response = self.client.post(
            url_for('api.like_comment',_external=True),
            data=json.dumps({
                        "comment_id":comment_id 
                                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_everydaypic
    def test_d_get_everydaypic(self):
        response = self.client.get(
            url_for('api.get_everydaypic',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_everydaypic
    def test_c_add_everydaypic(self):
        response = self.client.post(
            url_for('api.add_everydaypic',_external=True),
            headers = {
                "Authorization":"Basic "+b64token,
            },
            data = json.dumps({ 
                "img_url":"test"+str(number),
                "climate":1,
                "data":str(number)
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 201)
