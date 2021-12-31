from flask import Flask
from flask import render_template

import auth
import mypage

app = Flask(__name__)
app.secret_key = 'sparta'


@app.route('/')
def main():  # put application's code here
    return render_template('main.html')


app.register_blueprint(auth.bp)

if __name__ == '__main__':
    app.run()
