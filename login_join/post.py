from flask import Flask, render_template,request,redirect,url_for,make_response ,jsonify
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib
import jwt
import datetime as dt
from bson.json_util import dumps

client = MongoClient('localhost',27017)
db = client.dbProject1
SECRET_KEY = 'sparta'


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
    #response로 글 보냄
    return jsonify( {'content': dumps(content)})

@app.route('/api/delete',methods=['PUT'])
def api_delete():
    #현재 로그인 사용자 정보
    user = get_user()
    #글에서 글 작성자 아이디를 가져옴
    id = request.args.get('id')
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
    return redirect(url_for('home'))
