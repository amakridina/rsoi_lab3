from flask import Flask, request, redirect, url_for
import requests
import json


app = Flask(__name__)

def get_session_url(url_part):
    return "http://localhost:27012/" + url_part


def get_artist_url(url_part):
    return "http://localhost:27013/" + url_part


def get_track_url(url_part):
    return "http://localhost:27014/" + url_part


def check_connection(login, token):
    url = get_session_url("check_connection?login={0}&token={1}".format(login, token))
    result = request.get(url).json()
    return 'ok' in result


@app.route("/add_user", methods=['POST'])
def add_user():
    data_json = request.get_json()
    url = get_session_url("add_user")
    headers = {'Content-type': 'application/json'}
    try:
        result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
    except:
        return json.dumps({'error_code': 503, 'error_msg': 'Service Session Temporary Unavailable'})
    json1 = json.dumps(result)
    return json1


@app.route("/authorize", methods=['GET'])
def authorize():
    username = request.args.get('username')
    password = request.args.get('password')
    if username is None or password is None:
        return json.dumps({'error_code': 400, 'error_msg': 'No username or wrong password'}, indent=4), 400
    url = get_session_url("authorize") + "?username={0}&password={1}".format(username, password)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1

@app.route("/get_me", methods=['GET'])
def get_me():
    username = request.args.get('name')
    url = get_session_url("get_me") + "?name={0}".format(username)
    try:
        result = requests.get(url).json()
    except:
        return json.dumps({'error_code': 503, 'error_msg': 'Service Session Temporary Unavailable'})
    json1 = json.dumps(result)
    return json1


@app.route("/tracks", methods=['GET'])
def get_tracks():
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    url = get_track_url("tracks") + "?page={0}&per_page={1}".format(page, per_page)
    try:
        result = requests.get(url).json()
    except:
        return json.dumps({'error_code': 503, 'error_msg': 'Service Tracks Temporary Unavailable'})
    json1 = json.dumps(result)
    return json1


@app.route("/track/<id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_track_by_id(id):
    url = get_track_url("track") + "/{0}".format(id)
    if request.method == 'GET':
        try:
            result = requests.get(url).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Tracks Temporary Unavailable'})
        json1 = json.dumps(result)

        url = get_artist_url("artist") + "/{0}".format(result['artist_id'])
        try:
            res = requests.get(url).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Artists Temporary Unavailable'})
        aa = res['name']
        result['artist_name'] = res['name']
        json1 = json.dumps(result)
        return json1
    elif request.method == 'DELETE':
        try:
            result = requests.delete(url).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Tracks Temporary Unavailable'})
    else:
        data_json = request.get_json()
        headers = {'Content-type': 'application/json'}
    if request.method == 'POST':
        try:
            result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Tracks Temporary Unavailable'})
    if request.method == 'PUT':
        try:
            result = requests.put(url, data=json.dumps(data_json), headers=headers).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Tracks Temporary Unavailable'})
    json1 = json.dumps(result)
    return json1



@app.route("/artists", methods=['GET'])
def get_artists():
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    url = get_artist_url("artists") + "?page={0}&per_page={1}".format(page, per_page)
    try:
        result = requests.get(url).json()
    except:
        return json.dumps({'error_code': 503, 'error_msg': 'Service Artists Temporary Unavailable'})
    json1 = json.dumps(result)
    return json1

@app.route("/artist/<id>", methods=['GET', 'POST','PUT'])
def get_artist(id):
    url = get_artist_url("artist") + "/{0}".format(id)
    if request.method == 'GET':
        try:
            result = requests.get(url).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Artists Temporary Unavailable'})
    else:
        data_json = request.get_json()
        headers = {'Content-type': 'application/json'}
    if request.method == 'POST':
        try:
            result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
        except:
            return json.dumps({'error_code': 503, 'error_msg': 'Service Artists Temporary Unavailable'})
    if request.method == 'PUT':
        result = requests.put(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/check_session", methods=['GET'])
def check_ss():
    username = request.args.get('name')
    code = request.args.get('code')
    url = get_session_url("check_session") + "?username={0}&code={1}".format(username, code)
    try:
        result = requests.get(url).json()
    except:
        return json.dumps({'error_code': 503, 'error_msg': 'Service Session Temporary Unavailable'})
    json1 = json.dumps(result)
    return json1

if __name__ == "__main__":
    app.run(debug=True, port=27011)