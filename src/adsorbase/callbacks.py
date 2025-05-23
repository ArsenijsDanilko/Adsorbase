from dash import Dash, Input, Output, State, html, dcc, dash_table
from dash.exceptions import PreventUpdate
import adsorbase.utils as utils
from numpy import floor, ceil
import plotly.express as px
from dash_bootstrap_templates import ThemeSwitchAIO, load_figure_template
from typing import Any

df = utils.load_df()
data_options = utils.column_titles[2:]

load_figure_template(['cosmo', 'darkly'])


def register_callbacks(app: Dash) -> None:

    @app.callback(
        Output('Temp-slider', 'min'),
        Output('Temp-slider', 'max'),
        Output('Pressure-slider', 'min'),
        Output('Pressure-slider', 'max'),
        Input('actualize-btn', 'n_clicks')
    )
    def update_filter_range(n_clicks) -> tuple:
        t_min = floor(df['Conditions T [K]'].min()/10)*10
        t_max = ceil(df['Conditions T [K]'].max()/10)*10

        p_min = floor(df['Conditions P [bar]'].min()/10)*10
        p_max = ceil(df['Conditions P [bar]'].max()/10)*10

        if n_clicks:
            data = utils.current_data()
            try:
                t_min = floor(data['Conditions T [K]'].min()/10)*10
                t_max = ceil(data['Conditions T [K]'].max()/10)*10
                p_min = floor(data['Conditions P [bar]'].min()/10)*10
                p_max = ceil(data['Conditions P [bar]'].max()/10)*10
            except Exception as e:
                print('Error updating sliders:', e)

        return (t_min, t_max, p_min, p_max)

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
    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('xaxis-column', 'value'),
        Input('yaxis-column', 'value'),
        Input('hover-dropdown', 'value'),
        Input('Temp-slider', 'value'),
        Input('Pressure-slider', 'value'),
        Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
        Input('actualize-btn', 'n_clicks')
    )
    def update_graph(xaxis_column_name, yaxis_column_name, selected_hover_data, t_range, p_range, theme, n_clicks):
        if not xaxis_column_name or not yaxis_column_name:
            raise PreventUpdate

        filtered_df = utils.current_data()
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

        plot_template = 'bootstrap' if theme else 'darkly'

        fig = px.scatter(
            filtered_df,
            x=xaxis_column_name,
            y=yaxis_column_name,

            color=filtered_df.columns[1],
            symbol='Type of Adsorbent',
            hover_name=filtered_df.columns[0],
            title=f'{yaxis_column_name} as a function of {xaxis_column_name}',
            custom_data=list(filtered_df.head(1)),
            template=plot_template,
            color_discrete_sequence=px.colors.qualitative.Vivid
        )

        fig.update_layout(
            hoverlabel=dict(font_size=16, font_family='Arial'),
            xaxis_autorange=True,  # to rerange the axis after changing the sliders
            yaxis_autorange=True
        )

        additional_hover = ''
        if selected_hover_data:
            for data_name in selected_hover_data:

                index = utils.column_titles.index(data_name)
                additional_hover += f'{data_name}' + \
                    f' : %{{customdata[{index}]:.2f}} <br>'

        fig.update_traces(
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>' +
                '<i>%{customdata[1]}</i><br><br>' +
                f'{xaxis_column_name}' + ' : %{x:.2f} <br>' +
                f'{yaxis_column_name}' + ' : %{y:.2f} <br>' +
                additional_hover + '<extra></extra>'
            ),
            mode='markers',
            marker={'sizemode': 'area',
                    'sizeref': 10,
                    'size': 8}
        )

        return fig

    def get_traces(relayout_data, restyle_data, figure) -> tuple[list, float, float, float, float]:
        '''Get all series on the plotly scatter, as well as the zoom limits (`x_min`, `x_max`, `y_min`, `y_max`)'''
        visible_traces = []

        # Identify the visible traces
        if restyle_data and 'visible' in str(restyle_data):
            for i, trace in enumerate(figure['data']):
                if trace.get('visible', True) not in (False, 'legendonly'):
                    visible_traces.append(i)
        else:
            # All the visible trace by default
            visible_traces = list(range(len(figure['data'])))

        # Extract the limits of the zoom
        x_min = y_min = x_max = y_max = None
        if relayout_data and ('xaxis.range[0]' in relayout_data):
            x_min = relayout_data['xaxis.range[0]']
            x_max = relayout_data['xaxis.range[1]']
            y_min = relayout_data['yaxis.range[0]']
            y_max = relayout_data['yaxis.range[1]']

        # Set the limits if zoomed out
        if x_min is None:
            x_min = -float('inf')
        if y_min is None:
            y_min = -float('inf')
        if x_max is None:
            x_max = float('inf')
        if y_max is None:
            y_max = float('inf')

        return (visible_traces, x_min, x_max, y_min, y_max)

    # Callback to count the number of visible points on the graph
    @app.callback(
        Output('point-count', 'children'),
        Input('indicator-graphic', 'relayoutData'),
        Input('indicator-graphic', 'restyleData'),
        Input('indicator-graphic', 'figure'),
        Input('Temp-slider', 'value'),
        Input('Pressure-slider', 'value'),
    )
    def count_visible_points(relayout_data, restyle_data, figure, t_range, p_range) -> str:

        visible_traces, x_min, x_max, y_min, y_max = get_traces(
            relayout_data, restyle_data, figure)

        # Count the visible traces on the graph
        count = 0
        for i in visible_traces:
            x_points: list[float] = []
            y_points: list[float] = []

            trace: dict[str, dict | Any] = figure['data'][i]

            x_vals: dict[str, Any] = trace['x'].get('_inputArray', dict())
            if x_vals:
                for k, v in x_vals.items():
                    if k.isdigit():
                        x_points.append(v)

            y_vals: dict[str, Any] = trace['y'].get('_inputArray', dict())
            if y_vals:
                for k, v in y_vals.items():
                    if k.isdigit():
                        y_points.append(v)

            for x, y in zip(x_points, y_points):
                if None not in (x_min, x_min, y_max, y_max, x, y):
                    if (x_min <= x <= x_max) and (y_min <= y <= y_max):
                        count += 1

        return f'Number of visible points : {count}'


    # Callback to connect the table to the filters
    @app.callback(
        Output('adsorbents-table', 'children'),
        Input('indicator-graphic', 'relayoutData'),
        Input('indicator-graphic', 'restyleData'),
        Input('indicator-graphic', 'figure'),
        Input('Temp-slider', 'value'),
        Input('Pressure-slider', 'value'),
        Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
    )
    def update_table(relayout_data, restyle_data, figure, t_range, p_range, theme):

        visible_traces, x_min, x_max, y_min, y_max = get_traces(
            relayout_data, restyle_data, figure)

        # Extract to data
        column_names = df.head(1)
        filtered_data = []

        for i in visible_traces:
            x_points: list[float] = []
            y_points: list[float] = []

            trace: dict[str, dict | Any] = figure['data'][i]

            x_vals: dict[str, Any] = trace['x'].get('_inputArray')
            if x_vals:
                for k, v in x_vals.items():
                    if k.isdigit():
                        x_points.append(v)

            y_vals: dict[str, Any] = trace['y'].get('_inputArray')
            if y_vals:
                for k, v in y_vals.items():
                    if k.isdigit():
                        y_points.append(v)

            custom_data = trace.get('customdata', [])

            for x, y, custom in zip(x_points, y_points, custom_data):
                if None not in (x_min, x_max, y_min, y_max, x, y):
                    if (x_min <= x <= x_max) and (y_min <= y <= y_max):
                        row = dict(zip(column_names, custom))
                        filtered_data.append(row)

            dark = not theme

            children = dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in df.columns],
                data=filtered_data,
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': '#34495e' if dark else '#e1e5ec',
                    'color': 'white' if dark else 'black'
                },
                style_cell={
                    'backgroundColor': '#2b2b2b' if dark else 'white',
                    'color': 'white' if dark else 'black',
                    'textAlign': 'left',
                    'padding': '5px',
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#353535' if dark else '#f9f9f9'
                    }
                ],
                page_size=10
            )

        return children


    def check_inputs(name, ads_type, BET, Pore, Ads, T, P) -> tuple[bool, html.Span | None]:
        insert = False
        span = None
        if '' in (name, ads_type):
            span = html.Span(
                'Error : Please enter a name and type', style={'color': 'red'})

        if (BET, Pore, Ads).count(None) >= 2:
            span = html.Span('Error : Please enter at least two of the fields' +
                             "'BET surface area'," +
                             "'Pore Volume' and 'Adsorption capacity'",
                             style={'color': 'red'})
        else:
            insert = True
            span = html.Div(
                f'Added : {name}, {ads_type}, {BET}, {Pore}, {Ads}, {T}, {P}')

        return (insert, span)

    @app.callback(
        Output('output', 'children'),
        Input('submit-btn', 'n_clicks'),
        State('input-name', 'value'),
        State('input-type', 'value'),
        State('input-BET', 'value'),
        State('input-Pore', 'value'),
        State('input-Ads', 'value'),
        State('input-T', 'value'),
        State('input-P', 'value')
    )
    def update_output(n_clicks, name, ads_type, BET, Pore, Ads, T, P):

        if n_clicks:
            insert, span = check_inputs(name, ads_type, BET, Pore, Ads, T, P)

            if insert:
                utils.insert_into_csv(name, ads_type, BET, Pore, Ads, T, P)

            return span

    @app.callback(
        [
            Output('input-name', 'value'),
            Output('input-type', 'value'),
            Output('input-BET', 'value'),
            Output('input-Pore', 'value'),
            Output('input-Ads', 'value'),
            Output('input-T', 'value'),
            Output('input-P', 'value')
        ],
        Input('submit-btn', 'n_clicks')
    )
    def clear_fields(n_clicks):
        return ['', ''] + [None for i in range(5)]

    @app.callback(
        Output('download-dataframe-csv', 'data'),
        Input('export-btn', 'n_clicks'),
        State('xaxis-column', 'value'),
        State('yaxis-column', 'value'),
        State('Temp-slider', 'value'),
        State('Pressure-slider', 'value'),
        prevent_initial_call=True
    )
    def export_filtered_data(n_clicks, x_col, y_col, t_range, p_range):
        dff = utils.current_data()

        if t_range:
            dff = dff[(dff['Conditions T [K]'] >= t_range[0]) &
                      (dff['Conditions T [K]'] <= t_range[1])]
        if p_range:
            dff = dff[(dff['Conditions P [bar]'] >= p_range[0]) &
                      (dff['Conditions P [bar]'] <= p_range[1])]

        return dcc.send_data_frame(dff.to_csv, filename='filtered_data.csv', index=False)
