from dash import html, dcc, dash_table
from math import floor, ceil
from adsorbase.utils import load_df, axis_options
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

df = load_df()

color_mode_switch = html.Span([
    dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
    dbc.Switch(
        id="color-mode-switch",
        value=False,
        className="d-inline-block ms-1",
        persistence=True
    ),
    dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
])

theme_switch = html.Div([
    ThemeSwitchAIO(
        aio_id="theme",
        themes=[dbc.themes.COSMO, dbc.themes.DARKLY]
    )],
    style={"position": "absolute", "top": "20px", 'right': "20px"}
)

title = html.H1(
    children='Adsorbase',
    id='title',
    style={
        'textAlign': 'center',
        'fontSize': '4em',
        'letterSpacing': '3px',
        'marginTop': '5px'
    }
)

subtitle = html.H3(
    children='Your reliable adsorbent database',
    id='subtitle',
    style={
        'textAlign': 'center',
        'fontSize': '1.8em',
        'fontStyle': 'italic',
        'letterSpacing': '1px'
    }
)

x_dropdown = html.Div([
    dcc.Dropdown(
        {col: col for col in axis_options},
        'Pore volume [cm³/g]',
        id='xaxis-column',
        style={'color': 'black'}
    ),
], id='xaxis-container', style={'width': '48%', 'display': 'inline-block'}
)

y_dropdown = html.Div([
    dcc.Dropdown(
        {col: col for col in axis_options},
        'BET Surface Area [m²/g]',
        id='yaxis-column',
        style={'color': 'black'}
    ),
], id='yaxis-container', style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
)

temp_slider_text = html.Label('Select the right temperature conditions [K]')
temp_slider = dcc.RangeSlider(
    floor(df['Conditions T [K]'].min()/10)*10,
    ceil(df['Conditions T [K]'].max()/10)*10,
    step=None,
    updatemode='drag',
    tooltip={'placement': 'bottom', 'always_visible': True},
    allowCross=False,
    id='Temp-slider'
)

pressure_slider_text = html.Label('Select the right pressure conditions [bar]')
pressure_slider = dcc.RangeSlider(
    floor(df['Conditions P [bar]'].min()),
    ceil(df['Conditions P [bar]'].max()),
    step=None,
    updatemode='drag',
    tooltip={'placement': 'bottom', 'always_visible': True},
    allowCross=False,
    id='Pressure-slider'
)

hover_dropdown = html.Div([
    html.Label('Select hover data:'),
    dcc.Dropdown(
        id='hover-dropdown',
        options=[{'label': col, 'value': col} for col in axis_options],
        value=[],
        multi=True,
        style={
            'width': '100%',         
            'color': 'black',
            'justify-content': 'center',
            'marginLeft' : '5px'          
        }
    )
], style={
    'width': '60%',                 
    'display': 'inline-block'       
})

graph = dcc.Graph(id='indicator-graphic')
shown_count = html.Div(
    id='selected-number',
    style={'marginBottom': '20px', 'fontWeight': 'bold'}
)

input_title = html.H3('Extending the database')
input_prompt = html.P('Note: use periods as decimal separators, not commas')
input_fields = [
    dcc.Input(id='input-name', type='text', placeholder='Name'),
    dcc.Input(id='input-type', type='text', placeholder='Type of adsorbent'),
    dcc.Input(id='input-BET', type='number', placeholder='BET Surface Area'),
    dcc.Input(id='input-Pore', type='number',
              placeholder='Pore volume [cm³/g]'),
    dcc.Input(id='input-Ads', type='number',
              placeholder='Adsorption capacity'),
    dcc.Input(id='input-T', type='number', placeholder='Conditions T [K]'),
    dcc.Input(id='input-P', type='number', placeholder='Conditions P [bar]')
]

add_button = dbc.Button(
    'Add',
    id='submit-btn',
    n_clicks=0,
    style={'marginLeft': '10px'}
)

actualize_button = dbc.Button(
    'Actualize graph',
    id='actualize-btn',
    n_clicks=0,
    style={'marginLeft': '10px'}
)

add_output = html.Div(id='output', style={'color': 'green'})

filtered_table_title = html.H3(
    'Filtered Adsorbents Table',
    style={'textAlign': 'center'}
)

filtered_table = dcc.Loading(
    id='loading-table',
    type='default',
    children=dash_table.DataTable(
        id='adsorbents-table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'minWidth': '100px',
            'maxWidth': '200px',
            'whiteSpace': 'normal',
        },
        style_header={
            'backgroundColor': 'rgb(255, 255, 255)',
            'fontWeight': 'bold',
            'color': 'black'
        },
        style_data={
            'backgroundColor': 'rgb(255, 255, 255)',
            'color': 'black'
        },
        page_size=10
    )
)

export_button = dbc.Button(
    'Export Filtered Data',
    id='export-btn',
    n_clicks=0,
    style={'marginTop': '20px'}
)

download = dcc.Download(id='download-dataframe-csv')


full_layout = html.Div([
    title,
    subtitle,
    theme_switch,

    html.Div([
        x_dropdown,
        y_dropdown
    ]),

    html.Div([
        temp_slider_text,
        temp_slider,
        pressure_slider_text,
        pressure_slider
    ]),

    hover_dropdown,
    graph,
    shown_count,
    input_title,
    input_prompt,
    *input_fields,

    add_button,
    actualize_button,
    add_output,

    html.Hr(),

    filtered_table_title,
    filtered_table,
    export_button,
    download
], id='main-div')
