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

    return render_template('a_insta_main.html')


app.register_blueprint(auth.bp)
app.register_blueprint(post.bp)
app.register_blueprint(mypage.bp)

if __name__ == '__main__':
    app.run(debug=True)
