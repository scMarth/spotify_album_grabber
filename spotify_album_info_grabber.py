import requests, re, urllib, os

def download_album_thumb(html_data, dir_path):
    expression = r'<meta[\s]+property="og:image"[\s]+content="(http[^"]+)"'
    img_url = re.findall(expression, html_data)[0]                     # Find image url from the HTML
    img_name = re.findall(r'([^/]+)$', img_url)[0] + ".jpg"         # Make a filename based on the url

    print(img_url)
    print(img_name)

    file_path = dir_path + '\\' + img_name
    urllib.request.urlretrieve(url=img_url, filename=file_path)      # Download the image



def print_album_info(html_data, destination):

    # get the album name
    expression = r'<h1><span[\s]+dir="auto">([^<]+)</span></h1>'
    album_name = re.findall(expression, html_data)[0]
    print(album_name)

    # get the artist name
    '''
    <h2>By <a href="/artist/7dGJo4pcD2V6oG8kP0tJRR?highlight=spotify%3Atrack%3A7FIWs0pqAYbP91WWM0vlTQ">Eminem</a></h2>
    '''

    expression = r'<h2>By[\s]+<a[\s]+href="/artist/[^"]+">([^<]+)</a></h2>'
    artist_name = re.findall(expression, html_data)[0]
    print(artist_name)

    # get the year and number of songs
    expression = r'<p[\s]+class="text-silence[\s]+entity-additional-info">([^<]+)</p>'
    year_and_num_songs = re.findall(expression, html_data)[0].split(' &bull; ')
    print(year_and_num_songs)

    # get the track data
    # expression = r'<li[\s]+class="tracklist-row[\s]+js-track-row[\s+]tracklist-row--track[\s+]track-has-preview.*</li>'
    expression = r'<li[\s]+class="tracklist-row[\s]+js-track-row[\s]+tracklist-row--track.*?</li>'
    track_html = re.findall(expression, html_data, re.S)
    print(len(track_html))



'''

<li
            class="tracklist-row js-track-row tracklist-row--track track-has-preview"
            data-position="1"
            tabindex="0"
            role="button"><div class="tracklist-col position-outer"><div class="play-pause middle-align"><svg class="svg-play" role="button" aria-label="Play"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#icon-play"></use></svg><svg class="svg-pause" role="button" aria-label="Pause"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#icon-pause"></use></svg></div><div class="tracklist-col__track-number position middle-align">
                      1.
                  </div></div><div class="tracklist-col name"><div class="middle-align track-name-wrapper"><span class="track-name" dir="auto">Premonition - Intro</span></div></div><div class="tracklist-col explicit"><div class="middle-align"><svg title="Explicit" class="icon-explicit"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#icon-explicit"></use></svg></div></div><div class="tracklist-col duration"><div class="middle-align"><span class="total-duration">2:53</span><span class="preview-duration">0:30</span></div></div><div class="progress-bar-outer"><div class="progress-bar"></div></div></li>

'''


# debug dump html data to a target directory
def debug_print(html_data, dir_path, file_name):
    with open(dir_path + '\\' + file_name, 'w', encoding='utf-8') as debug_file:
        debug_file.write(html_data)

# use this to specify the output path of downloaded thumb images
config = {
    'specify_path' : False,
    'album_art_path' : r'C:\Users\vince\Pictures\Album Art'
}

with open(os.path.dirname(__file__) + r'/album_urls.txt', 'r') as file:
    for line in file:
        r = requests.get(line.strip()) # Get the HTML
        debug_print(r.text, os.path.dirname(__file__), 'debug.txt')
        try:
            download_album_thumb(r.text, config['album_art_path'] if config['specify_path'] else os.path.dirname(__file__))
            print_album_info(r.text, os.path.dirname(__file__))
        except:
            try:
                # If something went wrong, try to dump the result of the request
                debug_filename = re.findall(r'([^/]+)$', line.strip())[0] + ".txt"
                debug_print(r.text, os.path.dirname(__file__), debug_filename)
            except:
                continue