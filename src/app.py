import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

df = pd.read_excel("./data/bike-counter-annarbor.xlsx", skiprows = 3, names = ['Datetime', "IN", "OUT"])
weather_df = pd.read_csv("./data/weather-annarbor.csv", parse_dates = ['DATE'], usecols = ['DATE', 'PRCP', 'TMAX', 'TMIN'])

app = Dash(__name__)

server = app.server

#specify layout of the dashboard
app.layout = html.Div([
    html.H1(children = ["Bicycle traffic dashboard"]),
    
    html.H2(children = dcc.Markdown("Location: [Division St. Annarbor, MI](https://maps.app.goo.gl/u5XHVAhEjpJBtMhZA)")),
    
    dcc.DatePickerRange(id = 'date', 
                        start_date = '2023-05-01',
                        end_date = '2023-09-16',
                       ),
    
    dcc.RadioItems( id = 'data_res',
                   options = {'1_week':'Weekly',
                              '1_day':'Daily',
                              '1_hour':'Hourly'
                             },
                   value = '1_day',
                   inline = True,
                  ),

    dcc.Graph(id = 'trend')
])

# specify the callback function
@app.callback(
    Output(component_id = 'trend', component_property = 'figure'),
    Input(component_id = 'date', component_property = 'start_date'),
    Input(component_id = 'date', component_property = 'end_date'),
    Input(component_id = 'data_res', component_property = 'value'),
)

def update_figure(start, end, data_res):
    
    if data_res == '1_week':
        rule = 'W'
    elif data_res == '1_day':
        rule = 'D'
    elif data_res == '1_hour':
        rule = 'H'
        
    df_updated = (df
                  .set_index("Datetime")
                  .resample(rule)
                  .sum()
                  .assign(total = lambda x : x['IN'] + x['OUT'], day_of_week = lambda x : x.index.day_name())
                  .loc[start:end]
                  .join(weather_df.set_index('DATE'))
                 )
    
    fig = px.bar(df_updated, x = df_updated.index, y = 'total', hover_data = ['IN', 'OUT', 'day_of_week', 'TMAX', 'TMIN', 'PRCP'])

    return fig

if __name__=='__main__':
    app.run(jupyter_mode = 'external', debug = True, port = 8052)