#Necessary imports 
from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.express as px
from pathlib import Path
from dash.exceptions import PreventUpdate
import pandas as pd
import math
import os


#Importing the csv file
cwd = Path.cwd()
csv_file = cwd / 'adsorbents.csv'
df = pd.read_csv(csv_file, sep=',')
custom_path = cwd/ 'custom.csv'
data_options = list(df.head(1))[2:]


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

#Initializing the app
app = Dash(__name__)

#Appearance of the app
app.layout = html.Div([
    # Store to keep dark mode state
    dcc.Store(id='dark-mode-store', data=False),

    html.H1(
        children='Adsorbase',
        id='title',
        style={
            'textAlign': 'center',
            'fontSize': '4em',
            'color': 'black',
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
                'Pore volume [cm³/g]',
                id='xaxis-column',
                style=dropdown_light_style
            ),
        ], id='xaxis-container', style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df.columns[2:5].unique(),
                'BET Surface Area [m²/g]',
                id='yaxis-column',
                style=dropdown_light_style
            ),
        ], id='yaxis-container', style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Label("Select the right temperature conditions [K]"),
        dcc.RangeSlider(
            math.floor(df['Conditions T [K]'].min()/10)*10,
            math.ceil(df['Conditions T [K]'].max()/10)*10,
            step=None,
            updatemode='drag',
            tooltip={"placement": "bottom", "always_visible": True},
            allowCross=False,
            id='Temp-slider'
        ),

        html.Label("Select the right pressure conditions [bar]"),
        dcc.RangeSlider(
            math.floor(df['Conditions P [bar]'].min()),
            math.ceil(df['Conditions P [bar]'].max()),
            step=None,
            updatemode='drag',
            tooltip={"placement": "bottom", "always_visible": True},
            allowCross=False,
            id='Pressure-slider'
        )
    ]),

    html.Div([
        html.Label('Select hover data:'),
        dcc.Dropdown(
            id='hover-dropdown',
            options=[{'label': col, 'value': col}
                     for col in data_options],
            value=[],
            multi=True,
            style={'color': 'black'}
        ),
    ]),
  
    dcc.Graph(id='indicator-graphic'),
    html.Div(id="selected-number", style={"marginBottom": "20px", "fontWeight": "bold"}),
    
    html.H3("Adding adsorbent"),
    html.P("Please write the name and the type of adsorbent in letter, and the rest in number with a point for the decimal."),
    dcc.Input(id='input-name', type='text', placeholder='Name'),
    dcc.Input(id='input-type', type='text', placeholder='Type of adsorbent'),
    dcc.Input(id='input-BET', type='number', placeholder='BET Surface Area'),
    dcc.Input(id='input-Pore', type='number', placeholder='Pore volume [cm³/g]'),
    dcc.Input(id='input-Ads', type='number',
              placeholder='Adsorption capacity'),
    dcc.Input(id='input-T', type='number', placeholder='Conditions T [K]'),
    dcc.Input(id='input-P', type='number', placeholder='Conditions P [bar]'),
    html.Button('Add', id='submit-btn', n_clicks=0,
                style={'marginLeft': '10px'}),
    html.Button('Actualize graph', id='actualize-btn', n_clicks=0,
                style={'marginLeft': '10px'}),
    html.Div(id='output', style={'color': 'green'}),
    
    html.Hr(),
    html.H3("Filtered Adsorbents Table", style={'textAlign': 'center'}),
    dcc.Loading(
        id="loading-table",
        type="default",
        children=dash_table.DataTable(
            id='adsorbents-table',
            columns=[{"name": col, "id": col} for col in df.columns],
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
),
    html.Button("Export Filtered Data", id="export-btn", n_clicks=0, style={'marginTop': '20px'}),
    dcc.Download(id="download-dataframe-csv")
], id='main-div', style=light_style)


# Function set to count the number of element on the graph
app.clientside_callback(
    """
    function(restyleData, relayoutData, figure) {
    if (!figure || !figure.data) return "N/A";

    // Set the limit of the zoom
    let xRange = null;
    let yRange = null;

    if (relayoutData) {
        if ('xaxis.range[0]' in relayoutData && 'xaxis.range[1]' in relayoutData) {
            xRange = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']];
        } else if ('xaxis.range' in relayoutData) {
            xRange = relayoutData['xaxis.range'];
        }
        if ('yaxis.range[0]' in relayoutData && 'yaxis.range[1]' in relayoutData) {
            yRange = [relayoutData['yaxis.range[0]'], relayoutData['yaxis.range[1]']];
        } else if ('yaxis.range' in relayoutData) {
            yRange = relayoutData['yaxis.range'];
        }
    }

    // Redefine the actual range before counting
    if ((!xRange || !yRange) && figure.layout) {
        if (!xRange && figure.layout.xaxis && figure.layout.xaxis.range) {
            xRange = figure.layout.xaxis.range;
        }
        if (!yRange && figure.layout.yaxis && figure.layout.yaxis.range) {
            yRange = figure.layout.yaxis.range;
        }
    }

    let totalElements = 0;

    for (let i = 0; i < figure.data.length; i++) {
        let trace = figure.data[i];
        let visible = trace.visible === undefined || trace.visible === true;
        if (!visible || !trace.x || !trace.y) continue;

        for (let j = 0; j < trace.x.length; j++) {
            let x = trace.x[j];
            let y = trace.y[j];
            let inX = !xRange || (x >= xRange[0] && x <= xRange[1]);
            let inY = !yRange || (y >= yRange[0] && y <= yRange[1]);

            if (inX && inY) {
                totalElements += 1;
            }
        }
    }

    return "Selected points : " + totalElements;
    }   
    """,
    Output("selected-number", "children"),
    [Input("indicator-graphic", "restyleData"), Input("indicator-graphic", "relayoutData"), Input("indicator-graphic", "figure"),
     Input("Temp-slider", "value"), Input("Pressure-slider", "value")]
)


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


column_titles = list(df.head(1))

def current_data()->pd.DataFrame:
    if os.path.exists(custom_path):
        df = pd.read_csv(custom_path)
    else:
        df = pd.read_csv(csv_file)
    return df

# Callback to update graph

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('hover-dropdown', 'value'),
    Input('dark-mode-store', 'data'),
    Input('Temp-slider', 'value'),
    Input('Pressure-slider', 'value'),
    Input('actualize-btn', 'n_clicks')
)
def update_graph(xaxis_column_name, yaxis_column_name, selected_hover_data, is_dark_mode, t_range, p_range, n_clicks):
    if not xaxis_column_name or not yaxis_column_name:
        raise PreventUpdate


    filtered_df = current_data()
    if t_range:
        filtered_df = filtered_df[
            (t_range[0] <= filtered_df['Conditions T [K]']) &
            (filtered_df['Conditions T [K]'] <= t_range[1])
        ]
    if p_range:
        filtered_df = filtered_df[
            (p_range[0] <= filtered_df['Conditions P [bar]']) & 
            (filtered_df['Conditions P [bar]'] <= p_range[1])
        ]

    # figure
    fig = px.scatter(
        filtered_df,
        x=xaxis_column_name,
        y=yaxis_column_name,
        # labels={xaxis_column_name: units[xaxis_column_name],
        #         yaxis_column_name: units[yaxis_column_name]},
        color=filtered_df.columns[1],
        symbol="Type of Adsorbent",
        hover_name=filtered_df.columns[0],
        title=f'{yaxis_column_name} as a function of {xaxis_column_name}',
        custom_data=list(df.head(1)),
        template='seaborn'
    )

    fig.update_layout(
        hoverlabel=dict(font_size=16, font_family='Arial'),
        xaxis_autorange=True,  # to rerange the axis after changing the sliders
        yaxis_autorange=True
    )

    additional_hover = ""
    if selected_hover_data:
        for data_name in selected_hover_data:

            index = column_titles.index(data_name)
            additional_hover += f"{data_name}" + \
                f" : %{{customdata[{index}]:.2f}} <br>"

    fig.update_traces(
        hovertemplate = ("<b>%{customdata[0]}</b><br>" + 
        "<i>%{customdata[1]}</i><br><br>" +

        f"{xaxis_column_name}" + " : %{x:.2f} <br>" +
        f"{yaxis_column_name}" + " : %{y:.2f} <br>" +
        additional_hover + "<extra></extra>"),
        mode='markers',
        marker={'sizemode': 'area',
                'sizeref': 10,
                'size': 8}
    )

    if is_dark_mode:
        fig.update_layout(
            transition_duration=1000,
            paper_bgcolor='#2a2a2a',
            plot_bgcolor='#2a2a2a',
            font_color='white',
            title_font_color='white',
            xaxis=dict(gridcolor='#444', color='white'),
            yaxis=dict(gridcolor='#444', color='white')
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
        'fontSize': '4em',
        'color': 'white' if is_dark_mode else 'black',
        'letterSpacing': '3px',
        'marginTop': '5px'
    }
    subtitle_style = {
        'textAlign': 'center',
        'fontSize': '1.8em',
        'fontStyle': 'italic',
        'color': 'white' if is_dark_mode else '#444',
        'letterSpacing': '1px'
    }
    return style, title_style, subtitle_style

#Callback to connect the table to the filters 
@app.callback(
    Output('adsorbents-table', 'data'),
    Input('Temp-slider', 'value'),
    Input('Pressure-slider', 'value')
)
def update_table(t_range, p_range):
    if (t_range is None) or (p_range is None):
        raise PreventUpdate

    filtered_df = df[
        (df['Conditions T [K]'] >= t_range[0]) & (df['Conditions T [K]'] <= t_range[1]) &
        (df['Conditions P [bar]'] >= p_range[0]) & (df['Conditions P [bar]'] <= p_range[1])
    ]

    return filtered_df.to_dict('records')

def insert_into_csv(name, type, BET, Pore, Ads, T, P):
    new_data = pd.DataFrame(
        [[name, type, BET, Pore, Ads, T, P]],
        columns=list(df.head(1))
    )

    updated = pd.concat([current_data(), new_data], ignore_index=True)
    updated.to_csv(custom_path, index=False)

@app.callback(
    Output('output', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('input-name', 'value'),
    State('input-type', 'value'),
    State('input-BET', 'value'),
    State('input-Pore', 'value'),
    State('input-Ads', 'value'),
    State('input-T', 'value'),
    State('input-P', 'value'),
)
def update_output(n_clicks, name, type, BET, Pore, Ads, T, P):
    if n_clicks > 0:
        if None in (name, type, BET, Pore, Ads, T, P):
            return html.Span("Error : Please complete each data.", style={'color': 'red'})
        else:
            insert_into_csv(name, type, BET, Pore, Ads, T, P),
            return f"Added : {name}, {type}, {BET}, {Pore}, {Ads}, {T}, {P}"

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-btn", "n_clicks"),
    State("xaxis-column", "value"),
    State("yaxis-column", "value"),
    State("Temp-slider", "value"),
    State("Pressure-slider", "value"),
    prevent_initial_call=True
)
def export_filtered_data(n_clicks, x_col, y_col, t_range, p_range):
    dff = current_data()

    if t_range:
        dff = dff[(dff['Conditions T'] >= t_range[0]) & (dff['Conditions T'] <= t_range[1])]
    if p_range:
        dff = dff[(dff['Conditions P'] >= p_range[0]) & (dff['Conditions P'] <= p_range[1])]

    return dcc.send_data_frame(dff.to_csv, filename="filtered_data.csv", index=False)

if __name__ == '__main__':
    app.run(debug=True)
