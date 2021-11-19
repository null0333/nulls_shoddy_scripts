import re
import argparse
import requests
import io
import math
from PIL import Image, ImageDraw, ImageFont
import pickle
import sys

# chartgen.py - generates shitty lastfm-like soundcloud likes charts
# usage: ./chartgen.py <client id> <oauth> <user id>

# TODO: make multithreaded
# TODO: use API key and client ID from enviorment variables
# TODO: unpack font

font = ImageFont.truetype("cour.ttf", 15)

next_href_regx = re.compile("offset=([0-9]+)&")
sc_req_headers = {"client_id": sys.argv[1],
        "app_version": "1633940551",
        "app_locale": "en",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": sys.argv[2],
        "Connection": "keep-alive",
        "Host": "api-v2.soundcloud.com",
        "Origin": "https://soundcloud.com",
        "Referer": "https://soundcloud.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"}

next_offset = "0"
art_l = []
while True:
    print(f"scraping offset: {next_offset}")
    r = requests.get(f"https://api-v2.soundcloud.com/users/{sys.argv[3]}/likes?linked_partitioning=1&limit=50&offset={next_offset}",
                     headers=sc_req_headers)

    r_json = r.json()
    if not r_json["next_href"]:
        break
    next_offset = next_href_regx.search(r_json["next_href"]).group(1)
    print(next_offset)
    print("updated next, ", r_json["next_href"])

    for track in r_json["collection"]:
        if "track" in track:
            name = track["track"]["user"]["username"] + " - " + track["track"]["title"]
            print("adding " + name)
            if track["track"]["artwork_url"]:
                r_image = requests.get(track["track"]["artwork_url"])
                art_l.append((r_image.content, name))
            else:
                r_image = requests.get(track["track"]["user"]["avatar_url"])
                art_l.append((r_image.content, name))

f_dimen = int(math.ceil(math.sqrt(len(art_l))))
im_dimen = Image.open(io.BytesIO(art_l[0][0])).width
dst = Image.new("RGB", (f_dimen * im_dimen, f_dimen * im_dimen), (0, 0, 0))
art_l_idx = 0
for height in range(f_dimen):
    for width in range(f_dimen):
        if art_l_idx >= len(art_l):
            break
        im = Image.open(io.BytesIO(art_l[art_l_idx][0]))
        dst.paste(im, (width * im_dimen, height * im_dimen))
        art_l_idx += 1

nw = 500
name_img = Image.new("RGB", (nw, f_dimen * im_dimen), (0, 0, 0))
draw = ImageDraw.Draw(name_img)
off_x = 10
off_y = 10
for track in art_l:
    if off_x >=  f_dimen * im_dimen:
        tmp = name_img
        name_img = Image.new("RGB", (tmp.width + nw, f_dimen * im_dimen), (0, 0, 0))
        name_img.paste(tmp, (0, 0))
        draw = ImageDraw.Draw(name_img)
        off_x = 10
        off_y += nw
    draw.text((off_y, off_x), track[1], font=font, fill=(255, 255, 255))
    off_x += 20

final = Image.new("RGB", (dst.width + name_img.width, dst.height), (0, 0, 0))
final.paste(dst, (0, 0))
final.paste(name_img, (dst.width, 0))

final.save("chart.png")
print("done.")
