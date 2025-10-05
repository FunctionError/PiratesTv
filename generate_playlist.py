import os
import requests
import re

def is_channel_live(url):
    try:
        response = requests.get(url, stream=True, timeout=5)
        # First check if the response is OK
        if response.status_code == 200:
            try:
                # Then try to read the first chunk of content
                next(response.iter_content(1024))
                return True
            except StopIteration:
                return False
        return False
    except requests.RequestException:
        return False
    finally:
        if 'response' in locals():  
            response.close()

def read_m3u_playlist(source):
    playlist = []
    if source is None:
        print("Error: Playlist source URL is None")
        return []

    if source.startswith("http"):
        try:
            response = requests.get(source)
            content = response.text
        except requests.RequestException as e:
            print(f"Error fetching playlist from {source}: {e}")
            return []
    else:
        try:
            with open(source, 'r') as f:
                content = f.read()
        except IOError as e:
            print(f"Error reading file {source}: {e}")
            return []

    pattern = re.compile(r'#EXTINF:(.*?)(?: tvg-logo="(.*?)")?(?: group-title="(.*?)")?,(.*?)\n(.*?)\n', re.DOTALL)
    matches = pattern.findall(content)
    
    for match in matches:
        duration, logo, group, channel_name, url = match
        if '.m3u8' in url and is_channel_live(url):
            playlist.append({'logo': logo, 'group': group, 'channel_name': channel_name, 'url': url})
    return playlist

def combine_playlists(playlist_sources, priority_order):
    combined_playlist = []
    seen_channels = set()

    for source in priority_order + playlist_sources:
        source_playlist = read_m3u_playlist(source)
        for channel in source_playlist:
            channel_identity = (channel['channel_name'].strip().lower(), channel['url'].strip())
            if channel_identity not in seen_channels:
                seen_channels.add(channel_identity)
                combined_playlist.append(channel)

    return combined_playlist

def write_to_file(playlist, output_file, include_credits=False, promo_channel=None):
    credit_text = "# All the links in this file are collected from public sources. If anyone wants to remove their source, please let us know. We respect your opinions and efforts, so we will not object to removing your source. https://www.t.me/PiratesTv_ch\n"
    with open(output_file, 'w') as f:
        f.write("#EXTM3U\n")  
        if include_credits:
            f.write(credit_text)
        # Write promo channel first if provided
        if promo_channel:
            f.write("#EXTINF:-1 tvg-logo=\"%s\" group-title=\"Promo\",%s\n%s\n" % (
                promo_channel['logo'], promo_channel['channel_name'], promo_channel['url']
            ))
        # Write normal playlist channels
        for item in playlist:
            f.write("#EXTINF:-1 tvg-logo=\"%s\" group-title=\"%s\",%s\n%s\n" % (item['logo'], item['group'], item['channel_name'], item['url']))

if __name__ == "__main__":
    playlist_sources = [
        os.getenv('PLAYLIST_SOURCE_URL_1'),
        os.getenv('PLAYLIST_SOURCE_URL_2'),
        os.getenv('PLAYLIST_SOURCE_URL_3')  
    ]
    priority_order = [
        os.getenv('PRIORITY_PLAYLIST_URL_1'),
        os.getenv('PRIORITY_PLAYLIST_URL_2'),
        os.getenv('PRIORITY_PLAYLIST_URL_3')  
    ]
    output_file = 'combined_playlist.m3u'
    include_credits = True  

    combined_playlist = combine_playlists(playlist_sources, priority_order)

    # ------------------------------------------------  Define promo channel ------------------------------------------------
    promo_channel = {
        'logo': 'https://raw.githubusercontent.com/falconcasthoster/images/refs/heads/main/FalconCast.png',
        'channel_name': 'FalconCast',
        'url': 'https://raw.githubusercontent.com/falconcasthoster/promo/refs/heads/main/nolink/master.m3u8'
    }

    write_to_file(combined_playlist, output_file, include_credits, promo_channel)

    print("Combined and filtered playlist written to", output_file)
