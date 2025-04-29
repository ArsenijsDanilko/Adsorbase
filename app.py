from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
from pathlib import Path

import pandas as pd

app = Dash()

cwd = Path.cwd()
csv_file = cwd / "adsorbents.csv"
df = pd.read_csv(csv_file, sep=",")

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                df.columns[2:6].unique(),
                'BET Surface Area',
                id='xaxis-column'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df.columns[2:6].unique(),
                'Pore volume',
                id='yaxis-column'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    dcc.Graph(id='indicator-graphic')
])


@callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
)

def update_graph(x,y):
    fig = px.scatter(x = 'xaxis-column',
                     y = 'yaxis-column')
    return fig

if __name__ == '__main__':
    app.run(debug=True)