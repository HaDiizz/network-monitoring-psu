from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html

dash_app = dash.Dash(__name__, server=server)