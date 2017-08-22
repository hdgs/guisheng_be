#coding:utf-8

import os
from flask import Flask,request,send_from_directory,jsonify
import time
from qiniu import Auth,put_file,etag
import qiniu.config
from . import api

UPLOAD_FOLDER='guisheng_pics'
ALLOWED_EXTENSIONS=set(['png','jpg','jpeg','svg'])
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
BUCKET_NAME = 'guishengapp'

q = Auth(ACCESS_KEY, SECRET_KEY)

@api.route('/guisheng/upload_pics/',methods = ['GET','POST'])
def upload_pics():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            fname = '.'.join([str(int(time.time())),file.filename.split('.',1)[1]])
            file.save(os.path.join(UPLOAD_FOLDER,fname))
            localfile = ''.join([UPLOAD_FOLDER,'/',fname])
            key = '.'.join([str(int(time.time())),file.filename.split('.',1)[1]])
            token = q.upload_token(BUCKET_NAME, key, 3600)
            ret, info = put_file(token, key, localfile)
            pic_url = "".join(["http://7xqk8r.com1.z0.glb.clouddn.com/",key])
            os.remove(os.path.join(UPLOAD_FOLDER,fname))
            return jsonify({
                'pic_url':pic_url
            })

@api.route('/guisheng_pics/<filename>/',methods = ['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

