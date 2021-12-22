from flask import Flask
from flask import request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert

import argparse
import gzip
import json
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Don't forget to update this when changing the schema!
METADATA_COLS = ['title', 'artist', 'group']
EXPECTED_COLS = ['title', 'artist', 'group', 'banner_data']

# Initialize the db
db = SQLAlchemy(app)
class Song(db.Model):
    id = db.Column('song_id', db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    artist = db.Column(db.String(256))  
    group = db.Column(db.String(256))
    banner_data = db.Column(db.Text)
    
    def metadata_dict(self):
        return {
            'title' : self.title,
            'artist' : self.artist,
            'group' : self.group,
        }

    def to_dict(self):
        return {
            'title' : self.title,
            'artist' : self.artist,
            'group' : self.group,
            'banner_data' : self.banner_data.decode('utf-8')
        }

db.create_all()
# db.drop_all()

@app.route("/")
def first_function():
    return "<html><body><h1 style='color:red'>I am hosted on Raspberry Pi !!!</h1></body></html>"

@app.route("/api/songs/list", methods=['GET'])
def get_list():
    return { 'songs' : Song.query.all() }

@app.route("/api/songs/add", methods=['POST'])
def post_add():
    gz_songs = request.data
    songs_decompressed = gzip.decompress(gz_songs)
    songs = json.loads(songs_decompressed.decode('utf-8'))

    # Not sure how to do this efficiently :(
    added, dups = [], []

    all_songs = [r.metadata_dict() for r in db.session.query(Song).all()]
    for song in songs:
        # Reencode binary data
        # song['banner_data'] = song['banner_data'].decode('utf-8')
        #print(song['banner_data'])

        if { k : song[k] for k in METADATA_COLS } in all_songs:
            dups.append(song)
        else:
            added.append(song)
            db.session.add(Song(**song))
            
    db.session.commit()
    print(f'Added {len(added)} new songs')
    print(f'Saw {len(dups)} duplicates')

    # TODO: log levels to dump added, dups

    return jsonify({
        'num_new_songs' : len(added),
        'num_duplicates' : len(dups),
        }), 200

@app.route("/songs", methods=['GET'])
def get_songs():
    return render_template('songs.html', title='Stepmate Song Search')

@app.route("/api/data")
def api_data():
    query = Song.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Song.title.like(f'%{search}%'),
            Song.artist.like(f'%{search}%'),
            Song.group.like(f'%{search}%'),
        ))
    num_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in EXPECTED_COLS:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Song, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    data = [song.to_dict() for song in query]
    return {
        'data' : data,
        'recordsFiltered' : num_filtered,
        'recordsTotal' : Song.query.count(),
        'draw' : request.args.get('draw', type=int)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drop-db', action='store_true')

    args = parser.parse_args()
    if args.drop_db:
        db.drop_all()


    app.run(host='0.0.0.0')
