import requests, re, urllib

with open(r'./album_urls.txt', 'r') as file:
    for line in file:
        r = requests.get(line)
        expression = r'<meta[\s]+property="og:image"[\s]+content="(http[^"]+)"'
        matches = re.findall(expression, r.text)
        if matches:
            img_url = matches[0]
            expression = r'([^/]+)$'
            img_name = re.findall(expression, img_url)[0]
            urllib.request.urlretrieve(img_url, img_name + ".jpg")
        else:
            