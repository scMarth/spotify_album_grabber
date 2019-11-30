import requests, re, urllib, os

# use this to specify the output path of downloaded thumb images
config = {
    'specify_path' : False,
    'album_art_path' : r''
}


with open(r'./album_urls.txt', 'r') as file:
    for line in file:
        r = requests.get(line.strip()) # Get the HTML
        try:
            expression = r'<meta[\s]+property="og:image"[\s]+content="(http[^"]+)"'
            img_url = re.findall(expression, r.text)[0]                     # Find image url from the HTML
            img_name = re.findall(r'([^/]+)$', img_url)[0] + ".jpg"         # Make a filename based on the url
            file_path = config['album_art_path'] + '\\' + img_name if config['specify_path'] else os.path.dirname(__file__) + '\\' + img_name
            urllib.request.urlretrieve(url=img_url, filename=file_path)      # Download the image
        except:
            try:
                # If something went wrong, try to dump the result of the request
                debug_filename = re.findall(r'([^/]+)$', line.strip())[0] + ".txt"
                with open(debug_filename, 'w') as debug_file:
                    debug_file.write(r.text)
            except:
                continue