from flask import Flask, request
import requests
import json


app = Flask(__name__)

def get_session_url(url_part):
    return "http://localhost:27012/" + url_part


def get_artist_url(url_part):
    return "http://localhost:27013" + url_part


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
    result = request.post(url, data=json.dumps(data_json), headers=headers).json()
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
    username = request.args.get('username')
    url = get_session_url("get_me") + "?username={0}".format(username)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1


@app.route("/tracks", methods=['GET'])
def get_tracks():
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    url = get_track_url("tracks") + "?page={0}&per_page={1}".format(page, per_page)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1


@app.route("/track/<id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_track_by_id(id):
    url = get_track_url("track") + "/{0}".format(id)
    if request.method == 'GET':
        result = requests.get(url).json()
    elif request.method == 'DELETE':
        result = request.delete(url).json()
    else:
        data_json = requests.get_json()
        headers = {'Content-type': 'application/json'}
    if request.method == 'POST':
        result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
    if request.method == 'PUT':
        result = requests.put(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1



@app.route("/artists", methods=['GET'])
def get_artists():
    try:
        per_page_artist = int(request.args.get('per_page'))
        url = get_artist_url("get_artist") + "?per_page={0}".format(per_page_artist)
        result = requests.get(url).json()
        page_artist = int(request.args.get('page'))
    except:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    url = get_track_url("get_tracks_artist")
    result_track = requests.get(url).json()
    o1 = result_track['items'];  a1 = o1[1]
    o2 = result['items']; a2 =o2[1]
    items = []
    for i1 in range(0, len(o1)):
        for i2 in range(0, len(o2)):
            a1 = o1[i1]; a2 = o2[i2]
            if a1['id_artist']== a2['id_artist']:
                items.append({
                'id_artist': a2['id_artist'],
                'name': a2['name'],
                'title': a1['title']})
    items = items[(page_artist-1)*per_page_artist:page_artist*per_page_artist]
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items,
        'per_page': per_page_artist,
        'page': page_artist})

@app.route("/artist/<id>", methods=['GET', 'POST','PUT'])
def get_artist(id):
    url = get_artist_url("get_artist") + "/{0}".format(id)
    if request.method == 'GET':
        result = requests.get(url).json()
    else:
        data_json = request.get_json()
        headers = {'Content-type': 'application/json'}
    if request.method == 'POST':
        result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
    if request.method == 'PUT':
        result = requests.put(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/check_session", methods=['GET'])
def check_ss():
    username = request.args.get('name')
    code = request.args.get('code')
    url = get_session_url("check_session") + "?username={0}&code={1}".format(username, code)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1

# @app.route("/check_user", methods=['GET'])
# def check_user():
#     name = request.args.get('username')
#     res = user_exist(username)
#     json1 = json.dumps(result)
#     return json1

if __name__ == "__main__":
    app.run(debug=True, port=27011)