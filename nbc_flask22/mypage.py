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
    # user = get_user()
    # print(user['_id'])
    # print(type(user['_id']))
    # content_list = list(db.contents.find({'user_id': str(user['_id'])}))
    # print(content_list)

    return render_template('a_insta_my_page.html')


@bp.route('/api/my_page', methods=['GET'])
@login_required
def api_my_page():

    user = get_user()
    content_list = list(db.contents.find({'user_id': str(user['_id'])}, {'_id': False}))

    return jsonify({'result': content_list})

