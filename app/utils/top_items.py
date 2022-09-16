from SpotifyHistory.app.utils.spotify import SpotifyHandler


s = SpotifyHandler()

artists = [artist['name'] for artist in s.get_top_artists()['items']]

print(artists)