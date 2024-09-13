# %%
from bokeh.plotting import figure, show


x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

p = figure(title="Simple line example", x_axis_label='x', y_axis_label='y')

p.line(x, y, legend_label="Temp.", line_width=2)

show(p)


# %%
from numpy.random import random

from bokeh.core.enums import MarkerType
from bokeh.plotting import figure, show

p = figure(title="Bokeh Markers", toolbar_location=None)
p.grid.grid_line_color = None
p.background_fill_color = "#eeeeee"
p.axis.visible = False
p.y_range.flipped = True

N = 10

for i, marker in enumerate(MarkerType):
    x = i % 4
    y = (i // 4) * 4 + 1

    p.scatter(random(N)+2*x, random(N)+y, marker=marker, size=14,
              line_color="navy", fill_color="orange", alpha=0.5)

    p.text(2*x+0.5, y+2.5, text=[marker],
           text_color="firebrick", text_align="center", text_font_size="13px")

show(p)