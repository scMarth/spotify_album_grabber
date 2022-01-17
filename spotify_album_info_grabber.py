import requests, re, urllib, os, html, shutil, sys

# return unescaped html
def unescape_html(html_data):
    return html.unescape(html_data)

def find_expr_in_html(expr, html):
    return re.findall(expr, html, re.S)

def print_album_info(html_data, album_info_destination, album_thumb_destination):
    print('\n\n')
    print('print_album_info reached')

    # <meta property="og:title" content="Thriller 25 Super Deluxe Edition" />

    # <title>A Star Is Born Soundtrack - Album by Lady Gaga, Bradley Cooper | Spotify</title><meta name="description" content="Listen to A Star Is Born Soundtrack on Spotify. Lady Gaga · Album · 2018 · 34 songs." />

    # <title>Thriller 25 Super Deluxe Edition - Album by Michael Jackson | Spotify</title><meta name="description" content="Listen to Thriller 25 Super Deluxe Edition on Spotify. Michael Jackson · Album · 1982 · 30 songs." />

    # get the album name
    album_name = find_expr_in_html(
        r'<title>(.*?)[\s]+-[\s]+[a-zA-Z]+[\s]+by',
        html_data
    )[0]
    print('album_name: ' + album_name)

    # get the artist name
    '''
    <h2>By <a href="/artist/7dGJo4pcD2V6oG8kP0tJRR?highlight=spotify%3Atrack%3A7FIWs0pqAYbP91WWM0vlTQ">Eminem</a></h2>
    <a href="/artist/3fMbdgg4jU18AjLCKBhRSm">Michael Jackson</a>
    '''
    artist_name_data = None
    artist_names = None
    try:
        artist_name_data = find_expr_in_html(
            r'<title>.*? on Spotify. (.*?) · [a-zA-Z]+',
            html_data
        )[0]

        artist_names = find_expr_in_html(
            r'<title>.*? - [a-zA-Z]+ by (.*?) \| Spotify</title><meta',
            html_data
        )[0]
        print('hi')
        print(artist_names)
    except:
        pass

    print('artist_name_data:')
    print(artist_name_data)
    print('artist_names:')
    print(artist_names)


    # <title>Thriller 25 Super Deluxe Edition - Album by Michael Jackson | Spotify</title><meta name="description" content="Listen to Thriller 25 Super Deluxe Edition on Spotify. Michael Jackson · Album · 1982 · 30 songs." />

    # get the year and number of songs
    year_and_num_songs = find_expr_in_html(
        r'<title>.*? on Spotify\. .*?· [a-zA-Z]+ \· (.*?) songs."',
        html_data
    )[0]

    year_and_num_songs = year_and_num_songs.split(' · ')


    print('year_and_num_songs')
    print(year_and_num_songs)

    # Spotify</title><meta name="description" content="Listen to Thriller 25 Super Deluxe Edition on Spotify. Michael Jackson · Album · 1982 · 30 songs."


    # get the track data
    tracks_html = find_expr_in_html(
        r'<div data-testid="track-row" class=.*?></svg></button></span></div>',
        html_data
    )

    track_data = []
    print(len(tracks_html))
    for track_html in tracks_html:

        track_info = {}


        # 1</span><div type="track"

        # get the track number
        track_num = find_expr_in_html(r'([0-9]+)</span><div type="track"', track_html)[0]
        print('track_num:{}'.format(track_num))
        track_info['track number'] = track_num
        
        # get the song name
        song_title = find_expr_in_html(
            r'aria-label="track (.*?)"',
            track_html
        )[0]
        song_title = unescape_html(song_title) # unescape html
        print('song_title:{}'.format(song_title))
        track_info['song title'] = song_title

        # <a href="/artist/3fMbdgg4jU18AjLCKBhRSm">Michael Jackson</a></span>

        # get featured artists
        featured_artists = find_expr_in_html(
            r'<a[\s]+href="/artist/[^>]*>([^<]+)</a>',
            track_html
        )
        print('featured_artists:{}'.format(featured_artists))        

        # for some reason, we need to doubly unescape artist names...
        featured_artists = [unescape_html(unescape_html(artist)) for artist in featured_artists]
        track_info['featured artists'] = featured_artists

        track_data.append(track_info)
    
    print(track_data)

    # download the album thumb

    # ><meta property="og:image" content="https://i.scdn.co/image/ab67616d0000b2734121faee8df82c526cbab2be"

    # find the image url from the html
    img_url = find_expr_in_html(
        r'<meta[\s]+property="og:image"[\s]+content="(http[^"]+)"',
        
        html_data
    )[0]

    # make a filename based on the url
    unique_id = find_expr_in_html(r'([^/]+)$', img_url)[0]
    img_name = unique_id + ".jpg"
    file_path = album_thumb_destination + '/' + img_name
    urllib.request.urlretrieve(url=img_url, filename=file_path)      # Download the image

    album_info_file = album_info_destination + '/' + unique_id + '_info.txt'
    with open(album_info_file, 'w', encoding='utf-8') as info_file:
        info_file.write(unescape_html(album_name) + '\n')
        info_file.write(artist_names + '\n')
        info_file.write(year_and_num_songs[0] + '\n')
        info_file.write(year_and_num_songs[1] + '\n\n')

        for track in track_data:
            info_file.write(track['track number'] + '\n')
            info_file.write(track['song title'] + '\n')

            if track['featured artists']:
                info_file.write(', '.join(track['featured artists']))
            info_file.write('\n')
            
            info_file.write(', '.join(track['featured artists']) + ' - ' + track['song title'])
            info_file.write('.mp3\n')

            info_file.write('\n')
    # sys.exit()

# debug dump html data to a target directory
def debug_print(html_data, dir_path, file_name):
    with open(dir_path + '/' + file_name, 'w', encoding='utf-8') as debug_file:
        debug_file.write(html_data)

# get the path to the directory that this script resides in
script_dir = os.path.dirname(os.path.abspath(__file__))

'''
    specify_album_art_path (bool): If True, album art will be written to
        'album_art_path'. If False, album art will be written to the same
        location as this script

    album_art_path (str): The directory that album art will be written to
        if 'specify_album_art_path' is True.

    specify_album_info_path (bool): If True, album info will be written to
        'album_info_path'. If False, album info will be written to the same
        location as this script

    clear_album_info (bool): If True, clears the contents of 'album_info_path',
        only if 'album_art_path' is True.
'''
config = {
    'specify_album_art_path' : False,
    'album_art_path' : r'',
    'specify_album_info_path' : True,
    'album_info_path' : script_dir + '/album_info/',
    'clear_album_info' : False
}

with open(script_dir + r'/album_urls.txt', 'r') as file:
    for line in file:
        r = requests.get(line.strip()) # Get the HTML
        # debug_print(r.text, script_dir, 'debug.txt')
        try:

            # create output directories if they don't exist
            if config['specify_album_info_path']:
                if config['clear_album_info']:
                    if os.path.exists(config['album_info_path']):
                        shutil.rmtree(config['album_info_path'])

                if not os.path.exists(config['album_info_path']):
                    os.mkdir(config['album_info_path'])

            if config['specify_album_art_path']:
                if not os.path.exists(config['album_art_path']):
                    os.mkdir(config['album_art_path'])

            print_album_info(
                r.text,
                config['album_info_path'] if config['specify_album_info_path'] else script_dir,
                config['album_art_path'] if config['specify_album_art_path'] else script_dir
            )
        except:
            try:
                # If something went wrong, try to dump the result of the request                
                debug_filename = find_expr_in_html(r'([^\?/]+)[^/]*$', line.strip())[0] + ".txt"
                debug_print(r.text, script_dir, debug_filename)
            except:
                continue
        # sys.exit()