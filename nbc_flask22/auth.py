from flask import render_template
from flask import request
from flask import Blueprint
from flask import make_response
from flask import jsonify
from flask import url_for

from flask import redirect
from functools import wraps

import requests
import jwt
import hashlib
# import requests

import db

db = db.get_db()

SECRET_KEY = 'sparta'

bp = Blueprint("auth", __name__)


# 아이디 중복확인
@bp.route('/api/isit')
def id_isit():
    id = request.args.get('id')
    is_it = db.user.find_one({'id':id})

    if is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 이미 존재 합니다.'})
    else:
        return jsonify({'result': 'success', 'msg': '사용하셔도 좋습니다.'})


def login_required(f):
    @wraps(f)
    def wrap(**kwargs):
        token_receive = request.cookies.get('token')
        try:
            jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            return f(**kwargs)
        except jwt.ExpiredSignatureError:
            return redirect('/login')
        except jwt.exceptions.DecodeError:
            return redirect('/login')

    return wrap


# 현재 로그인 된 유저의 정보를 return
def get_user():
    token_receive = request.cookies.get('token')
    user_info = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user = db.user.find_one({'id': user_info['id']})
    print('user', user)
    return user


# 회원가입 페이지
@bp.route('/join', methods=['GET'])
def join_page():
    # 로그인 되어 있다면 홈으로 이동
    return render_template('join.html')


# 로그인 페이지
@bp.route('/login')
def login_page():
    # 로그인 되어 있다면 홈으로 이동
    return render_template('lol.html')


# 로그인 api
@bp.route('/api/login', methods=['POST'])
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


@bp.route('/login/github')
def login_github():
    code = request.args.get('code')
    url = 'https://github.com/login/oauth/access_token'
    client_secret = '0775e84c22ce79ebdc1ef85ca5f9293f599e057e'
    client_id = '94debc0ee29ed22a1f74'
    headers = {'Accept': 'application/json'}

    resp = requests.post(
        url=url,
        headers=headers,
        data={'client_id': client_id, 'client_secret': client_secret, 'code': code}
    )

    access_token = resp.json()['access_token']
    url = 'https://api.github.com/user'
    headers = {'Authorization': f'token {access_token}'}
    resp = requests.get(
        url=url,
        headers=headers,
    )
    user_info = resp.json()
    is_it = db.user.find_one({'id': user_info['id']})

    # 아이디가 존재하면 아이디 생략 x
    if not is_it:
        db.user.insert_one(
            {'id': user_info['id'], 'nick': user_info['name'], 'name': user_info['name'], 'social_only': True})
    # 토큰 생성후 쿠키 부여
    payload = {'id': user_info['id']}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    resp = make_response(redirect('/'))
    resp.set_cookie('token', token)
    return resp


@bp.route('/login/kakao')
def login_kakao():
    code = request.args.get('code')
    redirect_uri = 'http://hojin9car.shop/login/kakao'
    client_id = '7f535c9ad05fa8ee370a9eb9318421c7'
    url = "https://kauth.kakao.com/oauth/token"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    resp = requests.post(
        url=url,
        headers=headers,
        data={'grant_type': "authorization_code", 'client_id': client_id, 'redirect_uri': redirect_uri, 'code': code}
    )
    # 토큰 얻어옴

    access_token = resp.json()['access_token']
    url = 'https://kapi.kakao.com/v2/user/me'
    headers.update({'Authorization': f'Bearer {access_token}'})
    resp = requests.post(
        url=url,
        headers=headers,
    )
    # 토큰을 바탕으로 유저정보 얻어옴
    user_info = resp.json()
    is_it = db.user.find_one({'id': user_info['id']})
    # 아이디가 존재하면 아이디 생략 x
    if not is_it:
        db.user.insert_one({'id': user_info['id'], 'nick': user_info['properties']['nickname'],
                            'name': user_info['properties']['nickname'], 'social_only': True})
    # 토큰 생성후 쿠키 부여
    payload = {'id': user_info['id']}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    resp = make_response(redirect(url_for('/')))
    resp.set_cookie('token', token)
    return resp
