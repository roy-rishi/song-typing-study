import pandas
from datetime import datetime
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import cred

SONG_DATA_PATH="song-log.json"

# load monkeytype data
dfs = pandas.read_html("monkeytype-complete.html")
df = dfs[0]
df.drop(["Unnamed: 0", "chars", "mode", "info", "tags"], axis=1, inplace=True)
df.to_csv("monkeytype-converted.csv", index=False)

# authenticate spotify
auth_manager = SpotifyClientCredentials(client_id=cred.client_id, client_secret=cred.client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


def typingStringToEpoch(typing_date):
    date_format = "%d %b %Y %H:%M"
    dt = datetime.strptime(typing_date, date_format)
    return int(dt.timestamp())

def songStringToEpoch(song_date):
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    dt = datetime.strptime(song_date, date_format)
    return int(dt.timestamp())

def checkTimeMatch(song_ts, song_duration, typing_ts):
    song_ts -= 25200 # convert to PT from UTC
    song_ts
    high_bound = int(song_ts) + 30
    low_bound= int(song_ts) - int(song_duration) - 30

    if typing_ts > low_bound and typing_ts < high_bound:
        return True
    return False

def searchConcurrentSong(typing_ts, song_log):

    for song in song_log:
        song_name = song["master_metadata_track_name"]
        duration = song["ms_played"]

        song_date = song["ts"]
        song_ts = songStringToEpoch(song_date)

        if checkTimeMatch(song_ts, duration / 1000, typing_ts):
            return {"name":song_name,"track_uri":song["spotify_track_uri"]}
    return {"name":"no_matches","track_uri":"no_matches"}


song_log = None
with open(SONG_DATA_PATH) as dataFile:
    song_log = json.load(dataFile)

epochs = []
songs = []
track_uris = []
bpms = []
artist_genres = []

for index, row in df.iterrows():
    typing_date = df.loc[index, "date"]

    typing_epoch = typingStringToEpoch(typing_date)
    epochs.append(typing_epoch)
    print(typing_date, typing_epoch)

    search = searchConcurrentSong(typing_epoch, song_log)
    name = search["name"]
    uri = search["track_uri"]
    songs.append(name)
    track_uris.append(uri)
    print(name, uri)

# get track info (bpm, genres)
    if name != "no_matches":
        try:
            analysis = sp.audio_analysis(uri)
        except:
            print("ERROR getting audio analysis")
            bpm = "unable_to_retrieve"
        else:
            bpm = analysis["track"]["tempo"]
        print(bpm)
        bpms.append(bpm)

        try:
            result = sp.search(name)
            track = result['tracks']['items'][0]
            artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
            genres = ", ".join(artist["genres"])
        except:
            print("ERROR searching for genres")
            genres = "unable_to_retrieve"
        else:
            artist_genres.append(genres)
        print(genres)
    else:
        bpms.append("no_matches")
        artist_genres.append("no_matches")
    print()


df["epoch"] = epochs
df["song"] = songs
df["track uri"] = track_uris

df["tempo (bpm)"] = bpms
df["artist genres"] = artist_genres

print(df)

df.to_csv("typing-with-songs.csv", index=False)
