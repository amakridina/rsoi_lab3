import pyodbc

def Tracks_db_conn():
    cnxn = pyodbc.connect(r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=TracksArtist;' +
            r'UID=rsoi;PWD=Mak123456')
    cursor = cnxn.cursor()
    return cursor;

def users_db_conn():
    cnxn = pyodbc.connect(r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=rsoi;' +
            r'UID=rsoi;PWD=Mak123456')
    cursor = cnxn.cursor()
    return cursor;

def user_exist(username, password):
    cursor = users_db_conn()
    cursor.execute("select * from UsersInfo where UserName='" + username+"' and Password='"+ password+"'")
    row = cursor.fetchone()
    if row:
        return 1
    else:
        return 0

def insert_user(username, first_name, last_name, tel, email, password):
    db = users_db_conn()
    insert_str  = ("insert into UsersInfo"+
                       " (UserName, FirstName, LastName, Telephone, Email, Password)"+
                       " values ('%s','%s','%s','%s','%s','%s' )"
                       % (username, first_name, last_name, tel, email, password))
    db.execute(insert_str)
    db.commit()
    return 0;

def insert_code(code, username):
    try:
        cursor = users_db_conn()
        cursor.execute("update UsersInfo set Token='"+code+"' where UserName='" + username+"'")
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1;

def len_db_tracks():
    cursor = Tracks_db_conn()
    cursor.execute("select count(*) from tracks")
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0;

def len_db_artists():
    cursor = Tracks_db_conn()
    cursor.execute("select count(*) from artists")
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0;

###############################################
def len_db_tracks():
    count = 0
    cursor = Tracks_db_conn()
    cursor.execute("select * from tracks")
    rows = cursor.fetchall()
    for row in rows:
        count += 1
    return count

def tracks_from_db(page, per_page):
    items = []
    cursor = Tracks_db_conn()
    cursor.execute("select * from tracks")
    rows = cursor.fetchall()
    end = page * per_page
    if end > len(rows):
        end = len(rows)
    for i in range((page -1) * per_page, end):
        row = rows[i]
        items.append({
            'id': row.track_id,
            'track': row.track,
            'artist_id': row.artist_id,
            'album': row.album,
            'year': row.year,
            'genre':row.genre
            })
    return items

def len_db_artist():
    count = 0
    cursor = Tracks_db_conn()
    cursor.execute("select * from artists")
    rows = cursor.fetchall()
    for row in rows:
        count += 1
    return count

def artists_from_db(page, per_page):
    items = []
    cursor = Tracks_db_conn()
    cursor.execute("select * from artists")
    rows = cursor.fetchall()
    end = page * per_page
    if end > len(rows):
        end = len(rows)
    for i in range((page -1) * per_page, end):
        row = rows[i]
        items.append({
        'artist_id': row.artist_id,
        'name': row.name,
        'count': len_db_artist()
        })
    return items

def artist_by_id(id):
    cursor = Tracks_db_conn()
    cursor.execute("select * from artists where artist_id=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;

def insert_artist(id, name, year, origin, genres):
    cursor = Tracks_db_conn()
    try:
        cursor.execute("insert into artists values ("+id+", '"+name+"', '"+year+"', '"+origin+"', '"+genres+"')")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1

def update_artist(id, str, value):
    cursor = Tracks_db_conn()
    try:
        cursor.execute("update artists set "+str+"='"+value+"' where artist_id="+id)
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1


def films_for_dir():
    items = []
    cursor = Tracks_db_conn()
    cursor.execute("select * from Tracks")
    rows = cursor.fetchall()
    for row in rows:
            items.append({
            'artist_id': row.artist_id,
            'track': row.track,
            })
    return items;


def track_by_id(id):
    cursor = Tracks_db_conn()
    cursor.execute("select * from tracks where track_id=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;

def insert_track(id, track, artistId, album, year, genre):
    cursor = Tracks_db_conn()
    try:
        cursor.execute("insert into tracks "+
                       "([track_id],[track],[artist_id],[album],[year],[genre])values ('"
                       +id+"', '"+track+"', '"+ artistId+"','"+ album+"','"+year+"', '"+genre+"')")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1

def update_track(id, str, value):
    cursor = Tracks_db_conn()
    try:
        if str == 'album' or str == 'year' or str == 'genre' or str == 'track' or str=='artist_id':
            cursor.execute("update tracks set "+str+"='"+value+"' where track_id='"+id+"'")
            cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1

def del_track(id):
    cursor = Tracks_db_conn()
    cursor.execute("delete from tracks where track_id='"+id+"'")
    cursor.commit()


###########################
def user_connected(user, code):
    cursor = users_db_conn()
    cursor.execute("select * from UsersInfo where UserName='" + user+"'")
    row = cursor.fetchone()
    if row:
        if row.Token == code:
            return 1
    return 0



def get_me(username):
    DB = users_db_conn()
    select_str = ("select * from UsersInfo where UserName = '%s'" % username)
    cursor = DB.execute(select_str)
    row = cursor.fetchone()
    if not row:
        return None
    return row
