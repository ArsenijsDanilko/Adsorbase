from dash import Dash, dcc, html, Input, Output
import pandas as pd
from pathlib import Path
import plotly.express as px

cwd = Path.cwd()
df = pd.read_csv(cwd / "adsorbents.csv")
app = Dash(__name__)

data_options = [
    "Type of Adsorbent",
    "BET Surface Area",
    "Pore volume",
    "Adsorption capacity",
    "Conditions T",
    "Conditions P",
]

data_options = list(df.head(1))
app.layout = html.Div(
    [
        # Axis dropdowns in a horizontal row
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select x-axis:"),
                        dcc.Dropdown(
                            id="x-axis",
                            options=[
                                {"label": col, "value": col} for col in data_options
                            ],
                            value="Adsorption capacity",
                            multi=False,
                        ),
                    ],
                    style={"flex": 1, "margin-right": "10px"},
                ),
                html.Div(
                    [
                        html.Label("Select y-axis:"),
                        dcc.Dropdown(
                            id="y-axis",
                            options=[
                                {"label": col, "value": col} for col in data_options
                            ],
                            value="Pore volume",
                            multi=False,
                        ),
                    ],
                    style={"flex": 1},
                ),
            ],
            style={"display": "flex", "margin-bottom": "20px"},
        ),
        # Graph below the dropdowns
        dcc.Graph(id="scatter-plot"),
        # Hover data selector
        html.Div(
            [
                html.Label("Select hover data:"),
                dcc.Dropdown(
                    id="hover-dropdown",
                    options=[{"label": col, "value": col}
                             for col in data_options],
                    value=[],
                    multi=True,
                ),
            ]
        ),
    ]
)


@app.callback(
    Output("scatter-plot", "figure"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
    Input("hover-dropdown", "value"),
)
def update_scatter(x_axis, y_axis, selected_hover_data):
    fig = px.scatter(
        data_frame=df,
        x=x_axis,
        y=y_axis,
        color="Type of Adsorbent",
        title="Adsorbents",
        labels={"color": "Type of Adsorbent"},
        hover_data=selected_hover_data,
        hover_name="Name",
        width=1000,
        height=800,
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
