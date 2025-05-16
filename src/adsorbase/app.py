from adsorbase.callbacks import register_callbacks
from dash import Dash
from adsorbase.layout import full_layout

app = Dash(__name__)

app.layout = full_layout

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
