print("\n*!~!* created by Techoholic *!~!*\n")
import spotipy
import json
from time import time, sleep
import pytz, dateutil.parser
from spotipy.oauth2 import SpotifyOAuth

print("Authenticating with Spotify...")
scope = "user-library-read user-read-recently-played"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="439b2971705d4f93902b4c60162014ec",client_secret="23e0a68e6acd4dd6a41f37c05495db33",redirect_uri="http://example.com",scope=scope))
print("Done! Now saving Spotify listens to history.json :)")

after = str(int(time()))+'000'
while True:
    tracks = sp.current_user_recently_played(after=after,limit=50)
    if tracks['cursors']:
        after = tracks['cursors']['after']
        tracks_clean = []
        for idx, item in enumerate(tracks['items']):
            try:
                track = item[1]['track']
            except:
                track = item['track']
            artists = []
            for a in enumerate(track['artists']):
                artists.append(a[1]['name'])
            utctime = dateutil.parser.parse(item['played_at']) #didn't write these two lines but they make the iso-8601->local time conversion work
            localtime = utctime.astimezone(pytz.timezone("America/Los_Angeles"))

            tracks_clean.append({'name':track['name'], 'artists':artists, 'album':track['album']['name'], 'datetime':str(localtime), 'user_link':track['external_urls']['spotify'], 'id':track['id'], 'album_img':track['album']['images'][0]['url'], 'context':item['context']})
        file = open("history.json", 'a+')
        tracks_clean.reverse()
        for t in tracks_clean:
            file.write(json.dumps(tracks_clean)[1:-1] + '\n') #string slicing to remove brackets
        file.close()
        print("Logged", len(tracks_clean), "songs:", ''.join(t['name'] + ', ' for t in tracks_clean))
    else:
        print("No new listens")
    sleep(60)
    print("\nChecking for new listens...")
