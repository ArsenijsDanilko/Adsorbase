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
    # Function set to count the number of element on the graph
    javascript_count = """
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
        """
    
    app.clientside_callback(
        javascript_count,
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

