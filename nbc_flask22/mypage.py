from flask import render_template
from flask import Blueprint
from flask import jsonify
from bson.objectid import ObjectId
import json

from auth import login_required
from auth import get_user

import db

db = db.get_db()

SECRET_KEY = 'sparta'

bp = Blueprint("mypage", __name__)


@bp.route('/my_main')
@login_required
def my_main():
    # 로그인 되어있지 않으면 로그인창으로 보냄
    user = get_user()

    content_list = list(db.contents.find({'user_id': str(user['_id'])}))

    # likes의 uuid와 콘텐츠의 uuid가 같은 것을 찾음
    for content in content_list:
        contents_like = db.likes.find_one({'uuid': content['uuid']}, {'_id': False})
        # liker의 값이 0보다 크다면 즉 누가 댓글을 달았다면
        if contents_like and len(contents_like['liker']) > 0:
            # content에 아래와 같은 값을 추가
            content['likes'] = contents_like['liker']
            content['count_num'] = len(contents_like['liker'])
            content['first_click'] = contents_like['liker'][0]
            # 이건 내가 좋아요 눌른 게시물인지 확인하기 위해서
            if user['nick'] in contents_like['liker']:
                content['my_click'] = True

    return render_template('a_insta_my_page.html', contents=content_list)


@bp.route('/api/my_page', methods=['GET'])
@login_required
def api_my_page():

    user = get_user()
    content_list = list(db.contents.find({'user_id': str(user['_id'])}, {'_id': False}))

    return jsonify({'result': content_list})

