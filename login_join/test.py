from flask import Flask, render_template,request,redirect,url_for, jsonify
import requests
from pymongo import MongoClient
import hashlib
import jwt


SECRET_KEY = 'sparta'

client = MongoClient('localhost',27017)
db = client.dbProject1

app = Flask(__name__)


def home():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload['id']})
        return user_info
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))




@app.route('/')
def hello():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload['id']})
        return render_template('index.html', user=user_info)
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page"))



@app.route('/login')
def login_page():
    return render_template('lol.html')
@app.route('/join')
def join_page():
    return render_template('join.html')

@app.route('/api/login',methods=['POST'])
def login():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'user_id':data['id_give']})
    if not is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 존재하지 않아요.'})
    if pw_hashed != is_it['user_pw']:
        return jsonify({'result': 'fail', 'msg':'비밀번호가 일치하지 않습니다.'})

    print(is_it['user_id'])
    payload = {
        'id' : is_it['user_id'],

    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({'result': 'success', 'token': token})


# @app.route('/login/github/callback')
# def login_github():
#     code = request.args.get('code')
#
#
#
#     client_secret = '31dea26d2ca436678af09e88085248358c8e8e06'
#
#
#     client_id = '94debc0ee29ed22a1f74'
#     # redirect_uri = 'localhost:5000/login/github/callback'
#     params = {'code': code, 'client_id': '94debc0ee29ed22a1f74', 'client_secret':client_secret}
#     print('token mae')
#     # "Content-Type": "application/x-www-form-urlencoded",
#     # "Cache-Control": "no-cache",
#
#
#     headers = {'Content-Type': 'application/json'}
#     a = requests.get(
#         url="https://github.com/login/oauth/authorize",
#         headers={
#             "Accept": "application/json",
#             "Cache-Control": "no-cache",
#         },
#         params=params
#     )
#
#     print('token ato')
#
#     print(a)
#     print('1')
#     return

@app.route('/api/join',methods=['POST'])
def join():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'user_id':data['id_give']})
    print(is_it)
    if is_it:
        return jsonify({'result': 'fail', 'msg':'아이디가 이미 존재 합니다.'})
    db.user.insert_one({'user_id':data['id_give'],'user_nick':data['nick_give'],'user_pw':pw_hashed})
    return jsonify({'result': 'success', 'msg':'아이디를 성공적으로 생성하였습니다.'})

if __name__ == '__main__':
    app.run(debug=True)

