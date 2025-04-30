from dash import Dash, html, dcc, Input, Output
import pandas as pd
from pathlib import Path
import plotly.express as px

cwd = Path.cwd()
df = pd.read_csv(cwd / "adsorbents.csv")
app = Dash(__name__)

hover_options = [
    "Type of Adsorbent",
    "BET Surface Area",
    "Pore volume",
    "Adsorption capacity",
    "Conditions T",
    "Conditions P",
]
app.layout = html.Div(
    [
        html.H4("Select hover data:"),
        dcc.Dropdown(
            id="hover-dropdown",
            options=[{"label": col, "value": col} for col in hover_options],
            value=["Pore Volume", "Adsorption capacity"],
            multi=True,
        ),
        dcc.Graph(id="scatter-plot"),
    ]
)


@app.callback(Output("scatter-plot", "figure"), Input("hover-dropdown", "value"))
def update_scatter(selected_hover_data):
    fig = px.scatter(
        df,  # data to pull from
        x="Pore volume",  # column name withx-axis
        y="Adsorption capacity",  # column name withy-axis
        size="BET Surface Area",
        size_max=20,
        color="Type of Adsorbent",  # color by application
        title="Adsorbents",  # title of the plot
        labels={"color": "Type of Adsorbent"},  # label for the color legend
        hover_data=selected_hover_data,
        hover_name="Name",
        width=1000,
        height=800,
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
