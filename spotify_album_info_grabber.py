import requests, re, urllib, os, html

# return unescaped html
def unescape_html(html_data):
    return html.unescape(html_data)

def find_expr_in_html(expr, html):
    return re.findall(expr, html, re.S)

def print_album_info(html_data, album_info_destination, album_thumb_destination):

    # get the album name
    album_name = find_expr_in_html(
        r'<h1><span[\s]+dir="auto">([^<]+)</span></h1>',
        html_data
    )[0]

    # get the artist name
    '''
    <h2>By <a href="/artist/7dGJo4pcD2V6oG8kP0tJRR?highlight=spotify%3Atrack%3A7FIWs0pqAYbP91WWM0vlTQ">Eminem</a></h2>
    '''
    artist_name = find_expr_in_html(
        r'<h2>By[\s]+<a[\s]+href="/artist/[^"]+">([^<]+)</a></h2>',
        html_data
    )[0]

    # get the year and number of songs
    year_and_num_songs = find_expr_in_html(
        r'<p[\s]+class="text-silence[\s]+entity-additional-info">([^<]+)</p>',
        html_data
    )[0].split(' &bull; ')

    # get the track data
    tracks_html = find_expr_in_html(
        r'<li[\s]+class="tracklist-row[\s]+js-track-row[\s]+tracklist-row--track.*?</li>',
        html_data
    )
    track_data = []
    for track_html in tracks_html:

        track_info = {}

        # get the track number
        track_num = find_expr_in_html(r'data-position="([^"]+)"', track_html)[0]
        track_info['track number'] = track_num
        
        # get the song name
        song_title = find_expr_in_html(
            r'<span[\s]+class="track-name[^>]*>([^<]+)</span>',
            track_html
        )[0]
        song_title = unescape_html(song_title) # unescape html
        track_info['song title'] = song_title

        # get featured artists
        featured_artists = find_expr_in_html(
            r'<a[\s]+href="/artist/[^>]*><span[\s]+dir="auto">([^<]+)</span></a>',
            track_html
        )

        # for some reason, we need to doubly unescape artist names...
        featured_artists = [unescape_html(unescape_html(artist)) for artist in featured_artists]
        track_info['featured artists'] = featured_artists

        track_data.append(track_info)

    # download the album thumb

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
    with open(album_info_file, 'w') as info_file:
        info_file.write(album_name + '\n')
        info_file.write(artist_name + '\n')
        info_file.write(year_and_num_songs[0] + '\n')
        info_file.write(year_and_num_songs[1] + '\n\n')

        for track in track_data:
            info_file.write(track['track number'] + '\n')
            info_file.write(track['song title'] + '\n')

            info_file.write(artist_name)
            if track['featured artists']:
                info_file.write(' ft. ' + ', '.join(track['featured artists']) + '\n')
            else:
                info_file.write('\n')

            info_file.write('\n')

# debug dump html data to a target directory
def debug_print(html_data, dir_path, file_name):
    with open(dir_path + '/' + file_name, 'w', encoding='utf-8') as debug_file:
        debug_file.write(html_data)

# get the path to the directory that this script resides in
script_dir = os.path.dirname(os.path.abspath(__file__))

# use this to specify the output path of downloaded thumb images
config = {
    'specify_album_art_path' : True,
    'album_art_path' : r'C:\Users\vince\Pictures\Album Art',
    'specify_album_info_path' : True,
    'album_info_path' : script_dir + '/album_info/'
}

with open(script_dir + r'/album_urls.txt', 'r') as file:
    for line in file:
        r = requests.get(line.strip()) # Get the HTML
        # debug_print(r.text, script_dir, 'debug.txt')
        try:
            
            # create output directories if they don't exist
            if config['specify_album_info_path']:
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
                debug_filename = find_expr_in_html(r'([^/]+)$', line.strip())[0] + ".txt"
                debug_print(r.text, script_dir, debug_filename)
            except:
                continue