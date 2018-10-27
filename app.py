import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import fantrax
#import Teams as teams

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("Fantrax Fantasy"),
    ]),
    dcc.Tabs(
        className='button-primary',
        id='tabs',
        style={"height":"20","verticalAlign":"middle"},
                children=[
                    dcc.Tab(className='custom-tab', label="Teams comparison", value="teams_tab"),
                    dcc.Tab(className='custom-tab', label="Roster progress", value="roster_tab"),
                    dcc.Tab(className='custom-tab', label="Players", value="players_tab"),
                ],
                value="teams_tab",
    ),
    html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
])

@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "teams_tab":
        return teams_layout()
    elif tab == "roster_tab":
        return None
    elif tab == "players_tab":
        return None
    else:
        return teams.layout()

dfYtd, dfProj = fantrax.get_teams_categories()
renameDict = {}
for col in dfYtd.columns:
    renameDict[col] = col.split('_')[0]
dfYtd.rename(renameDict, axis='columns', inplace=True)

renameDict = {}
for col in dfProj.columns:
    renameDict[col] = col.split('_')[0]
dfProj.rename(renameDict, axis='columns', inplace=True)

for col in dfYtd.columns:
    if dfYtd[col].dtype == np.float64:
        dfYtd[col] = dfYtd[col].round(2)
        dfProj[col] = dfProj[col].round(2)

#df_norm = (dfYtd - dfYtd.mean()) / (dfYtd.max() - dfYtd.min())
df_norm=dfYtd

teamNames = dfYtd['Status']
labels = dfYtd.columns[1:]

marksLabels = {i: '' for i in range(10)}
marksLabels[0] = 'Projected'
marksLabels[10] = 'YTD'

def teams_layout():
    retLayout = html.Div([
    # dcc.RadioItems(
    #     options=[
    #         {'label': teamNames[i], 'value': teamNames[i]} for i in range(len(teamNames))
    #     ],
    #     value=teamNames[0]
    # ),
    dcc.Graph(
        id='compareRadio',
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
def update_bar(input_value):
    df_norm = pd.DataFrame()
    df_norm['Status'] = dfYtd['Status']
    for col in dfYtd.columns:
        if col in ['FTA','FTM','FGA','FGM']:
            continue
        if dfYtd[col].dtype == np.float64:
            df_norm[col] = dfYtd[col]*(input_value/10)+dfProj[col]*(1-input_value/10)
    traces = []
    rangeDict = {
        'FG%': 100,
        'FT%': 100,
        'PTS': 1000,
        'TO': 150,
        'BLK': 100,
        'ST': 100,
        'AST': 200,
        'REB': 400,
        '3PTM': 150,
    }
    for i in range(len(dfYtd)):
        traces.append(go.Bar(
            y= df_norm.columns[1:],
            x= df_norm.iloc[i].values[1:],
            name=df_norm.iloc[i].values[0],
            orientation = 'h',
            visible='legendonly' if i>=2 else True
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            barmode='group',
            showlegend=True,
        )
    }


@app.callback(
    Output(component_id='compareRadio', component_property='figure'),
    [Input(component_id='projectedYtdAlphaSlider', component_property='value')]
)
def update_radio(input_value):
    df_norm = pd.DataFrame()
    df_norm['Status'] = dfYtd['Status']

    rangeDict = {
        'FG%': 100,
        'FT%': 100,
        'PTS': 1000,
        'TO': 150,
        'BLK': 100,
        'ST': 100,
        'AST': 200,
        'REB': 400,
        '3PTM': 150,
    }

    for col in dfYtd.columns:
        if col in ['FTA','FTM','FGA','FGM']:
            continue
        if dfYtd[col].dtype == np.float64:
            df_norm[col] = dfYtd[col]*(input_value/10)+dfProj[col]*(1-input_value/10)
            df_norm[col] = df_norm[col]/rangeDict[col]
    traces = []

    for i in range(len(df_norm)):
        traces.append(go.Scatterpolar(
                        r = df_norm.iloc[i].values[1:],
                        theta = df_norm.columns[1:],
                        mode = 'lines',
                        fill='tonext',
                        name=df_norm.iloc[i].values[0],
                        connectgaps=True,
                        visible='legendonly' if i>=2 else True
                    ))
    return {
        'data': traces,
        'layout': go.Layout(
            showlegend=True,
            autosize=False,
            polar = dict(
                        # domain = dict(
                        #     x = [0,0.4],
                        #     y = [0,1]
                        # ),
                        radialaxis = dict(
                            # tickfont = dict(
                            # size = 8
                            # )
                            range = [0,1]
                        )
            )
        )
    }

if __name__ == '__main__':
    app.run_server()