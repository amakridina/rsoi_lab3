from flask import Flask, render_template, request, session, redirect, url_for, make_response
import requests
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)


def get_logic_url(url_part):
    return "http://localhost:27011/" + url_part


def get_data_from_cookies():
    expired = session.get('expired')
    if expired is None:
        return None, None
    if expired < datetime.now():
        clear_data_in_cookies()
        return 0, 0
    return session.get('login'), session.get('code')


def set_data_to_cookies(user, code):
    session['login'] = user
    session['code'] = code
    session['expired'] = datetime.now() + timedelta(minutes=10)


def clear_data_in_cookies():
    session.pop('login', None)
    session.pop('code', None)
    session.pop('expired', None)


@app.route("/")
def main():
    if not ('login' in session and 'code' in session):
        return redirect(url_for('authorization_form'))

    return render_template("home.html")


@app.route("/authorize", methods=['GET', 'POST'])
def login():
    error_info = ''
    if request.method == 'POST':
        if not ('login' in session and 'code' in session):
            username = request.form['username']
            password = request.form['password']
            url = get_logic_url("authorize") + "?username={0}&password={1}".format(username, password)
            result = requests.get(url).json()
            if 'error_code' in result:
                code = result['error_code']
                msg = result['error_msg']
                return json.dumps({'message': msg, 'error': code}, indent=4), code
            session.permanent = True
            set_data_to_cookies(username, result['code'])
            response = make_response(redirect(url_for('home_form')))
            response.set_cookie('Expires', "{0}".format(datetime.now()+timedelta(minutes=10)))
            response.set_cookie('token', result['code'])
            response.set_cookie('login', username)
            print response
            return response
        return redirect(url_for('home_form'))
    return render_template('auth.html', errorInfo=error_info)


@app.route('/register', methods=['POST', 'GET'])
def register():
    error_info = ''
    if request.method == 'POST':
        name = request.form['username']
        first_name = request.form['fname']
        last_name = request.form['lname']
        phone = request.form['tel']
        email = request.form['email']
        password = request.form['password']

        url = get_logic_url("add_user")
        data = {'name': name, 'password': password, 'email': email, 'phone': phone, 'fname': first_name, 'lname': last_name}
        headers = {'Content-type': 'application/json'}

        result = requests.post(url, data=json.dumps(data), headers=headers).json()

        if 'error_code' in result:
            code = result['error_code']
            msg = result['error_msg']
            return json.dumps({'message': msg, 'error': code}, indent=4), code
        return render_template("authorize.html")
    render_template('register.html', errorInfo=error_info)


@app.route("/logout", methods=['GET'])
def logout():
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return render_template("home.html")
    clear_data_in_cookies()
    response = make_response(redirect(url_for('home_form')))
    response.delete_cookie('login')
    response.delete_cookie('Expires')
    response.delete_cookie('token')
    return response


@app.route('/home', methods=['GET'])
def home_form():
    return render_template("home.html")


@app.route('/home', methods=['POST'])
def home():
    if 'track_by_id' in request.form:
        return render_template("ID_track.html")
    if 'p_tracks' in request.form:
        return render_template("track_data.html")
    if 'artist_by_id' in request.form:
        return render_template("ID_artist.html")
    if 'p_artists' in request.form:
        return render_template("artist_data.html")
    return '', 200

@app.route('/homeanswer', methods=['GET'])
def home_answer():
    delete = request.args.get('delete')
    id = request.args.get('id')
    res = ''
    if delete is not None:
        res = delete_track_by_id(id)
    return res

@app.route('/tracks', methods=['GET'])
def get_tracks():
    global page
    next = request.args.get('next')
    prev = request.args.get('prev')
    if prev is not None:
        page -= 1
    elif next is not None:
        page += 1
    else:
        page = 1
    per_page = 5
    url = get_logic_url("tracks") + ("?page={0}&per_page={1}".format(page, per_page))
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    res = result['items']
    return render_template("list_tracks.html", tracks=res, page=page)


@app.route('/tracks/<id>', methods=['GET', 'POST', 'PUT'])
def get_track_by_id(id):
    name, code = get_data_from_cookies()
    print name, code
    if name is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if name == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_logic_url("check_session") + "?name={0}&code={1}".format(name, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    url = get_logic_url("track") + ("/{0}".format(id))

    if request.method == 'GET':
        result = requests.get(url).json()

    if request.method == 'POST':
        artist_id = request.args.get('artist_id')
        track = request.args.get('track')
        album = request.args.get('album')
        year = request.args.get('year')
        genre = request.args.get('genre')
        if artist_id is None or year is None:
            return '', 400
        if album is None or track is None or genre is None:
            return '', 400
        headers = {'Content-type': 'application/json'}
        data = {'id': id, 'track': track, 'artist_id': artist_id,
                'album': album, 'year': year, 'genre': genre}
        result = requests.post(url, data=json.dumps(data), headers=headers).json()

    if request.method == "PUT":
        try:
            artist_id = request.args.get('artist_id')
            track = request.args.get('track')
            album = request.args.get('album')
            year = request.args.get('year')
            genre = request.args.get('genre')
            if artist_id is None and year is None and album is None and track is None and genre is None:
                raise Exception()
        except:
            return '', 400
        if artist_id == '' and year == '' and album == '' and track == '' and genre == '':
            return '', 400
        if artist_id != '':
            data = {'id': id, 'artist_id': artist_id}
        if track != '':
            data = {'id': id, 'track': track}
        if album != '':
            data = {'id': id, 'album': album}
        if year != '':
            data = {'id': id, 'year': year}
        if genre != '':
            data = {'id': id, 'genre': genre}
        headers = {'Content-type': 'application/json'}
        result = requests.put(url, data=json.dumps(data), headers=headers).json()

    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    if request.method == 'GET':
        return render_template("track_id.html", track=result)
    if request.method == 'POST' or request.method == 'PUT':
        location = result['Location']
        return json.dumps({'Location': location}, indent=4), 201

@app.route('/tracks/<id>', methods=['DELETE'])
def delete_track_by_id(id):
    name, code = get_data_from_cookies()
    print name, code
    if name is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if name == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_logic_url("check_session") + "?name={0}&code={1}".format(name, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    url = get_logic_url("track") + ("/{0}".format(id))
    result = requests.delete(url)
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    return 'ok', 200

@app.route('/artists', methods=['GET'])
def get_artists():
    global page
    next = request.args.get('next')
    prev = request.args.get('prev')
    if prev is not None:
        page -= 1
    elif next is not None:
        page += 1
    else:
        page = 1
    per_page = 5
    url = get_logic_url("artists") + ("?page={0}&per_page={1}".format(page, per_page))

    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    res = result['items']
    return render_template("artists_show.html", artists=res, page=page)


@app.route('/artist', methods=['GET'])
def artist_by_id():
    id = int(request.args.get('id'))
    return get_artist_by_id(id)


@app.route('/artists/<id>', methods=['GET'])
def get_artist_by_id(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_logic_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    url = get_logic_url("artist") + "/{0}".format(id)

    result = requests.get(url).json()
    print result
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    return render_template("artist_by_id.html", artist=result)


@app.route('/artist_p', methods=['GET'])
def artist_p():
    id = int(request.args.get('artist_id'))
    if id == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'}), 400
    post = request.args.get('post')
    put = request.args.get('put')
    res = 200
    if post is not None:
        res = post_artist(id)
    if put is not None:
        res = put_artist(id)
    return res


@app.route('/artists/<id>', methods=['POST'])
def post_artist(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_logic_url("check_session") + "?username={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    name = request.args.get('name')
    birthday = request.args.get('birthday')
    country = request.args.get('country')
    if name is None or birthday is None or country is None:
        return '', 400

    url = get_logic_url("artist") + "/{0}".format(id)
    headers = {'Content-type': 'application/json'}
    data = {'name': name, 'birthday': birthday, 'country': country}

    result = requests.post(url, data=json.dumps(data), headers=headers).json()
    print result
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    location = result['Location']
    return json.dumps({'Location': location}, indent=4), 201


@app.route('/artists/<id>', methods=['PUT'])
def put_artist(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_logic_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    name = request.args.get('name')
    birthday = request.args.get('birthday')
    country = request.args.get('country')
    if name == '' and birthday == '' and country == '':
        return '', 400

    url = get_logic_url("artist") + "/{0}".format(id)
    if name != '':
        data = {'artist_id': id, 'name': name}
    if birthday != '':
        data = {'artist_id': id, 'birthday': birthday}
    if country != '':
        data = {'artist_id': id, 'country': country}
    headers = {'Content-type': 'application/json'}

    result = requests.put(url, data=json.dumps(data), headers=headers).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    location = result['Location']

    return json.dumps({'Location': location}, indent=4), 200


@app.route('/me', methods=['GET'])
def me():
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_logic_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    print result
    url = get_logic_url("get_me") + "?phone={0}".format(phone)
    result = requests.get(url).json()

    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    return json.dumps(result, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

if __name__ == "__main__":
    page = 1
    app.secret_key = os.urandom(24)
    app.run(debug=True, port=27010)
