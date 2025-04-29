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
                df.columns[2:5].unique(),
                'BET Surface Area',
                id='xaxis-column'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df.columns[2:5].unique(),
                'Pore volume',
                id='yaxis-column'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    dcc.Graph(id='indicator-graphic'),
    html.Div([
    dcc.Slider(id='value-slider')
    ], style={'width': '95%', 'padding': '20px'})
])


@callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value')
)

def update_graph(xaxis_column_name, yaxis_column_name):
    fig = px.scatter(
        df,
        x=xaxis_column_name,
        y=yaxis_column_name,
        color=df.columns[1],         # Color based on second column
        hover_name=df.columns[0],    # Hover label from the first column (optional)
        title=f'{yaxis_column_name} vs {xaxis_column_name}',
        hover_data=["Conditions T", "Conditions P"]
    )
    fig.update_layout(transition_duration=500)
    return fig



if __name__ == '__main__':
    app.run(debug=True)