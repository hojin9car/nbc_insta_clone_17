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


# 로그인 api
@bp.route('/api/login', methods=['POST'])
@login_not_required
def login():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'id': data['id_give']})

    if not is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 존재하지 않아요.'})
    if pw_hashed != is_it['password']:
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다.'})

    payload = {
        'id': is_it['id'],
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({'result': 'success', 'token': token})


# 회원가입
@bp.route('/api/join', methods=['POST'])
@login_not_required
def join():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'id': data['id_give']})

    if is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 이미 존재 합니다.'})
    db.user.insert_one(
        {'id': data['id_give'], 'nick': data['nick_give'], 'password': pw_hashed, 'name': data['name_give'],
         'social_only': False})
    return jsonify({'result': 'success', 'msg': '아이디를 성공적으로 생성하였습니다.'})
