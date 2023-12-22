from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_required
import datetime
from .callback import monthly_callbacks



dash_host = dash.Dash(__name__, server=server,
                      url_base_pathname='/admin/hosts/',
                      external_stylesheets=['../static/css/dash/main.css']
                      )

for view_func in server.view_functions:
    if view_func.startswith(dash_host.config.url_base_pathname):
        server.view_functions[view_func] = login_required(
            server.view_functions[view_func])


def generate_year_options():
    current_year = datetime.datetime.now().year
    year_options = [{'label': str(year), 'value': year} for year in range(2023 - 2, current_year + 1)] #! Delete -2 this is for test function
    return year_options

dash_host.layout = html.Div([
    html.H1("Host Monthly", className='text-4xl font-bold', style={'padding-bottom': '3rem'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[
            # {'label': '2021', 'value': 2021},
            # {'label': '2022', 'value': 2022},
            {'label': '2023', 'value': 2023},
        ],
        value=datetime.datetime.now().year,
        style={'margin-bottom': '20px'},
    ),
    html.Div(id='average-sla-per-year', className='text-left font-bold text-2xl', style={'margin-top': '3rem'}),
    html.Div(id='cards-row', className='dash_card'),
    html.Div(id='sla-percentage-detail', className='text-left', style={'margin-top': '2rem'}),
        html.Div([
        html.Div(dcc.Graph(id='sla-graph'), className='pt-2') 
    ], className='grid grid-cols-1'),
], className='')


monthly_callbacks(dash_host, "host")
