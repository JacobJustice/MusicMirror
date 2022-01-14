"""
this is just a file I used for testing

felt bad about deleting it

"""


import sys
import json

import spotipy
import spotipy.util as util

def extract_track_id(text):
    url_ind = text.find("https://open.spotify.com/track/")
    # cut everything before the url
    track_url = text[url_ind:]
    # cut everything after the track_url if there is anything after the track_url
    if track_url.find(' ') != -1:
        track_url = track_url[:track_url.find(' ')]
    print(track_url)
    # cut everything before /track/ and after the ? (inclusive)
    track_id = track_url[track_url.find('/track/')+len('/track/'):track_url.find('?')]
    return track_id

# Load spotify credentials
spotify_cred = None
with open('./spotify.json') as f_s:
    spotify_cred = json.load(f_s)

username = spotify_cred['username']
playlist_id = spotify_cred['playlist']

scope = 'playlist-modify-public playlist-modify-private'
token = util.prompt_for_user_token(username,
                                   scope,
                                   client_id=spotify_cred['id'],
                                   client_secret=spotify_cred['secret'],
                                   redirect_uri=spotify_cred['redirect'])
print(token)

text = "Harder, Better, Faster, Stronger https://open.spotify.com/track/5W3cjX2J3tjhG8zb6u0qHn?si=9d85d635eb7945c8 this is my fav song !!"
track = '5WNYg3usc6H8N3MBEp4zVk'

track_ids = [extract_track_id(text)]
print(track_ids)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
#    print(results)
else:
    print("Can't get token for", username)


