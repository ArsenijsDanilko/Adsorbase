from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from pathlib import Path

#Initializing the  app 
app = Dash()

#Incorporating data
cwd = Path.cwd()
csv_file = cwd / "adsorbents.csv"
df2 = pd.read_csv(csv_file, sep=",")
df2.head()

#App layout
app.layout =[
    html.Div(children = 'Adsorbent Data'),
    html.Hr(),
    dcc.RadioItems(options=['BET Surface Area', 'Pore volume', 'Adsorption capacity']),
    dash_table.DataTable(data=df2.to_dict('records'), page_size=14),
    dcc.Graph(figure={}, id='my-final-graph-example'),
] 

@callback(
    Output(component_id='my-final-graph-example', component_property='figure'),
    Input(component_id='my-final-radio-item-example', component_property='value')
)
def update_graph(col_chosen_x,col_chosen_y):
    fig = px.histogram(df2, x=col_chosen_x, y=col_chosen_y, histfunc='avg')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)