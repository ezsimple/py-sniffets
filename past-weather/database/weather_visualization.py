# %%
import altair as alt
import pandas as pd
from core.config import logging

logger = logging.getLogger(__name__)

class WeatherVisualization(alt.Chart):
    def __init__(self, data, type='monthly'):
        # 데이터가 딕셔너리 형식인지 확인
        if not isinstance(data, dict):
            logger.error(f"Data must be a dictionary. : {data}")
            raise ValueError("Data must be a dictionary.")

        super().__init__(data)
        self.type = type
        self.df = pd.DataFrame(data)

    def temperature_chart(self):
        temperature_chart = alt.Chart(self.df).mark_line(color='red').encode(
            x=alt.X('일자:T', axis=alt.Axis(title='날짜', format='%d')),  # 날짜 형식
            y=alt.Y('온도(°C):Q', axis=alt.Axis(title='온도(°C)')),
            tooltip=['일자:T', '온도(°C):Q']
        ).properties(height=200, width=800,title='온도 변화')
        return temperature_chart

    def humidity_chart(self):
        humidity_chart = alt.Chart(self.df).mark_line(color='gray').encode(
            x=alt.X('일자:T', axis=alt.Axis(title='날짜', format='%d')),  # 날짜 형식
            y=alt.Y('습도(%):Q', axis=alt.Axis(title='습도(%)')),
            tooltip=['일자:T', '습도(%):Q']
        ).properties(height=200, width=800,title='습도 변화')
        return humidity_chart

    def precipitation_chart(self):
        precipitation_chart = alt.Chart(self.df).mark_bar(color='blue', opacity=0.5).encode(
            x=alt.X('일자:T', axis=alt.Axis(title='날짜', format='%d')),  # 날짜 형식
            y=alt.Y('강수량(mm):Q', axis=alt.Axis(title='강수량(mm)', orient='right')),
            tooltip=['일자:T', '강수량(mm):Q']
        ).properties(height=200, width=800,title='강수량 변화')
        return precipitation_chart
    
    def combined_chart(self):
        ''' 온도, 습도, 강수량 차트를 수직으로 결합 '''
        temperature_layer = self.temperature_chart()
        humidity_layer = self.humidity_chart()
        precipitation_layer = self.precipitation_chart()

        combined_layer = alt.vconcat(
            temperature_layer,
            alt.layer(
                humidity_layer,
                precipitation_layer
            ).resolve_scale(
                y='independent'
            ).properties(
                title='습도 & 강수량 변화'
            )
        ).properties(
        ).configure_mark(
            # strokeWidth=2,
            opacity=0.8
        ).configure_axis(
            # labelFontSize=14,
            # titleFontSize=16
        )
        return combined_layer