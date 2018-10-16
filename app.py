import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import fantrax

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

dfFact, labelsFact = fantrax.get_players_mean(True)
df, labels = fantrax.get_players_mean(False)
#print(df.head())
angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False)
angles=np.concatenate((angles,[angles[0]]))
#print(angles)

# for i in df.Status.unique():
#     print(df[df['Status'] == i][labels].values)
#     break
#print(df[df['Status'] == 'GREEN'][labels].values[0])

stats = {}
for i in df.Status.unique():
    stats[i] = df[df['Status'] == i][labels].values[0]
    stats[i] = np.append(stats[i], stats[i][0])

labels = np.append(labels, labels[0])

statsfact = {}
for i in dfFact.Status.unique():
    statsfact[i] = dfFact[dfFact['Status'] == i][labelsFact].values[0]
    statsfact[i] = np.append(statsfact[i], statsfact[i][0])

labelsFact = np.append(labelsFact, labelsFact[0])

app.layout = html.Div([
    html.H1('Mean of all players per team'),
    dcc.Graph(
        id='compare',
        figure={
            'data': [
                go.Scatterpolar(
                    r = stats[i],
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
                    r = statsfact[i],
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