from flask import Flask, render_template,request,redirect,url_for,make_response ,jsonify
import requests
from pymongo import MongoClient
import hashlib
import jwt


SECRET_KEY = 'sparta'

client = MongoClient('localhost',27017)
db = client.dbProject1

app = Flask(__name__)




# 로그인 했는지 안했는지 확인.
def sign_in():
    token_receive = request.cookies.get('token')
    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return 'ok'
    except jwt.ExpiredSignatureError:
        return 'bad'
    except jwt.exceptions.DecodeError:
        return 'bad'

#현재 로그인 된 유저의 정보를 return
def get_user():
    token_receive = request.cookies.get('token')
    user_info =  jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user = db.user.find_one({'user_id':user_info['id']},{'_id':0})
    return user

#처음 /에 접속시 로그인 안되어있으면 /로 이동, 로그인 되어있으면 /home으로 이동
@app.route('/')
def init():
    token_receive = request.cookies.get('token')
    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return redirect(url_for('home'))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page"))
# 홈 화면
@app.route('/home')
def home():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()
    if logged == 'bad':
        return redirect(url_for('login_page'))
    user = get_user()

    return render_template('home.html')


#회원가입 페이지
@app.route('/join')
def join_page():
    #로그인 되어 있다면 홈으로 이동
    logged = sign_in()
    if logged == 'ok':
        return redirect(url_for('home'))
    return render_template('join.html')

#아이디 중복확인
@app.route('/api/isit')
def id_isit():
    id = request.args.get('id')
    is_it = db.user.find_one({'user_id':id})

    if is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 이미 존재 합니다.'})
    else:
        return jsonify({'result': 'success', 'msg': '사용하셔도 좋습니다.'})


#회원가입
@app.route('/api/join',methods=['POST'])
def join():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'user_id':data['id_give']})

    if is_it:
        return jsonify({'result': 'fail', 'msg':'아이디가 이미 존재 합니다.'})
    db.user.insert_one({'user_id':data['id_give'],'user_nick':data['nick_give'],'user_pw':pw_hashed,'social_only':False})
    return jsonify({'result': 'success', 'msg':'아이디를 성공적으로 생성하였습니다.'})

#로그인 페이지
@app.route('/login')
def login_page():
    #로그인 되어 있다면 홈으로 이동
    logged = sign_in()
    if logged == 'ok':
        return redirect(url_for('home'))
    return render_template('lol.html')


#로그인 api
@app.route('/api/login',methods=['POST'])
def login():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'user_id':data['id_give']})
    if not is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 존재하지 않아요.'})
    if pw_hashed != is_it['user_pw']:
        return jsonify({'result': 'fail', 'msg':'비밀번호가 일치하지 않습니다.'})


    payload = {
        'id' : is_it['user_id'],

    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({'result': 'success', 'token': token})




@app.route('/login/kakao')
def login_kakao():
    code = request.args.get('code')
    redirect_uri = 'http://localhost:5000/login/kakao'
    client_id = '7f535c9ad05fa8ee370a9eb9318421c7'
    url="https://kauth.kakao.com/oauth/token"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    resp = requests.post(
        url=url,
        headers=headers,
        data={'grant_type':"authorization_code",'client_id':client_id,'redirect_uri':redirect_uri,'code':code}
    )
    #토큰 얻어옴

    access_token = resp.json()['access_token']
    url = 'https://kapi.kakao.com/v2/user/me'
    headers.update({'Authorization': f'Bearer {access_token}'})
    resp = requests.post(
        url=url,
        headers=headers,
    )
    #토큰을 바탕으로 유저정보 얻어옴
    user_info = resp.json()
    is_it = db.user.find_one({'user_id':user_info['id']})
    #아이디가 존재하면 아이디 생략 x
    if not is_it:
        db.user.insert_one({'user_id': user_info['id'], 'user_nick': user_info['properties']['nickname'], 'social_only': True})
    #토큰 생성후 쿠키 부여
    payload = {'id': user_info['id']}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('token',token)
    return resp



if __name__ == '__main__':
    app.run(debug=True)