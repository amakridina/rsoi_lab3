from flask import Flask, request
import math
import json
from db import *

app = Flask(__name__)

@app.route('/artists', methods=['GET'])
def get_artist():
    try:
        per_page = int(request.args.get('per_page'))
        page = int(request.args.get('page'))
        lendb = len_db_artists()
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})

    items = []
    items = artists_from_db(page, per_page)
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)})

@app.route('/artist/<id>', methods=['GET', 'POST', 'PUT'])
def get_artist_id(id):
    if request.method == 'GET':
        row = artist_by_id(id)
        if row == 0:
            return json.dumps({'error_code': 404, 'error_msg': 'Artist not found'})
        else:
            return json.dumps({
                'artist_id': row.artist_id,
                'name': row.name,
                'country': row.origin,
                'genre': row.genres,
                'years_active': row.years_active})

    if request.method == 'POST':
        data_json = request.get_json()
        try:
            name = data_json['name']
            years = data_json['years']
            origin = data_json['country']
            genre = data_json['genre']
            if name is None or years is None or origin is None or genre is None:
                raise Exception()
        except:
            return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
        i = insert_artist(id, name, years, origin, genre)
        if i == 0:
            return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
        s = '/artist/{'+id+'}'
        return json.dumps({
            'Location': s
        }), 201, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

    if request.method == 'PUT':
        data_json = request.get_json()
        name = None
        years = None
        country = None
        genre = None

        if 'name' in data_json:
            name = data_json['name']
        if 'years' in data_json:
            years = data_json['years']
        if 'country' in data_json:
            country = data_json['country']
        if 'genre' in data_json:
            genre = data_json['genre']
        if name == 0 and years == 0 and country == 0 and genre == 0:
            return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})

        if name is not None:
            i = update_artist(id, 'name', name)
        if years is not None:
            i = update_artist(id, 'years_active', years)
        if country is not None:
            i = update_artist(id, 'origin', country)
        if genre is not None:
            i = update_artist(id, 'genres', genre)
        if i == 0:
            return '', 400
        s = '/artist/{'+id+'}'
        return json.dumps({
            'Location': s
        }), 200, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

if __name__ == "__main__":
 app.run(debug=True, port=27013)