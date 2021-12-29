from flask import Flask, session, redirect, render_template, request, json
import requests
import base64
import urllib
app = Flask(__name__)
app.secret_key = 'kkf3f44v4use4nx4lf03gs4vxe'
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login', methods=['GET'])
def login():
    receive_code = request.args.get('code')
    redir_url = 'https://hojin9car.pythonanywhere.com/login'
    get_user_id_url = f'https://slack.com/api/openid.connect.token?client_id=2822327673220.2857631084898&client_secret=3c58134350729455fb3ca8c17bd5d194&code={receive_code}&redirect_uri={redir_url}'
    res = requests.get(get_user_id_url)
    res_json = json.loads(res.text)
    if not res_json['ok']:
        print('error page render')
        return render_template('error.html')
    response_id_token = res_json['id_token'].split('.')
    for i in response_id_token:
        print("i:", i)
    strf = response_id_token[0]
    strf += strf + '=' * (4 - len(strf) % 4)
    header = base64.b64decode(strf)
    bst = response_id_token[1] + '=' * (4 - len(strf) % 4)
    body = base64.b64decode(bst)
    body = eval(body.decode('ascii'))
    uid = body['sub']
    APP_KEY = 'Bearer xoxp-2822327673220-2823663684982-2902285534304-a987e1d97aa12cf5218fdffa181d2832'
    url = f'https://slack.com/api/users.info?user={uid}'
    req = urllib.request.Request(url, headers={'Authorization': APP_KEY})
    res = urllib.request.urlopen(req).read()
    encoding = urllib.request.urlopen(req).info().get_content_charset('utf-8')
    JSON_object = json.loads(res.decode(encoding))
    session['uid'] = uid
    session['real_name'] = JSON_object['user']['profile']['real_name']
    session['img'] = JSON_object['user']['profile']['image_192']
    return render_template('instagram.html')
@app.route('/kakao')
def hello_world():  # put application's code here
    return render_template('kakao.html')
@app.route('/insta')
def insta():
    return render_template('instagram.html')
if __name__ == '__main__':
    app.run()