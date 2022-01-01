

from flask import render_template
from flask import Blueprint

from bson.objectid import ObjectId

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
    content_list = list(db.contents.find({}).sort([('write_time', -1)]))
    selected_list = []
    for i in content_list:
        if i['user._id'] == ObjectId(user['_id']):
            selected_list.append(i)


    return render_template('my_main.html', contents=selected_list)