from flask import Flask, request
import math
import json
from db import *

app = Flask(__name__)

@app.route('/tracks', methods=['GET'])
def get_tracks():

    try:
        per_page = int(request.args.get('per_page'))
        page = int(request.args.get('page'))
        lendb = len_db()
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})

    items = []
    items = tracks_from_db(page, per_page)
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)})


@app.route('/track/<id>', methods=['GET'])
def get_track(id):
    row = track_by_id(id)
    if row == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    else:
        return json.dumps({
            'id': row.track_id,
            'track': row.track,
            'album': row.album,
            'year': row.year,
            'genre': row.genre})

@app.route('/track/<id>', methods=['POST'])
def post_track(id):
    data_json = request.get_json()

    artist_id = data_json['artist_id']
    track = data_json['track']
    album = data_json['album']
    year = data_json['year']
    genre = data_json['genre']

    i = insert_track(id, track, artist_id, album, year, genre)
    if i == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 201, {
            'Content-Type': 'application/json;charset=UTF-8',
        }


@app.route('/track/<id>', methods=['PUT'])
def put_track(id):
    data_json = request.get_json()
    i=0
    artist_id = 0
    track = 0
    album = 0
    year = 0
    genre = 0

    if 'artist_id' in data_json:
        artist_id = data_json['artist_id']
    if 'track' in data_json:
        track = data_json['track']
    if 'album' in data_json:
        album = data_json['album']
    if 'year' in data_json:
        year = data_json['year']
    if 'genre' in data_json:
        genre = data_json['genre']

    if artist_id == 0 and year == 0 and album == 0 and track == 0 and genre == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})

    if artist_id != 0:
        i = update_track(id, 'artist_id', artist_id)
    if track != 0:
        i = update_track(id, 'track', track)
    if album != 0:
        i = update_track(id, 'album', album)
    if year != 0:
        i = update_track(id, 'year', year)
    if genre != 0:
        i = update_track(id, 'genre', genre)
    if i == 0:
         return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    s = '/tracks/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/track/<id>', methods=['DELETE'])
def delete_track(id):
    row = track_by_id(id)
    if row == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    #del_track(id)
    return json.dumps({'ok' : 'ok'})

@app.route("/tracks_for_artist", methods=['GET'])
def tracks_for_artist():
    items = films_for_dir()
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items})

if __name__ == "__main__":
 app.run(debug=True, port=27014)
