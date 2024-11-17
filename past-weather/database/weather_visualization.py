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
            x='일자:T',
            y=alt.Y('온도(°C):Q', axis=alt.Axis(title='온도(°C)')),
            tooltip=['일자:T', '온도(°C):Q']
        )
        return temperature_chart

    def humidity_chart(self):
        humidity_chart = alt.Chart(self.df).mark_line(color='gray').encode(
            x='일자:T',
            y=alt.Y('습도(%):Q', axis=alt.Axis(title='습도(%)')),
            tooltip=['일자:T', '습도(%):Q']
        )
        return humidity_chart

    def precipitation_chart(self):
        precipitation_chart = alt.Chart(self.df).mark_bar(color='blue', opacity=0.5).encode(
            x='일자:T',
            y=alt.Y('강수량(mm):Q', axis=alt.Axis(title='강수량(mm)', orient='right')),
            tooltip=['일자:T', '강수량(mm):Q']
        )
        return precipitation_chart
    
    def temperature_layer(self, width='container', height=200):
        temperature_layer = self.temperature_chart().properties(
            height=height
        ).encode(
            x=alt.X(
                '일자:T',
                axis=alt.Axis(title='월' if self.type == 'monthly' else '일', format='%m' if self.type == 'monthly' else '%d')
            )
        )
        return temperature_layer

    def humidity_precipitation_layer(self, width='container', height=200):
        # 습도와 강수량 차트를 수직으로 결합
        humidity_precipitation_layer = alt.layer(
            self.humidity_chart().encode(
                x=alt.X(
                    '일자:T',
                    axis=alt.Axis(title='월' if self.type == 'monthly' else '일', format='%m' if self.type == 'monthly' else '%d')
                )
            ),
            self.precipitation_chart().encode(
                x=alt.X(
                    '일자:T',
                    axis=alt.Axis(title='월' if self.type == 'monthly' else '일', format='%m' if self.type == 'monthly' else '%d')
                )
            )
        ).resolve_scale(
            y='independent'  # y축을 독립적으로 설정
        ).properties(
            height=height
        )
        return humidity_precipitation_layer

    def combined_chart(self, width='container', height=200):
        '''
        온도, 습도, 강수량 차트를 수직으로 결합
        '''
        combined_layer = alt.vconcat(
            self.temperature_layer(width=width, height=height),
            self.humidity_precipitation_layer(width=width, height=height)
        ).properties(
        ).configure_mark(
            strokeWidth=1,
            opacity=0.8
        ).configure_axis(
            labelFontSize=14,
            titleFontSize=16
        )
        return combined_layer
