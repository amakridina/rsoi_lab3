from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import math
import json
from db import *

app = Flask(__name__)

# @app.route('/artist/', methods=['GET'])
# def get_artist():
#     try:
#         per_page = int(request.args.get('per_page', 20))
#         if per_page < 20 or per_page > 100:
#             raise Exception()
#         page = int(request.args.get('page', 0))
#         lendb = len_db_dirs()
#         print lendb
#         if lendb % per_page > 0:
#             b = 1
#         else:
#             b = 0
#         if page < 0 or page > lendb / per_page + b:
#             raise Exception()
#     except:
#         return '', 400
#
#     items = []
#     items = artist_from_db(page, per_page)
#     return json.dumps({
#         'items': items,
#         'per_page': per_page,
#         'page': page,
#         'page_count': math.ceil(lendb / per_page + b)
#     }, indent=4), 200, {
#         'Content-Type': 'application/json;charset=UTF-8',
#     }

@app.route('/artist/<id>', methods=['GET'])
def get_artist_id(id):
    row = artist_by_id(id)
    if row == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Artist not found'})
    else: return json.dumps({
            'artist_id': row.artist_id,
            'name': row.name,
            'country': row.origin,
            'genre': row.genres,
            'years_active': row.years_active})


@app.route('/artist/<id>', methods=['POST'])
def post_artist(id):
    try:
        name = request.args.get('name')
        years = request.args.get('years_active')
        origin = request.args.get('origin')
        genre = request.args.get('genre')
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

@app.route('/artist/<id>', methods=['PUT'])
def put_artist(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = artist_by_id(id)
    if row == 0:
        return json.dumps({'error': 'no artist'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        name = request.args.get('name')
        years = request.args.get('years_active')
        origin = request.args.get('origin')
        genre = request.args.get('genre')
        if name is None and years is None and origin is None and genre is None:
            raise Exception()
    except:
        return '', 400
    if name is not None:
        i = update_artist(id, 'name', name)
    if years is not None:
        i = update_artist(id, 'years_active', years)
    if origin is not None:
        i = update_artist(id, 'origin', origin)
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