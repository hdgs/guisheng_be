import unittest
from guisheng_app import create_app
from flask import current_app, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import json
import base64

TOKEN = str(0)
ID = int(0)
ADMIN_ID = str(1)
ADMIN_PSWORD = str(535)
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
        global TOKEN
        TOKEN = s
        #global b64token
        #b64token = base64.b64encode(TOKEN)
        self.assertTrue(response.status_code == 200)
    
    #Test get_news
    def test_c_get_news(self):
        response = self.client.post(
            url_for('api.get_news',id=ID,_external=True),
            data=json.dumps({
                "my_id":int(number) 
                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test recommend_news
    def test_c_recommend_news(self):
        response = self.client.post(
            url_for('api.recommend_news',_external=True),
            data = json.dumps({ 
                "article_id":int(1),
            }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

    #Test show_news
    def test_c_show_news(self):
        response = self.client.get(
            url_for('api.show_news',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_news
    def test_c_add_news(self):
        response = self.client.post(
            url_for('api.add_news',_external=True),
            headers = {
                "Authorization":"Basic base64("+TOKEN+":)",
                "Accept" : "application/json" ,
                "Content_Type" :"application/json"
            },
            data = json.dumps({ 
                "title":"test",
                "tags":["test"],
                "name":"test",
                "img_url":"test",
                "editor":"test"
            }),
            content_type = 'application/json')
        print response.status_code
        #self.assertTrue(response.status_code == 200)
    #Test update_news
    def test_c_update_news(self):
        response = self.client.XXXX(
            url_for('api.update_news',_external=True),
            content_type = 'application/json')

    #Test get_news_body
    def test_c_get_news_body(self):
        response = self.client.get(
            url_for('api.get_news_body',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_news_body
    def test_c_update_news_body(self):
        response = self.client.XXXX(
            url_for('api.update_news_body',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_news
    def test_c_delete_news(self):
        response = self.client.XXXX(
            url_for('api.delete_news',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_pic
    def test_c_get_pic(self):
        response = self.client.post(
            url_for('api.get_pic',id=ID,_external=True),
            data = json.dumps({"my_id":ID}),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test recommend_pics
    def test_c_recommend_pics(self):
        response = self.client.post(
            url_for('api.recommend_pics',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test show_pic
    def test_c_show_pic(self):
        response = self.client.get(
            url_for('api.show_pic',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_pics
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
        self.assertTrue(response.status_code == 200)
    #Test update_pics
    def test_c_update_pics(self):
        response = self.client.XXXX(
            url_for('api.update_pics',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_pics
    def test_c_delete_pics(self):
        response = self.client.XXXX(
            url_for('api.delete_pics',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_one_pic
    def test_c_delete_one_pic(self):
        response = self.client.XXXX(
            url_for('api.delete_one_pic',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_interaction
    def test_c_get_interaction(self):
        response = self.client.post(
            url_for('api.get_interaction',id=1,_external=True),
            data=({
                    "my_id":1,
                 }),
            content_type = 'application/json')
        print response.status_code
        #self.assertTrue(response.status_code == 200)

    #Test recommend_interactions
    def test_c_recommend_interactions(self):
        response = self.client.post(
            url_for('api.recommend_interactions',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_tea
    def test_c_get_tea(self):
        response = self.client.get(
            url_for('api.get_tea',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test show_interaction
    def test_c_show_interaction(self):
        response = self.client.get(
            url_for('api.show_interaction',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_interaction
    def test_c_add_interaction(self):
        response = self.client.post(
            url_for('api.add_interaction',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_interaction
    def test_c_update_interaction(self):
        response = self.client.get(
            url_for('api.update_interaction',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_interaction_body
    def test_c_get_interaction_body(self):
        response = self.client.get(
            url_for('api.get_interaction_body',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_interaction_body
    def test_c_update_interaction_body(self):
        response = self.client.XXXX(
            url_for('api.update_interaction_body',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_interaction
    def test_c_delete_interaction(self):
        response = self.client.get(
            url_for('api.delete_interaction',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test set_tea
    def test_c_set_tea(self):
        response = self.client.post(
            url_for('api.set_tea',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_token
    def test_c_get_token(self):
        response = self.client.get(
            url_for('api.get_token',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_profile
    def test_c_get_profile(self):
        response = self.client.post(
            url_for('api.get_profile',id=ID,_external=True),
            data = json.dumps({
                    "my_id":ID
                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test edit_profile
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
    #Test get_works
    def test_c_get_works(self):
        response = self.client.get(
            url_for('api.get_works',id=ID,_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_collections
    def test_c_get_collections(self):
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
    def test_c_collect(self):
        response = self.client.post(
            url_for('api.collect',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test collect_delete
    def test_c_collect_delete(self):
        response = self.client.post(
            url_for('api.collect_delete',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_comments
    def test_c_get_comments(self):
        response = self.client.get(
            url_for('api.get_comments',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test create_comments
    def test_c_create_comments(self):
        response = self.client.post(
            url_for('api.create_comments',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_comment_likes
    def test_c_get_comment_likes(self):
        response = self.client.XXXX(
            url_for('api.get_comment_likes',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_comment
    def test_c_delete_comment(self):
        response = self.client.get(
            url_for('api.delete_comment',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test main_page
    def test_c_main_page(self):
        response = self.client.get(
            url_for('api.main_page',_external=True,kind=0,page=0,count=0),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test search
    def test_c_search(self):
        response = self.client.post(
            url_for('api.search',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_hottag
    def test_c_get_hottag(self):
        response = self.client.get(
            url_for('api.get_hottag',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test list
    def test_c_list(self):
        response = self.client.get(
            url_for('api.list',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test publish
    def test_c_publish(self):
        response = self.client.post(
            url_for('api.publish',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test unpublish
    def test_c_unpublish(self):
        response = self.client.post(
            url_for('api.unpublish',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

    
    #Test change_to_author
    def test_c_change_to_author(self):
        response = self.client.get(
            url_for('api.change_to_author',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test change_to_common_user
    def test_c_change_to_common_user(self):
        response = self.client.get(
            url_for('api.change_to_common_user',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_article
    def test_c_get_article(self):
        response = self.client.post(
            url_for('api.get_article',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test recommend_articles
    def test_c_recommend_articles(self):
        response = self.client.post(
            url_for('api.recommend_articles',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test show_article
    def test_c_show_article(self):
        response = self.client.get(
            url_for('api.show_article',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_article
    def test_c_add_article(self):
        response = self.client.post(
            url_for('api.add_article',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_article
    def test_c_update_article(self):
        response = self.client.XXXX(
            url_for('api.update_article',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_article_body
    def test_c_get_article_body(self):
        response = self.client.get(
            url_for('api.get_article_body',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test update_article_body
    def test_c_update_article_body(self):
        response = self.client.XXXX(
            url_for('api.update_article_body',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test delete_article
    def test_c_delete_article(self):
        response = self.client.get(
            url_for('api.delete_article',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test light
    def test_c_light(self):
        response = self.client.post(
            url_for('api.light',_external=True),
            data=json.dumps({
                        "article_id":1,
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
                        "picture_id":1 
                        }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test like_comment
    def test_c_like_comment(self):
        response = self.client.post(
            url_for('api.like_comment',_external=True),
            data=json.dumps({
                        "comment_id":1 
                                }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test get_everydaypic
    def test_c_get_everydaypic(self):
        response = self.client.get(
            url_for('api.get_everydaypic',_external=True),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
    #Test add_everydaypic
    def test_c_add_everydaypic(self):
        response = self.client.post(
            url_for('api.add_everydaypic',_external=True),
            data = json.dump({ }),
            content_type = 'application/json')
        self.assertTrue(response.status_code == 200)
