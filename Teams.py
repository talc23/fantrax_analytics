import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from app import app
from dash.dependencies import Input, Output


import pandas as pd
import numpy as np
import fantrax

dfYtd, dfProj = fantrax.get_teams_categories()
renameDict = {}
for col in dfYtd.columns:
    renameDict[col] = col.split('_')[0]
dfYtd.rename(renameDict, axis='columns', inplace=True)
for col in dfYtd.columns:
    if dfYtd[col].dtype == np.float64:
        dfYtd[col] = dfYtd[col].round(2)

#df_norm = (dfYtd - dfYtd.mean()) / (dfYtd.max() - dfYtd.min())
df_norm=dfYtd

teamNames = dfYtd['Status']
labels = dfYtd.columns[1:]

marksLabels = {i: '' for i in range(10)}
marksLabels[0] = 'Projected'
marksLabels[10] = 'YTD'

def layout():
    retLayout = html.Div([
    # dcc.RadioItems(
    #     options=[
    #         {'label': teamNames[i], 'value': teamNames[i]} for i in range(len(teamNames))
    #     ],
    #     value=teamNames[0]
    # ),
    dcc.Graph(
        id='compareFact',
        figure={
            'data': [
                go.Scatterpolar(
                    r = df_norm.iloc[i].values[1:],
                    theta = labels,
                    mode = 'lines',
                    fill='toself',
                    name=dfYtd.iloc[i].values[0],
                    visible='legendonly' if i>=2 else True
                ) for i in range(len(dfYtd))
               
            ],
            'layout': go.Layout({
                'showlegend': True,

            })
        }
    ),
    dcc.Graph(
        id='compareFactBar',
    ),
    dcc.Slider(
        id='projectedYtdAlphaSlider',
        min=0,
        max=10,
        step=0.5,
        marks=marksLabels,
        value=2
    )
    ])
    return retLayout

@app.callback(
    Output(component_id='compareFactBar', component_property='figure'),
    [Input(component_id='projectedYtdAlphaSlider', component_property='value')]
)
def update_output_div(input_value):
    df_norm=dfYtd*(input_value/10)+dfProj*(1-input_value/10)
    traces = []
    for i in range(len(dfYtd)):
        traces.append(go.Bar(
            y= labels,
            x= df_norm.iloc[i].values[1:],
            name=dfYtd.iloc[i].values[0],
            orientation = 'h',
            visible='legendonly' if i>=2 else True
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            showlegend=True,
        )
    }