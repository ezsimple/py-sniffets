# Bar chart
# %%

# express graph
import plotly.express as px

fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2],width=600, height=400)


fig.show()

# %%
import plotly.graph_objects as go

fig = go.Figure(data=[go.Bar(x=[1,2,3], y=[1,3,2])])

fig.update_layout(
    title_text="바차트 예제",
    width=600,
    height=400,
    margin_l=50,
    margin_r=50,
    margin_b=100,
    margin_t=100,
    # 백그라운드 칼라 지정, margin 잘 보이게 하기위함
    paper_bgcolor="LightSteelBlue",
)

# 타이틀 위치 설정부분
fig.update_layout(
                 title_x = 0.5,
                 title_y = 0.8,
                 title_xanchor = "center",
                 title_yanchor = "middle",
                 title_font_family = 'AppleGothic'
                 )

fig.show()