from flask import Flask, request, jsonify
import random
import string
import json
from db import *

app = Flask(__name__)

@app.route("/add_user", methods=['POST'])
def add_user_db():
    my_json = request.get_json()
    username = my_json['name']
    fname = my_json['fname']
    lname = my_json['lname']
    tel = my_json['phone']
    email = my_json['email']
    password = my_json['password']
    if user_exist(username):
        return json.dumps({'error_code': 400, 'error_msg': 'User already exists'}, {
        'Content-Type': 'application/json;charset=UTF-8',
    })
    i = insert_user(username, fname, lname, tel, email, password)
    if i == 0:
        return json.dumps({'error_code': 500, 'error_msg': 'Database error'})
    return json.dumps({'ok': 'ok'})

@app.route("/authorize", methods=['GET'])
def authorize():
    user_name = request.args.get('username')
    password = request.args.get('password')
    if user_exist(user_name, password):
        code = ''.join(random.choice(string.lowercase) for i in range(30))
        i = insert_code(code, user_name)
        if i==0:
            return json.dumps({'error_code': 500, 'error_msg': 'Database Error'})
        return json.dumps({'code': code})
    return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})


@app.route("/api/me", methods=['GET'])
def me():
    access_token = request.headers.get('Authorization', '')[len('Bearer '):]
    info = get_me(access_token)
    if not info:
        return json.dumps({'error': 'invalid_token'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }
    return jsonify(UserName=info.UserName,
                FirstName=info.FirstName,
                LastName=info.LastName,
                Telephone=info.Telephone,
                Email=info.Email)


@app.route("/check_session", methods=['GET'])
def check_ss():
    user_name = request.args.get('username')
    code = request.args.get('code')
    i = user_connected(user_name, code)
    if i == 0:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'})
    else:
        return json.dumps({'ok': 'ok'})

if __name__ == "__main__":
    app.run(debug=True, port=27012)