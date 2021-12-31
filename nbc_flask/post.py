from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import Blueprint

from bson.objectid import ObjectId
import datetime as dt

from auth import login_required
from auth import get_user
import db

bp = Blueprint("post", __name__)
db = db.get_db()


# 글 쓰는 화면으로 이동
@bp.route('/new_write')
@login_required
def new_write():
    return render_template('new_write.html')


# 글 작성
@bp.route('/api/write', methods=['POST'])
@login_required
def api_wirte():
    # html에서 가져온 정보
    data = request.json
    # 현재 로그인 사용자 정보
    writer = get_user()
    # 글 작성
    new_one = db.contents.insert_one({'user.nick': writer['nick'], 'user._id': writer['_id'], 'like': 0,
                                      'comments': 0,
                                      'write_time': dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초"),
                                      'write_edit_time': '', 'img': '', 'content': data['text_give']})
    # 글 작성한 것 가져오기 new_one사용 안됨
    content = db.contents.find_one({'_id': new_one.inserted_id})

    return jsonify({'result': 'success'})


@bp.route('/api/delete', methods=['PUT'])
@login_required
def api_delete():
    # 현재 로그인 사용자 정보
    user = get_user()
    # 글에서 글 작성자 아이디를 가져옴
    id = request.args.get('id')
    # 가져온 id값은 str이므로 db에서 찾을 수가 없다. 따라서 ObjectId로 바꿔주어야함
    id = ObjectId(id)
    # 글의 정보를 가져온 뒤 글의 작성자를 비교해야함
    one = db.contents.find_one({'_id': id})
    print(one['_id'])
    # 현재 로그인 사용자와 글작성자가 같아야지 진행이 가능
    if one['user._id'] != user['_id']:
        # 같지 않다면 홈화면 보이게함 이건 나중에 수정
        return redirect(url_for('post.home'))
    db.contents.delete_one({'_id': one['_id']})
    return redirect(url_for('post.home'))


# 글 수정 화면
@bp.route('/api/edit', methods=['POST'])
@login_required
def api_edit():
    data = request.json
    id = data['id']
    text_area = data['text-area']

    db.contents.update_one({'_id': ObjectId(id)}, {
        '$set': {'content': text_area, 'write_edit_time': dt.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}})
    return jsonify({'result': 'success'})


# 글 수정 화면
@bp.route('/edit_write/<id>')
@login_required
def edit_write(id):
    content = db.contents.find_one({'_id': ObjectId(id)})
    return render_template('edit_write.html', content=content)


# 홈 화면
@bp.route('/home')
@login_required
def home():
    user = get_user()
    content_list = list(db.contents.find({}).sort([('write_time', -1)]))

    return render_template('home.html', contents=content_list)
