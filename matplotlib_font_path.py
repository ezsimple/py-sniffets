#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
import matplotlib.font_manager
fpaths = matplotlib.font_manager.findSystemFonts()

for path in fpaths:
  if path.__contains__('local'):
    f = matplotlib.font_manager.get_font(path)
    print(f.family_name)
