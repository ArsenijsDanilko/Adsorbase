from dash import Dash, Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate
import adsorbase.utils as utils
import pandas as pd
import os
import plotly.express as px
from dash_bootstrap_templates import ThemeSwitchAIO, load_figure_template


csv_file = utils.ROOT_PATH / 'data/adsorbents.csv'
df = utils.load_df()
custom_path = utils.ROOT_PATH / 'data/custom.csv'
data_options = utils.column_titles[2:]

load_figure_template(["cosmo", "darkly"])


def register_callbacks(app: Dash) -> None:
    
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


    def current_data() -> pd.DataFrame:
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
        Input('Temp-slider', 'value'),
        Input('Pressure-slider', 'value'),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input('actualize-btn', 'n_clicks')
    )
    def update_graph(xaxis_column_name, yaxis_column_name, selected_hover_data, t_range, p_range, theme, n_clicks):
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

        # Choose Plotly template based on theme
        plot_template = "cosmo" if theme else "darkly"

        # Plot the figure
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
            template=plot_template
        )

        fig.update_layout(
            hoverlabel=dict(font_size=16, font_family='Arial'),
            xaxis_autorange=True,  # to rerange the axis after changing the sliders
            yaxis_autorange=True
        )

        additional_hover = ""
        if selected_hover_data:
            for data_name in selected_hover_data:

                index = utils.column_titles.index(data_name)
                additional_hover += f"{data_name}" + \
                    f" : %{{customdata[{index}]:.2f}} <br>"

        fig.update_traces(
            hovertemplate=("<b>%{customdata[0]}</b><br>" +
                        "<i>%{customdata[1]}</i><br><br>" +

                        f"{xaxis_column_name}" + " : %{x:.2f} <br>" +
                        f"{yaxis_column_name}" + " : %{y:.2f} <br>" +
                        additional_hover + "<extra></extra>"),
            mode='markers',
            marker={'sizemode': 'area',
                    'sizeref': 10,
                    'size': 8}
        )
        
        return fig 

    
    @app.callback(
        Output('point-count', 'children'),
        Input('indicator-graphic', 'relayoutData'),
        Input('indicator-graphic', 'restyleData'),
        Input('indicator-graphic', 'figure'),
        Input("Temp-slider","value"),
        Input("Pressure-slider","value"),
    )
    def count_visible_points(relayout_data, restyle_data, figure, TempSlider, PressSlider):
        visible_traces = []

        # Identify the visible traces 
        if restyle_data and 'visible' in str(restyle_data):
            for i, trace in enumerate(figure['data']):
                if trace.get('visible', True) not in [False, 'legendonly']:
                    visible_traces.append(i)
        else:
            # All the visible trace by default 
            visible_traces = list(range(len(figure['data'])))

        # Extract the limits of the zoom
        x0 = y0 = x1 = y1 = None
        if relayout_data and 'xaxis.range[0]' in relayout_data:
            x0 = relayout_data['xaxis.range[0]']
            x1 = relayout_data['xaxis.range[1]']
            y0 = relayout_data['yaxis.range[0]']
            y1 = relayout_data['yaxis.range[1]']

        # Set the limits if not zooming
        if x0 is None : 
            x0 = -float('inf')
        if y0 is None : 
            y0 = -float('inf')
        if x1 is None : 
            x1 = float('inf')
        if y1 is None : 
            y1 = float('inf')

        # Count the visible traces on the graph
        count = 0
        for i in visible_traces:
            x_points = []
            y_points = []
        
            trace = figure['data'][i]

            x_vals = trace['x'].get('_inputArray')
            if x_vals : 
                for k,v in x_vals.items() : 
                    if k.isdigit() : 
                        x_points.append(v)
                    
            y_vals = trace['y'].get('_inputArray')
            if y_vals :
                for k,v in y_vals.items() : 
                    if k.isdigit():
                        y_points.append(v)

            for x, y in zip(x_points, y_points):
                if x0 and x1 and y0 and y1 and x and y:
                    if (x0 <= x <= x1) and (y0 <= y <= y1):
                        count += 1

        return f"Number of visible points : {count}"


    # Callback to connect the table to the filters
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
            (df['Conditions P [bar]'] >= p_range[0]) & (
                df['Conditions P [bar]'] <= p_range[1])
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
            dff = dff[(dff['Conditions T [K]'] >= t_range[0]) &
                    (dff['Conditions T [K]'] <= t_range[1])]
        if p_range:
            dff = dff[(dff['Conditions P [bar]'] >= p_range[0]) &
                    (dff['Conditions P [bar]'] <= p_range[1])]

        return dcc.send_data_frame(dff.to_csv, filename="filtered_data.csv", index=False)

