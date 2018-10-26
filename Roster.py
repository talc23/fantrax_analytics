import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import fantrax

dfFact, labelsFact = fantrax.get_players_mean(True)
df, labels = fantrax.get_players_mean(False)

stats = {}
for i in df.Status.unique():
    stats[i] = df[df['Status'] == i][labels].values[0]
    stats[i] = np.append(stats[i], stats[i][0])

labels = np.append(labels, labels[0])

statsfact = {}
for i in dfFact.Status.unique():
    statsfact[i] = dfFact[dfFact['Status'] == i][labelsFact].values[0]
    statsfact[i] = np.append(statsfact[i],statsfact[i][0])

labelsFact = np.append(labelsFact, labelsFact[0])

teamNames = list(df['Status'])

def layout():
    retLayout = html.Div([
    html.H1('Mean of all players per team, factorized by games per player'),
    dcc.RadioItems(
        options=[
            {'label': teamNames[i], 'value': teamNames[i]} for i in range(len(teamNames))
        ],
        value='MTL'
    ),
    dcc.Graph(
        id='compareFact',
        figure={
            'data': [
                go.Scatterpolar(
                    r = dfFact.iloc[i].values[1:],
                    theta = labelsFact,
                    mode = 'lines',
                    fill='toself',
                    name=dfFact.iloc[i].values[0],
                    visible='legendonly' if i>=2 else True
                ) for i in range(len(df))
               
            ],
            'layout': go.Layout({
                'showlegend': True,

            })
        }
    )
    ])
    return retLayout