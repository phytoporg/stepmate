from flask import Flask
from flask import request, render_template

app = Flask(__name__)

# TODO: replace with a real storage solution
SONGS = []

@app.route("/")
def first_function():
    return "<html><body><h1 style='color:red'>I am hosted on Raspberry Pi !!!</h1></body></html>"

@app.route("/api/songs/list", methods=['GET'])
def list():
    return { 'songs' : SONGS }

@app.route("/api/songs/add", methods=['POST'])
def add():
    new_song = request.json
    for k in ['title', 'artist', 'group']:
        if not k in new_song.keys():
            return f'Missing song data: {k}', 400

    if new_song not in SONGS:
        SONGS.append(new_song)
        print(f'Got new song: {new_song}')
    else:
        print(f'Song {new_song} is a duplicate. Not adding.')

    return 'Success!', 200

@app.route("/songs", methods=['GET'])
def songs():
    return render_template('songs.html', songs=SONGS)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

