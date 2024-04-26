import os
import requests
import re

def read_m3u_playlist(source):
    playlist = []
    if source is None:
        print("Error: Playlist source URL is None")
        return []

    if source.startswith("http"):
        response = requests.get(source)
        content = response.text
    else:
        with open(source, 'r') as f:
            content = f.read()

    # Debugging: Print the content to verify it's being read correctly
    print("Content fetched:", content[:500])  # Print the first 500 characters of the content

    pattern = re.compile(r'#EXTINF:(.*?)(?: tvg-logo="(.*?)")?(?: group-title="(.*?)")?,(.*?)\n(.*?)\n', re.DOTALL)
    matches = pattern.findall(content)
    print("Matches found:", len(matches))  # Number of matches found

    for match in matches:
        duration, logo, group, channel_name, url = match
        print("Processing:", url)  # Print each URL being processed
        if '.m3u8' in url:
            playlist.append({'logo': logo, 'group': group, 'channel_name': channel_name, 'url': url})
    return playlist

def combine_playlists(playlist_sources, priority_order):
    combined_playlist = []

    for source in priority_order:
        source_playlist = read_m3u_playlist(source)
        combined_playlist.extend(source_playlist)

    priority_channels = set(channel['channel_name'] for channel in combined_playlist)
    for source in playlist_sources:
        source_playlist = read_m3u_playlist(source)
        source_playlist = [channel for channel in source_playlist if channel['channel_name'] not in priority_channels]
        combined_playlist.extend(source_playlist)

    return combined_playlist

def write_to_file(playlist, output_file):
    with open(output_file, 'w') as f:
        for item in playlist:
            f.write("#EXTINF:-1 tvg-logo=\"%s\" group-title=\"%s\",%s\n%s\n" % (item['logo'], item['group'], item['channel_name'], item['url']))

if __name__ == "__main__":
    playlist_sources = [
        os.getenv('PLAYLIST_SOURCE_URL_1'),
        os.getenv('PLAYLIST_SOURCE_URL_2')
    ]
    priority_order = [
        os.getenv('PRIORITY_PLAYLIST_URL_1'),
    ]
    output_file = 'combined_playlist.m3u'

    combined_playlist = combine_playlists(playlist_sources, priority_order)
    write_to_file(combined_playlist, output_file)

    print("Combined and filtered playlist written to", output_file)
