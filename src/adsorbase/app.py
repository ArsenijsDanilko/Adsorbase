from adsorbase.callbacks import register_callbacks
from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

# Import layout AFTER app initialisation to avoid circular imports
from adsorbase.layout import full_layout

app.layout = full_layout

register_callbacks(app)
