from flask import Flask, request
from datetime import datetime, timedelta
import math
import json
from db import *

app = Flask(__name__)

@app.route('/tracks/', methods=['GET'])
def get_track():
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}

    try:
        per_page = int(request.args.get('per_page', 20))
        if per_page < 20 or per_page > 100:
            raise Exception()
        page = int(request.args.get('page', 0))
        lendb = len_db()
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return 'error', 400

    items = []
    items = tracks_from_db(page, per_page)
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)
    }, indent=4),200, {
        'Content-Type': 'application/json;charset=UTF-8',
    }


@app.route('/tracks/<id>', methods=['GET'])
def get_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = track_by_id(id)
    print row
    if row == 0:
        return '', 404
    else:
        return json.dumps({
            'id': row.track_id,
            'track': row.track,
            'album': row.album,
            'year': row.year,
            'genre': row.genre
        }, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/tracks/<id>', methods=['POST'])
def post_track(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        artist_id = request.args.get('artist_id')
        track = request.args.get('track')
        album = request.args.get('album')
        year = request.args.get('year')
        genre = request.args.get('genre')
        if artist_id is None or year is None:
            raise Exception()
        if album is None or track is None or genre is None:
            raise Exception()
    except:
        return '', 400

    i = insert_track(id, track, artist_id, album, year, genre)
    if i == 0:
        return '', 400
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 201, {
            'Content-Type': 'application/json;charset=UTF-8',
        }


@app.route('/tracks/<id>', methods=['PUT'])
def put_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = track_by_id(id)
    if row == 0:
        return '', 404
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
    if artist_id is not None:
        i = update_track(id, 'artist_id', artist_id)
    if track is not None:
        i = update_track(id, 'track', track)
    if album is not None:
        i = update_track(id, 'album', album)
    if year is not None:
        i = update_track(id, 'year', year)
    if genre is not None:
        i = update_track(id, 'genre', genre)
    if i == 0:
        return '', 400
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/tracks/<id>', methods=['DELETE'])
def delete_track(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = track_by_id(id)
    if row == 0:
        return json.dumps({'error': 'no id'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    del_track(id)
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

if __name__ == "__main__":
 app.run(debug=True, port=27014)
