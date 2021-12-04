from flask import Flask
from flask import request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Don't forget to update this when changing the schema!
EXPECTED_COLS = ['title', 'artist', 'group']

# Initialize the db
db = SQLAlchemy(app)
class Song(db.Model):
    id = db.Column('song_id', db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    artist = db.Column(db.String(256))  
    group = db.Column(db.String(256))
    
    def to_dict(self):
        return {
            'title' : self.title,
            'artist' : self.artist,
            'group' : self.group,
        }

# Uncomment to reset state. DIRTY.
# db.drop_all()

db.create_all()

@app.route("/")
def first_function():
    return "<html><body><h1 style='color:red'>I am hosted on Raspberry Pi !!!</h1></body></html>"

@app.route("/api/songs/list", methods=['GET'])
def get_list():
    return { 'songs' : Song.query.all() }

@app.route("/api/songs/add", methods=['POST'])
def post_add():
    new_song = request.json
    for k in ['title', 'artist', 'group']:
        if not k in new_song.keys():
            return f'Missing song data: {k}', 400

    all_songs = Song.query.all()
    if new_song not in all_songs:
        db.session.add(Song(**new_song))

        # TODO: we need to be able to add chunks of songs
        db.session.commit()
        print(f'Got new song: {new_song}')
    else:
        print(f'Song {new_song} is a duplicate. Not adding.')

    return 'Success!', 200

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

    return {
        'data' : [song.to_dict() for song in query],
        'recordsFiltered' : num_filtered,
        'recordsTotal' : Song.query.count(),
        'draw' : request.args.get('draw', type=int)
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0')
