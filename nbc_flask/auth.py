from flask import Flask
from flask import render_template
from flask import request
from flask import Blueprint
from flask import make_response
from flask import jsonify
from bson.objectid import ObjectId
from flask import redirect
from functools import wraps

import jwt
import datetime as dt
import hashlib
# import requests

import db

db = db.get_db()

SECRET_KEY = 'sparta'

bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def wrap(**kwargs):
        token_receive = request.cookies.get('token')
        try:
            jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            return f(**kwargs)
        except jwt.ExpiredSignatureError:
            return 'bad'
        except jwt.exceptions.DecodeError:
            return 'bad'
    return wrap


def login_not_required(f):
    @wraps(f)
    def wrap(**kwargs):
        if request.cookies.get('token') is True:
            return redirect('/')
        else:
            return f(**kwargs)
    return wrap


# 현재 로그인 된 유저의 정보를 return
def get_user():
    token_receive = request.cookies.get('token')
    user_info = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user = db.user.find_one({'id': user_info['id']})
    return user


# 회원가입 페이지
@bp.route('/join', methods=['GET'])
@login_not_required
def join_page():
    # 로그인 되어 있다면 홈으로 이동
    return render_template('join.html')


# 로그인 페이지
@bp.route('/login')
@login_not_required
def login_page():
    # 로그인 되어 있다면 홈으로 이동
    return render_template('lol.html')


