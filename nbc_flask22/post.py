from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import Blueprint
from flask import send_file

from bson.objectid import ObjectId
import datetime as dt
import gridfs
import codecs
import uuid
import json

from auth import login_required
from auth import get_user
import db

bp = Blueprint("post", __name__)
dbe = db.get_db()
fs = gridfs.GridFS(dbe)

# 글 쓰는 화면으로 이동
@bp.route('/new_write')
@login_required
def new_write():
    return render_template('a_insta_write_form.html')


# 글 작성
@bp.route('/api/write', methods=['POST'])
@login_required
def api_wirte():
    if request.method == 'POST':

        # html에서 가져온 정보
        text = request.form['text_give']
        file = request.files['file_give']

        # 현재 로그인 사용자 정보
        writer = get_user()

        fs_img_id = str(fs.put(file))

        uid = str(uuid.uuid4())
        print(uid)
        # 글 작성
        dbe.contents.insert_one({
            'user_nick': writer['nick'],
            'user_id': str(writer['_id']),
            'uuid': uid,
            'write_time': dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초"),
            'write_edit_time': '',
            'img': fs_img_id,
            'content': text})

        dbe.comments.insert_one({
            'uuid': uid,
            'comments': []
        })

        dbe.likes.insert_one({
            'uuid': uid,
            'liker': []
        })

        return jsonify({'result': 'success'})


@bp.route('/api/delete', methods=['PUT'])
@login_required
def api_delete():
    # 현재 로그인 사용자 정보
    user = get_user()

    # 글에서 글 작성자 아이디를 가져옴
    uid = request.args.get('uuid')
    print('i9i9i9i9', uid)
    # 가져온 id값은 str이므로 db에서 찾을 수가 없다. 따라서 ObjectId로 바꿔주어야함
    # id = ObjectId(id)

    # 글의 정보를 가져온 뒤 글의 작성자를 비교해야함
    one = dbe.contents.find_one({'uuid': uid})
    # print(one['_id'])
    print(one)
    # 현재 로그인 사용자와 글작성자가 같아야지 진행이 가능
    # print(one['user_id'], user['_id'])
    # if one['user_id'] != user['_id']:
    #     # 같지 않다면 홈화면 보이게함 이건 나중에 수정
    #     return redirect(url_for('post.home'))

    dbe.contents.delete_one({'uuid': str(uid)})
    dbe.comments.delete_one({'uuid': str(uid)})
    dbe.likes.delete_one({'uuid': str(uid)})

    return jsonify({'result': 'success'})


# 글 수정 화면 # 사진첨부 = null 일때 사용하는 api
@bp.route('/api/edit_v1', methods=['POST'])
@login_required
def api_edit_v1():
    # print(request.form)
    # html에서 가져온 정보
    text = request.form['text_give']
    file = request.form['file_give']
    uuid = request.form['uuid']

    # 현재 로그인 사용자 정보
    writer = get_user()

    dbe.contents.update_one({'uuid': uuid}, {
            '$set': {'content': text, 'write_edit_time': dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}})

    return jsonify({'result': 'success'})


# 글 수정 화면 # 사진첨부시 사용하는 api
@bp.route('/api/edit_v2', methods=['POST'])
@login_required
def api_edit_v2():
    # print(request.form)
    # html에서 가져온 정보
    text = request.form['text_give']
    file = request.files['file_give']
    uuid = request.form['uuid']

    # 현재 로그인 사용자 정보
    writer = get_user()

    fs_img_id = str(fs.put(file))
    print(fs_img_id)
    dbe.contents.update_one({'uuid': uuid}, {
            '$set': {'content': text, 'img': fs_img_id, 'write_edit_time': dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}})

    return jsonify({'result': 'success'})


# 글 수정 화면
@bp.route('/edit_write/<uuid>')
@login_required
def edit_write(uuid):
    content = dbe.contents.find_one({'uuid': uuid})
    return render_template('a_insta_edit_form.html', content=content)


# 홈 화면
@bp.route('/home')
@login_required
def home():
    user = get_user()
    content_list = list(dbe.contents.find({}).sort([('write_time', -1)]))

    return render_template('home.html', contents=content_list)


@bp.route('/api/read_image/<uid>')
def read_image(uid):
    data = dbe.contents.find_one({'uuid': uid})
    img_binary = fs.get(ObjectId(data['img']))
    base64_data = codecs.encode(img_binary.read(), 'base64')
    image = base64_data.decode('utf-8')
    # print(image)
    # print(type(image))
    return image


@bp.route('/api/read_contents', methods=['GET'])
def read_contents():
    #유저 정보 불러옴
    user = get_user()
    content_list = list(dbe.contents.find({}, {'_id': False}).sort([('write_time', -1)]))
    # likes의 uuid와 콘텐츠의 uuid가 같은 것을 찾음
    for content in content_list:
        contents_like = dbe.likes.find_one({'uuid':content['uuid']}, {'_id': False})
        # liker의 값이 0보다 크다면 즉 누가 댓글을 달았다면
        if contents_like and len(contents_like['liker']) > 0:
            #content에 아래와 같은 값을 추가
            content['likes'] = contents_like['liker']
            content['count_num'] = len(contents_like['liker'])
            content['first_click'] = contents_like['liker'][0]
            #이건 내가 좋아요 눌른 게시물인지 확인하기 위해서
            if user['nick'] in contents_like['liker']:
                content['my_click'] = True


    return jsonify({'data': content_list})


@bp.route('/detail/<uuid>', methods=['GET'])
def view_detail(uuid):
    content = (dbe.contents.find_one({'uuid': uuid}))
    # print('fef3== ', content)
    return render_template('a_insta_view_detail.html', content=content)

@bp.route('/api/like/<uid>')
def like(uid):
    # 좋아요 테이블 찾아옴
    like_table = dbe.likes.find_one({'uuid': uid})
    user = get_user()
    if user['nick'] in like_table['liker']:
        new_liker = like_table['liker']
        new_liker.remove(user['nick'])
        dbe.likes.update_one({'uuid': uid}, {'$set': {'liker': new_liker}})
        return jsonify({'result':'cancle'})

    new_liker = like_table['liker']
    new_liker.append(user['nick'])
    dbe.likes.update_one({'uuid': uid}, {'$set' : { 'liker': new_liker }})



    return jsonify({'result':'success'})