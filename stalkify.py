print("\n*!~!* created by Techoholic *!~!*\n")
import spotipy
import json
from time import time, sleep
import pytz, dateutil.parser
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime as dt
import sys
from os import getenv
from dotenv import load_dotenv

running = True
while running:
    try:
        print("Authenticating with Spotify...")
        load_dotenv()
        CLIENT_ID = getenv('CLIENT_ID')
        CLIENT_SECRET = getenv('CLIENT_SECRET')
        REDIRECT_URI = getenv('REDIRECT_URI')
        scope = "user-library-read user-read-recently-played"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI,scope=scope))
        print("Done! Now saving Spotify listens to history.json :)")
        sp.volume(47, '020b40a16697d1e0ee100bd4fb1495eb401297dd')

        file = open("last_checked.txt", 'w+')
        afterStr = file.read()
        if afterStr:
            after = int(afterStr)
        else:
            after = int(str(int(time()))+"000")
        file.close()
        file = open("schedule.json")
        schedule = json.loads(file.read())
        file.close()
        for song in schedule:
            song['done'] = False
            song['dt'] = dt(song['dt'][0], song['dt'][1], song['dt'][2], song['dt'][3], song['dt'][4], song['dt'][5])
        while True:
            file = open("schedule.json")
            schedule = json.loads(file.read())
            file.close()
            for song in schedule:
                delta = song['dt'] - dt.now()
                if delta.total_seconds() <= -125:
                    song['done'] = True
                elif delta.total_seconds() <= 0 and not song['done']:
                    device = "020b40a16697d1e0ee100bd4fb1495eb401297dd" if song['device'] == 2 else None
                    sp.start_playback(device_id=device, uris=['spotify:track:'+song['uri']])
                    song['done'] = True
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
                file = open("last_checked.txt", 'w')
                file.write(after)
                file.close()
                print("Logged", len(tracks_clean), "songs:", ''.join(t['name'] + ', ' for t in tracks_clean))
            else:
                print("No new listens")
            sleep(60)
            print("\nChecking for new listens...")
    except KeyboardInterrupt:
        running = False
    except:
        msg = "ERROR OCCURRED ON "+str(dt.now())+str(sys.exc_info()[0])+'\n'
        print(msg)
        log = open("log.txt", 'a')
        log.write(msg)
        sleep(60)
        log.close()
