#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from pdf2image import convert_from_path

source = r"/tmp"
target = r"/tmp/wbnk_proposal_latest"
fname = "wbnk_proposal_latest.pdf"

pages = convert_from_path(source + "/" + fname)
print(str(len(pages)))

for i, page in enumerate(pages):
  image_name = "p_"+str(i).zfill(3)+".jpg"
  page.save(target + "/" + image_name, "JPEG")
  print(target + "/" + image_name + " saved")
