# %%
import plotly.graph_objects as go 

fig = go.Figure(
    data=[go.Bar(x=[1,2,3], y=[4,5,6])],
    layout=go.Layout(
        title=go.layout.Title(text='막대그래프')
    )
)

fig.show()