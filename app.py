from dash import Dash, dcc, html, Input, Output, State, callback, ctx
import plotly.express as px
from pathlib import Path
from dash.exceptions import PreventUpdate
import pandas as pd

app = Dash()

cwd = Path.cwd()
csv_file = cwd / "adsorbents.csv"
df = pd.read_csv(csv_file, sep=",")

# Default styles
light_style = {
    'backgroundColor': 'white',
    'color': 'black'
}

dark_style = {
    'backgroundColor': '#1e1e1e',
    'color': 'white'
}

dropdown_light_style = {
    'backgroundColor': 'white',
    'color': 'black'
}

dropdown_dark_style = {
    'backgroundColor': 'white',
    'color': 'black'
}

app.layout = html.Div([
    # Store to keep dark mode state
    dcc.Store(id='dark-mode-store', data=False),

    html.H1(
        children='Adsorbase',
        id='title',
        style={'textAlign': 'center'}
    ),
    html.H3(
        children='Your reliable adsorbent database',
        id='subtitle',
        style={'textAlign': 'center'}
    ),
    html.Button('Activate Dark mode', id='toggle-darkmode', n_clicks=0),

    html.Div([
        html.Div([
            dcc.Dropdown(
                df.columns[2:5].unique(),
                'Pore volume',
                id='xaxis-column',
                style=dropdown_light_style
            ),
        ], id='xaxis-container', style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df.columns[2:5].unique(),
                'BET Surface Area',
                id='yaxis-column',
                style=dropdown_light_style
            ),
        ], id='yaxis-container', style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    dcc.Graph(id='indicator-graphic'),
], id='main-div', style=light_style)


# Callback to update graph
@callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('dark-mode-store', 'data')
)
def update_graph(xaxis_column_name, yaxis_column_name, is_dark_mode):
    if not xaxis_column_name or not yaxis_column_name:
        raise PreventUpdate

    fig = px.scatter(
        df,
        x=xaxis_column_name,
        y=yaxis_column_name,
        color=df.columns[1],
        hover_name=df.columns[0],
        title=f'{yaxis_column_name} as a function of {xaxis_column_name}',
        hover_data=["Conditions T", "Conditions P"],
        template='plotly_white'
    )

    if is_dark_mode:
        fig.update_layout(
            paper_bgcolor="#2a2a2a",    # Graph area background
            plot_bgcolor="#2a2a2a",     # Plot area background
            font_color="white",         # Text color
            title_font_color="white",
            xaxis=dict(
                gridcolor="#444",       # Grid line color
                color="white"           # Axis label color
            ),
            yaxis=dict(
                gridcolor="#444",
                color="white"
            ),
        )
    else:
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="black",
            title_font_color="black",
            xaxis=dict(
                gridcolor="#ccc",
                color="black"
            ),
            yaxis=dict(
                gridcolor="#ccc",
                color="black"
            ),
        )

    fig.update_layout(transition_duration=500)
    return fig


# Callback to toggle dark mode
@callback(
    Output('dark-mode-store', 'data'),
    Input('toggle-darkmode', 'n_clicks'),
    State('dark-mode-store', 'data')
)
def toggle_dark_mode(n_clicks, current_state):
    if n_clicks is None:
        raise PreventUpdate
    return not current_state  # Toggle boolean


@callback(
    Output('xaxis-column', 'style'),
    Output('yaxis-column', 'style'),
    Input('dark-mode-store', 'data')
)
def update_dropdown_styles(is_dark_mode):
    return (dropdown_dark_style if is_dark_mode else dropdown_light_style,
            dropdown_dark_style if is_dark_mode else dropdown_light_style)

# Callback to update styles


@callback(
    Output('main-div', 'style'),
    Output('title', 'style'),
    Output('subtitle', 'style'),
    Input('dark-mode-store', 'data')
)
def update_styles(is_dark_mode):
    style = dark_style if is_dark_mode else light_style
    center_text = {'textAlign': 'center'}
    return style, {**style, **center_text}, {**style, **center_text}


if __name__ == '__main__':
    app.run(debug=True)
