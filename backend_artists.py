from flask import Flask, request
import math
import json
from db import *

app = Flask(__name__)

@app.route('/artist/', methods=['GET'])
def get_artist():
    try:
        per_page = int(request.args.get('per_page', 20))
        if per_page < 20 or per_page > 100:
            raise Exception()
        page = int(request.args.get('page', 0))
        lendb = len_db_artist()
        print lendb
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return '', 400

    items = []
    items = artist_from_db(page, per_page)
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)
    }, indent=4), 200, {
        'Content-Type': 'application/json;charset=UTF-8',
    }

@app.route('/artist/<id>', methods=['GET', 'POST', 'PUT'])
def get_artist_id(id):
    if request.method == 'GET':
        row = artist_by_id(id)
        if row == 0:
            return json.dumps({'error_code': 404, 'error_msg': 'Artist not found'})
        else: return json.dumps({
                'artist_id': row.artist_id,
                'name': row.name,
                'country': row.origin,
                'genre': row.genres,
                'years_active': row.years_active})

    if request.method == 'POST':
        data_json = request.get_json()
        try:
            name = data_json['name']
            years = data_json['years_active']
            origin = data_json['origin']
            genre = data_json['genre']
            if name is None or years is None or origin is None or genre is None:
                raise Exception()
        except:
            return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
        i = insert_artist(id, name,years ,origin, genre)
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
        name = 0
        years = 0
        origin = 0
        genre = 0

        if name in data_json:
            name = data_json['name']
        if years in data_json:
            years = data_json['years_active']
        if origin in data_json:
            origin = data_json['origin']
        if genre in data_json:
            genre = data_json['genres']
        if name == 0 and years == 0 and origin == 0 and genre == 0:
            return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})

        if name != 0:
            i = update_artist(id, 'name', name)
        if years != 0:
            i = update_artist(id, 'years_active', years)
        if origin != 0:
            i = update_artist(id, 'origin', origin)
        if genre != 0:
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