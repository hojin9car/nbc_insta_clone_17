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
#글 쓰는 화면으로 이동
@app.route('/new_write')
def new_write():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    logged = sign_in()
    if logged == 'bad':
        return redirect(url_for('login_page'))
    return render_template('new_write.html')



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

