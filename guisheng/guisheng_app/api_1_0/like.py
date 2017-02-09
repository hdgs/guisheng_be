# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Light
from . import api


