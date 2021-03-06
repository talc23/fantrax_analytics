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
app.config['suppress_callback_exceptions'] = True

server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("Fantrax Fantasy"),
    ]),
    dcc.Tabs(
        className='button-primary',
        id='tabs',
        style={"height": "20", "verticalAlign": "middle"},
        children=[
            dcc.Tab(className='custom-tab',
                    label="Teams comparison", value="teams_tab"),
            dcc.Tab(className='custom-tab',
                    label="Roster progress", value="roster_tab"),
            dcc.Tab(className='custom-tab',
                    label="Players", value="players_tab"),
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
df_norm = dfYtd

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
        html.Div([
            html.Div([
                html.P(
                    "Choose Team",
                    style={
                        "textAlign": "left",
                        "marginBottom": "2",
                        "marginTop": "4",
                    },
                ),
                dcc.Dropdown(
                    id='left-dropdown',
                    options=[
                        dict(label=df_norm.iloc[i].values[0], value=df_norm.iloc[i].values[0]) for i in range(len(df_norm['Status']))
                    ],
                    value=df_norm.iloc[0].values[0],
                    clearable=False
                ),
            ],
                className="six columns",
            ),
            html.Div([
                html.P(
                    "Choose Team",
                    style={
                        "textAlign": "left",
                        "marginBottom": "2",
                        "marginTop": "4",
                    },
                ),
                dcc.Dropdown(
                    id='right-dropdown',
                    options=[
                        dict(label=df_norm.iloc[i].values[0], value=df_norm.iloc[i].values[0]) for i in range(len(df_norm['Status']))
                    ],
                    value=df_norm.iloc[1].values[0],
                    clearable=False
                ),
            ],
                className="six columns",
            ),
        ],
            className="row",
            style={"paddingTop": "2%"},
        ),
        html.P(
            "Slide left to give more weight to projected stats, or right for Year-To-Date stats",
            style={
                "textAlign": "center",
                "marginBottom": "2",
                "marginTop": "4",
            },
        ),
        dcc.Slider(
            id='projectedYtdAlphaSlider',
            min=0,
            max=10,
            step=0.5,
            marks=marksLabels,
            value=2
        ),
        dcc.Graph(
            id='compareRadio',
        ),
        dcc.Graph(
            id='compareFactBar',
        )
    ])
    return retLayout


@app.callback(
    Output(component_id='right-dropdown', component_property='options'),
    [Input(component_id='left-dropdown', component_property='value')]
)
def update_left_dropdown(input_value):
    options = []
    for i in range(len(df_norm['Status'])):
        isDisabled = False
        if df_norm.iloc[i].values[0] == input_value:
            isDisabled = True
        options.append(dict(
            label=df_norm.iloc[i].values[0], value=df_norm.iloc[i].values[0], disabled=isDisabled))
    return options


@app.callback(
    Output(component_id='left-dropdown', component_property='options'),
    [Input(component_id='right-dropdown', component_property='value')]
)
def update_right_dropdown(input_value):
    options = []
    for i in range(len(df_norm['Status'])):
        isDisabled = False
        if df_norm.iloc[i].values[0] == input_value:
            isDisabled = True
        options.append(dict(
            label=df_norm.iloc[i].values[0], value=df_norm.iloc[i].values[0], disabled=isDisabled))
    return options


@app.callback(
    Output(component_id='compareFactBar', component_property='figure'),
    [Input(component_id='projectedYtdAlphaSlider', component_property='value'),
     Input(component_id='left-dropdown', component_property='value'),
     Input(component_id='right-dropdown', component_property='value')]
)
def update_bar(input_value, left_team, right_team):
    df_norm = pd.DataFrame()
    df_norm['Status'] = dfYtd['Status']
    df_values = pd.DataFrame()
    df_values['Status'] = dfYtd['Status']
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
        if col in ['FTA', 'FTM', 'FGA', 'FGM']:
            continue
        if dfYtd[col].dtype == np.float64:
            df_values[col] = dfYtd[col] * \
                (input_value/10)+dfProj[col]*(1-input_value/10)
            df_norm[col] = df_values[col] / rangeDict[col]
    traces = []

    for i in range(len(dfYtd)):
        if df_norm.iloc[i].values[0] == left_team or df_norm.iloc[i].values[0] == right_team:
            traces.append(go.Bar(
                y=df_norm.columns[1:],
                x=df_norm.iloc[i].values[1:],
                customdata=df_values.iloc[i].values[1:],
                text=df_values.iloc[i].values[1:],
                hoverinfo='name+text',
                name=df_norm.iloc[i].values[0],
                orientation='h',
                #visible='legendonly' if i >= 2 else True
            ))

    layoutDict = {
        'barmode': 'group',
        'showlegend': True,
        'xaxis': dict(visible=False, range=[0, 1])
    }

    return {
        'data': traces,
        'layout': go.Layout(layoutDict
                            )
    }


@app.callback(
    Output(component_id='compareRadio', component_property='figure'),
    [Input(component_id='projectedYtdAlphaSlider', component_property='value'),
     Input(component_id='left-dropdown', component_property='value'),
     Input(component_id='right-dropdown', component_property='value')]
)
def update_radio(input_value, left_team, right_team):
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
        if col in ['FTA', 'FTM', 'FGA', 'FGM']:
            continue
        if dfYtd[col].dtype == np.float64:
            df_norm[col] = dfYtd[col] * \
                (input_value/10)+dfProj[col]*(1-input_value/10)
            df_norm[col] = df_norm[col]/rangeDict[col]
    traces = []

    for i in range(len(df_norm)):
        if df_norm.iloc[i].values[0] == left_team or df_norm.iloc[i].values[0] == right_team:
            traces.append(go.Scatterpolar(
                r=df_norm.iloc[i].values[1:],
                theta=df_norm.columns[1:],
                mode='lines',
                fill='tonext',
                name=df_norm.iloc[i].values[0],
                connectgaps=True,
            ))
    return {
        'data': traces,
        'layout': go.Layout(
            showlegend=True,
            autosize=False,
            polar=dict(
                radialaxis=dict(
                    range=[0, 1],
                    visible=False,
                ),

            )
        )
    }


if __name__ == '__main__':
    app.run_server()
