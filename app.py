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

app = Dash(__name__)
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
        html.Label("Select the right temperature conditions [K]"),
        dcc.RangeSlider(
            df['Conditions T'].min(),
            df['Conditions T'].max(),
            step=None,
            id='Temp-slider'
        ),
        html.Label("Select the right pressure conditions [bar]"),
        dcc.RangeSlider(
            df['Conditions P'].min(),
            df['Conditions P'].max(),
            step=None,
            id='Pressure-slider'
        )
    ]),
    dcc.Graph(id='indicator-graphic'),
    html.Div(id="info", style={"marginBottom": "20px", "fontWeight": "bold"}),
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

#Function set to count the number of element of the graph
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
    Output("info", "children"),
    [Input("indicator-graphic", "restyleData"), Input("indicator-graphic", "relayoutData"), Input("indicator-graphic", "figure"),
    Input("Temp-slider", "value"), Input("Pressure-slider", "value")]
)

# Callback to update hover dropdown options
@ app.callback(
    Output('hover-dropdown', 'options'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value')
)
def update_hover_dropdown(x_axis, y_axis):
    hover_candidates= [
        col for col in data_options if col not in (x_axis, y_axis)]

    return [{'label': col, 'value': col} for col in hover_candidates]

data_index= ('Name', 'Type of Adsorbent', 'BET Surface Area',
              'Pore volume', 'Adsorption capacity', 'Conditions T', 'Conditions P')

# Callback to update graph
@ app.callback(
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

    filtered_df= df
    if (t_range is not None) and (p_range is not None):
        filtered_df= df[(t_range[0] <= df['Conditions T']) &
                         (df['Conditions T'] <= t_range[1])]
        filtered_df= filtered_df[(p_range[0] <= filtered_df['Conditions P']) & (
            filtered_df['Conditions P'] <= p_range[1])]

    fig= px.scatter(
        filtered_df,
        x=xaxis_column_name,
        y=yaxis_column_name,
        labels={xaxis_column_name: units[xaxis_column_name],
                yaxis_column_name: units[yaxis_column_name]},
        color=df.columns[1],
        symbol="Type of Adsorbent",
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

    additional_hover= ""
    if selected_hover_data:
        for data_name in selected_hover_data:
            index= data_index.index(data_name)
            additional_hover += f"{units[data_name]}" + f" : %{{customdata[{index}]:.2f}} <br>"

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
                'sizeref': 10,
                'size': 8},
    )

    if is_dark_mode:
        fig.update_layout(
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
@ app.callback(
    Output('dark-mode-store', 'data'),
    Input('toggle-darkmode', 'n_clicks'),
    State('dark-mode-store', 'data')
)
def toggle_dark_mode(n_clicks, current_state):
    if n_clicks is None:
        raise PreventUpdate
    return not current_state  # Toggle boolean


@ app.callback(
    Output('xaxis-column', 'style'),
    Output('yaxis-column', 'style'),
    Input('dark-mode-store', 'data')
)
def update_dropdown_styles(is_dark_mode):
    return (dropdown_dark_style if is_dark_mode else dropdown_light_style,
            dropdown_dark_style if is_dark_mode else dropdown_light_style)


# Callback to update styles
@ app.callback(
    Output('main-div', 'style'),
    Output('title', 'style'),
    Output('subtitle', 'style'),
    Input('dark-mode-store', 'data')
)
def update_styles(is_dark_mode):
    style= dark_style if is_dark_mode else light_style
    center_text= {'textAlign': 'center'}
    return style, {**style, **center_text}, {**style, **center_text}


if __name__ == '__main__':
    app.run(debug=True)
