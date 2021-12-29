from flask import Flask, render_template,request,redirect,url_for, jsonify
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
    print(user)

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


#로그인 페이지
@app.route('/login')
def login_page():
    #로그인 되어 있다면 홈으로 이동
    logged = sign_in()
    if logged == 'ok':
        return redirect(url_for('home'))
    return render_template('lol.html')

#회원가입 페이지
@app.route('/join')
def join_page():
    #로그인 되어 있다면 홈으로 이동
    logged = sign_in()
    if logged == 'ok':
        return redirect(url_for('home'))
    return render_template('join.html')

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

    print(is_it['user_id'])
    payload = {
        'id' : is_it['user_id'],
        
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({'result': 'success', 'token': token})

# 홈 화면
@app.route('/home')
def home():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()
    if logged == 'bad':
        return redirect(url_for('login_page'))
    user = get_user()
    print(user)
    return render_template('home.html')



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

