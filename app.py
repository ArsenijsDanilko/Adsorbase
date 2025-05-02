from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
from pathlib import Path
from dash.exceptions import PreventUpdate
import pandas as pd

cwd = Path.cwd()
csv_file = cwd / 'adsorbents.csv'
df = pd.read_csv(csv_file, sep=',')
data_options = list(df.head(1))[2:]

# Unit Dicts
units = {'BET Surface Area': 'BET Surface Area [m<sup>2</sup>/g]',
         'Pore volume': 'Pore volume [cm<sup>3</sup>/g]',
         'Adsorption capacity': 'Adsorption capacity [mmol/g]',
         'Conditions T': 'Conditions T [K]',
         'Conditions P': 'Conditions P [bar]'}

# Default styles
light_style = {
    'backgroundColor': 'white',
    'color': 'black',
    'transition': 'background-color 1.3s ease, color 1.3s ease'
}

dark_style = {
    'backgroundColor': '#2a2a2a',
    'color': 'white',
    'transition': 'background-color 1.3s ease, color 1.3s ease'
}

dropdown_light_style = {
    'backgroundColor': 'white',
    'color': 'black'
}

dropdown_dark_style = {
    'backgroundColor': 'white',
    'color': 'black'
}

app = Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Adsorbase</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap" rel="stylesheet">
        <style>
    .glow-title {
        color: #bf3b32;
        text-shadow: 6px 6px 8px rgba(0, 255, 255, 0.2);
        transition: text-shadow 0.3s ease-in-out;
    }
    @keyframes pulseGlow {
        0% {
            text-shadow: 0 0 3px #0ff, 0 0 5px #0ff, 0 0 8px #bf3b32;
        }
        50% {
            text-shadow: 0 0 6px #0ff, 0 0 10px #0ff, 0 0 20px #bf3b32;
        }
        100% {
            text-shadow: 0 0 3px #0ff, 0 0 5px #0ff, 0 0 8px #bf3b32;
        }
    }

    .glow-title:hover {
        animation: pulseGlow 1.5s infinite;
        cursor: pointer;
    }
</style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    # Store to keep dark mode state
    dcc.Store(id='dark-mode-store', data=False),

    html.H1(
        children='Adsorbase',
        id='title',
        className='glow-title',
        style={
            'textAlign': 'center',
            'fontSize': '4em',
            'color': '#bf3b32',
            'fontFamily': "'Orbitron', sans-serif",
            'textShadow': '6px 6px 10px rgba(0,255,255,0.2)',
            'letterSpacing': '3px',
            'marginTop': '5px'
        }),
    html.H3(
        children='Your reliable adsorbent database',
        id='subtitle',
        style={
            'textAlign': 'center',
            'fontSize': '1.8em',
            'fontStyle': 'italic',
            'color': '#444',
            'letterSpacing': '1px'
        }),
    html.Button('Activate Dark mode', id='toggle-darkmode'),

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
    html.Div([
        html.Label("Select the right temperature conditions in Kelvin"),
        dcc.RangeSlider(
            df['Conditions T'].min(),
            df['Conditions T'].max(),
            step=None,
            updatemode='drag',
            tooltip={"placement": "bottom", "always_visible": True},
            allowCross=False,
            id='Temp-slider'
        ),
        html.Label("Select the right pressure conditions in bar"),
        dcc.RangeSlider(
            df['Conditions P'].min(),
            df['Conditions P'].max(),
            step=None,
            updatemode='drag',
            tooltip={"placement": "bottom", "always_visible": True},
            allowCross=False,
            id='Pressure-slider'
        )
    ]),
    dcc.Graph(id='indicator-graphic'),
    html.Div([
        html.Label('Select hover data:'),
        dcc.Dropdown(
            id='hover-dropdown',
            options=[{'label': col, 'value': col}
                     for col in data_options],
            value=[],
            multi=True,
        ),
    ]),
], id='main-div', style=light_style)


# Callback to update hover dropdown options
@app.callback(
    Output('hover-dropdown', 'options'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value')
)
def update_hover_dropdown(x_axis, y_axis):
    hover_candidates = [
        col for col in data_options if col not in (x_axis, y_axis)]

    return [{'label': col, 'value': col} for col in hover_candidates]

# Callback to update graph
data_index = ('Name', 'Type of Adsorbent', 'BET Surface Area',
              'Pore volume', 'Adsorption capacity', 'Conditions T', 'Conditions P')

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('hover-dropdown', 'value'),
    Input('dark-mode-store', 'data'),
    Input('Temp-slider', 'value'),
    Input('Pressure-slider', 'value')
)
def update_graph(xaxis_column_name, yaxis_column_name, selected_hover_data, is_dark_mode, t_range, p_range):
    if not xaxis_column_name or not yaxis_column_name:
        raise PreventUpdate
    
    filtered_df = df
    if (t_range is not None) and (p_range is not None):
        filtered_df = df[(t_range[0] <= df['Conditions T']) & (df['Conditions T'] <= t_range[1])]
        filtered_df = filtered_df[(p_range[0] <= filtered_df['Conditions P']) & (filtered_df['Conditions P'] <= p_range[1])]
    
    fig = px.scatter(
        filtered_df,
        x=xaxis_column_name,
        y=yaxis_column_name,
        color=df.columns[1],
        hover_name=df.columns[0],
        title=f'{yaxis_column_name} as a function of {xaxis_column_name}',
        custom_data=['Name', 'Type of Adsorbent', 'BET Surface Area',
                     'Pore volume', 'Adsorption capacity', 'Conditions T', 'Conditions P'],
        template='seaborn'
    )

    # Style of the hover cells
    fig.update_layout(
        hoverlabel=dict(
            font_size=16,
            font_family='Arial' 
        )
    )

    additional_hover = ""
    if selected_hover_data:
        for data_name in selected_hover_data:
            index = data_index.index(data_name)
            additional_hover += f"{units[data_name]}" + \
                f" : %{{customdata[{index}]:.2f}} <br>"

    # Format of the hover cells
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]} </b><br>" +
        "<i>%{customdata[1]}</i><br><br>" +
        f"{units[xaxis_column_name]}" + " : %{x:.2f} <br>" +
        f"{units[yaxis_column_name]}" + " : %{y:.2f} <br>" +
        additional_hover +
        "<extra></extra>",

        mode='markers',

        marker={'sizemode': 'area',
                'sizeref': 10},
    )

    if is_dark_mode:
        fig.update_layout(
            transition_duration=1000,
            paper_bgcolor='#2a2a2a',    # Graph area background
            plot_bgcolor='#2a2a2a',     # Plot area background
            font_color='white',         # Text color
            title_font_color='white',
            xaxis=dict(
                gridcolor='#444',       # Grid line color
                color='white'           # Axis label color
            ),
            yaxis=dict(
                gridcolor='#444',
                color='white'
            ),
        )

    fig.update_layout(transition_duration=500)
    return fig


# Callback to toggle dark mode
@app.callback(
    Output('dark-mode-store', 'data'),
    Input('toggle-darkmode', 'n_clicks'),
    State('dark-mode-store', 'data')
)
def toggle_dark_mode(n_clicks, current_state):
    if n_clicks is None:
        raise PreventUpdate
    return not current_state  # Toggle boolean


@app.callback(
    Output('xaxis-column', 'style'),
    Output('yaxis-column', 'style'),
    Input('dark-mode-store', 'data')
)
def update_dropdown_styles(is_dark_mode):
    return (dropdown_dark_style if is_dark_mode else dropdown_light_style,
            dropdown_dark_style if is_dark_mode else dropdown_light_style)

@app.callback(
    Output('toggle-darkmode', 'children'),
    Input('dark-mode-store', 'data')
)
def update_toggle_label(is_dark_mode):
    return 'Activate Light Mode' if is_dark_mode else 'Activate Dark Mode'

# Callback to update styles
@app.callback(
    Output('main-div', 'style'),
    Output('title', 'style'),
    Output('subtitle', 'style'),
    Input('dark-mode-store', 'data')
)
def update_styles(is_dark_mode):
    style = dark_style if is_dark_mode else light_style
    # Title remains styled regardless of theme
    title_style = {
        'textAlign': 'center',
        'fontFamily': "'Orbitron', sans-serif",
        'fontSize': '4em',
        'color': '#bf3b32',
        'letterSpacing': '3px',
        'marginTop': '5px'
        # No textShadow here
    }
    subtitle_style = {
        'textAlign': 'center',
        'fontSize': '1.8em',
        'fontStyle': 'italic',
        'color': 'white' if is_dark_mode else '#444',
        'letterSpacing': '1px'
    }
    return style, title_style, subtitle_style


if __name__ == '__main__':
    app.run(debug=True)

   

