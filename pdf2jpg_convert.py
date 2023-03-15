#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from pdf2image import convert_from_path
from PIL import Image

source = r"/tmp"
target = r"/tmp/wbnk_proposal_latest"
fname = "wbnk_proposal_latest.pdf"

pages = convert_from_path(source + "/" + fname)
print(str(len(pages)))

for i, page in enumerate(pages):
  image_name = "p_"+str(i+1).zfill(3)+".jpg"
  img_name = target + "/" + image_name
  page.save(img_name, "JPEG")
  print(img_name + " saved")

  img = Image.open(img_name)
  img_resize = img.resize((int(img.width / 2), int(img.height / 2)))
  img_resize.save(target + "/pages/" + image_name)
  print(img_name + " resized")


# ls pages | gawk -F'.' '{ print "<img src=pages " $0 " id=\"" $1 "\"><br>" }' > index.html
