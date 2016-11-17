# coding: utf-8
from . import main
from flask import render_template,jsonify,Response
import json

@main.route('/',methods=['GET','POST'])
def index():
    return "hi"
