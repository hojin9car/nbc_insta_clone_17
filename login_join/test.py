from flask import Flask, render_template,request,redirect,url_for,make_response ,jsonify
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib
import jwt
import datetime as dt
from bson.json_util import dumps

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
    user = db.user.find_one({'id':user_info['id']})
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
    content_list = list(db.contents.find({}).sort([('write_time',-1)]))

    return render_template('home.html',contents=content_list)

#글 수정 화면
@app.route('/edit_write/<id>')
def edit_write(id):
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()

    if logged == 'bad':
        return redirect(url_for('login_page'))
    content = db.contents.find_one({'_id': ObjectId(id)})
    return render_template('edit_write.html', content=content)

#글 수정 화면
@app.route('/api/edit',methods = ['POST'])
def api_edit():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()
    if logged == 'bad':
        return redirect(url_for('login_page'))
    data = request.json
    id = data['id']
    text_area = data['text-area']

    db.contents.update_one({'_id': ObjectId(id)},{ '$set': { 'content': text_area, 'write_edit_time': dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}} )
    return jsonify({'result':'success'})


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
    is_it = db.user.find_one({'id':id})

    if is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 이미 존재 합니다.'})
    else:
        return jsonify({'result': 'success', 'msg': '사용하셔도 좋습니다.'})


#회원가입
@app.route('/api/join',methods=['POST'])
def join():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'id':data['id_give']})

    if is_it:
        return jsonify({'result': 'fail', 'msg':'아이디가 이미 존재 합니다.'})
    db.user.insert_one({'id':data['id_give'],'nick':data['nick_give'],'password':pw_hashed,'name':data['name_give'],'social_only':False})
    return jsonify({'result': 'success', 'msg':'아이디를 성공적으로 생성하였습니다.'})

#로그인 페이지
@app.route('/login')
def login_page():
    #로그인 되어 있다면 홈으로 이동
    logged = sign_in()
    if logged == 'ok':
        return redirect(url_for('home'))
    return render_template('lol.html')

#글 작성 화면이동
@app.route('/new_write')
def new_write():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()
    if logged == 'bad':
        return redirect(url_for('login_page'))
    return render_template('new_write.html')

#마이페이지 이동
@app.route('/my_main')
def my_main():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()
    if logged == 'bad':
        return redirect(url_for('login_page'))
    user = get_user()
    content_list = list(db.contents.find({}).sort([('write_time', -1)]))
    selected_list = []
    for i in content_list:
        if i['user._id'] == ObjectId(user['_id']):
            selected_list.append(i)


    return render_template('my_main.html', contents=selected_list)

@app.route('/api/delete',methods=['PUT'])
def api_delete():
    #현재 로그인 사용자 정보
    user = get_user()
    #글에서 글 작성자 아이디를 가져옴
    id = request.args.get('id')
    print(id)
    #가져온 id값은 str이므로 db에서 찾을 수가 없다. 따라서 ObjectId로 바꿔주어야함
    id = ObjectId(id)
    #글의 정보를 가져온 뒤 글의 작성자를 비교해야함
    one = db.contents.find_one({'_id': id})
    print(one['_id'])
    # 현재 로그인 사용자와 글작성자가 같아야지 진행이 가능
    if one['user._id'] != user['_id']:
        #같지 않다면 홈화면 보이게함 이건 나중에 수정
        return redirect(url_for('home'))
    db.contents.delete_one({'_id':one['_id']})

    return jsonify({'result':'success'})



#글 작성
@app.route('/api/write',methods=['POST'])
def api_wirte():
    #html에서 가져온 정보
    data = request.json
    # 현재 로그인 사용자 정보
    writer = get_user()
    # 글 작성
    new_one = db.contents.insert_one({'user.nick':writer['nick'],'user._id':writer['_id'],'like':0,\
    'comments':0,'write_time':dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초"),'write_edit_time':'','img':'','content':data['text_give']})
    #글 작성한 것 가져오기 new_one사용 안됨
    content = db.contents.find_one({'_id':new_one.inserted_id})

    return jsonify( {'result': 'success'})





#로그인 api
@app.route('/api/login',methods=['POST'])
def login():
    data = request.json
    pw_hashed = hashlib.sha256(data['pass_give'].encode('utf-8')).hexdigest()
    is_it = db.user.find_one({'id':data['id_give']})
    if not is_it:
        return jsonify({'result': 'fail', 'msg': '아이디가 존재하지 않아요.'})
    if pw_hashed != is_it['password']:
        return jsonify({'result': 'fail', 'msg':'비밀번호가 일치하지 않습니다.'})


    payload = {
        'id' : is_it['id'],

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
    is_it = db.user.find_one({'id':user_info['id']})
    #아이디가 존재하면 아이디 생략 x
    if not is_it:
        db.user.insert_one({'id': user_info['id'], 'nick': user_info['properties']['nickname'],'name': user_info['properties']['nickname'],'social_only': True} )
    #토큰 생성후 쿠키 부여
    payload = {'id': user_info['id']}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('token',token)
    return resp

@app.route('/login/github')
def login_github():
    code = request.args.get('code')
    url ='https://github.com/login/oauth/access_token'
    client_secret = '0775e84c22ce79ebdc1ef85ca5f9293f599e057e'
    client_id = '94debc0ee29ed22a1f74'
    headers = {'Accept': 'application/json'}

    resp = requests.post(
        url=url,
        headers=headers,
        data={'client_id': client_id, 'client_secret': client_secret,'code': code}
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

    #아이디가 존재하면 아이디 생략 x
    if not is_it:
        db.user.insert_one(
            {'id': user_info['id'], 'nick': user_info['name'], 'name':user_info['name'] ,'social_only': True})
    # 토큰 생성후 쿠키 부여
    payload = {'id': user_info['id']}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('token', token)
    return resp


if __name__ == '__main__':
    app.run(debug=True)