import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
#import numpy as np
import plotly.graph_objs as go
import fantrax

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

dfFact, labelsFact = fantrax.get_players_mean(True)
df, labels = fantrax.get_players_mean(False)

# stats = {}
# for i in df.Status.unique():
#     stats[i] = df[df['Status'] == i][labels].values[0]
#     stats[i] = stats[i].concat(stats[i][0])

# labels = labels.concat(labels[0])

# statsfact = {}
# for i in dfFact.Status.unique():
#     statsfact[i] = dfFact[dfFact['Status'] == i][labelsFact].values[0]
#     stats[i] = stats[i].concat(stats[i][0])

# labelsFact = np.append(labelsFact, labelsFact[0])

server = app.server

app.layout = html.Div([
    html.H1('Mean of all players per team'),
    dcc.Graph(
        id='compare',
        figure={
            'data': [
                go.Scatterpolar(
                    r = df[df['Status'] == i][labels].values[0],
                    theta = labels,
                    mode = 'lines',
                    fill='toself',
                    name=i
                ) for i in df.Status.unique()
               
            ],
            'layout': go.Layout({
                'showlegend': True,
                'radialaxis': { 'visible':True, 'range': [0,1]}
            })
        }
    ),
    html.H1('Mean of all players per team, factorized by games per player'),
    dcc.Graph(
        id='compareFact',
        figure={
            'data': [
                go.Scatterpolar(
                    r = dfFact[dfFact['Status'] == i][labels].values[0],
                    theta = labelsFact,
                    mode = 'lines',
                    fill='toself',
                    name=i
                ) for i in dfFact.Status.unique()
               
            ],
            'layout': go.Layout({
                'showlegend': True,

            })
        }
    )
])

if __name__ == '__main__':
    app.run_server()