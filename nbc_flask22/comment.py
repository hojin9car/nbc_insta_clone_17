from flask import Blueprint
from flask import request

from auth import login_required
from auth import get_user

import db

bp = Blueprint('comment', __name__)
db = db.get_db()


@bp.route('/api/write_comment', methods=['POST'])
@login_required
def write_comment():

    text = request.form['text_give']
    writer = get_user()

    doc = {
        'writer': writer,
        'text': text
    }




