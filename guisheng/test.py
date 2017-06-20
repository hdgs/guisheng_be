#coding:utf-8
import unittest
from flask import current_app, url_for,jsonify
from guisheng_app import create_app
from flask_sqlalchemy import SQLAlchemy
import random
import json
from flask_sqlalchemy import SQLAlchemy

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
    def test_register(self):
        reponse = self.client.post(
                url_for('api_1_0')

