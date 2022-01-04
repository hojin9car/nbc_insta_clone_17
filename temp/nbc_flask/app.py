from flask import Flask
from flask import render_template

import auth
import post
import mypage
import db

app = Flask(__name__)
app.secret_key = 'sparta'

db = db.get_db()

@app.route('/')
def main():  # put application's code here
    content_list = list(db.contents.find({}).sort([('write_time', -1)]))

    return render_template('main.html', contents=content_list)



app.register_blueprint(auth.bp)
app.register_blueprint(post.bp)
app.register_blueprint(mypage.bp)

if __name__ == '__main__':
    app.run(debug=True)
