#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from pdf2image import convert_from_path

source = r"/tmp"
target = r"/tmp/wbnk_proposal_latest"
fname = "wbnk_proposal_latest.pdf"

pages = convert_from_path(source + "/" + fname)
print(str(len(pages)))

for i, page in enumerate(pages):
  page.save(target+"/"+"p"+str(i)+".jpg", "JPEG")
  print(target+"/"+"p"+str(i).zfill(3)+".jpg" + " saved")
