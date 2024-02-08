from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_required
import datetime
from .callback import monthly_callbacks
from .. import models


dash_access_point = dash.Dash(__name__, server=server,
                      url_base_pathname='/admin/access-points/',
                      external_stylesheets=['../static/css/dash/main.css']
                      )

for view_func in server.view_functions:
    if view_func.startswith(dash_access_point.config.url_base_pathname):
        server.view_functions[view_func] = login_required(
            server.view_functions[view_func])


def generate_year_options():

    try:
        current_year = datetime.datetime.now().year
        accessPoint_start_year = models.AccessPoint.objects.order_by('year').first().year
        year_options = [{'label': str(year), 'value': year} for year in range(accessPoint_start_year, current_year + 1)]
    except (AttributeError, ValueError):
        print("WARNING: Generating year options based on current year, as no valid data found in the database.")
        year_options = [{'label': str(year), 'value': year} for year in range(2023, current_year + 1)]

    return year_options

dash_access_point.layout = html.Div([
    html.H1("Access Point Monthly", className='text-4xl font-bold', style={'padding-bottom': '3rem'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=generate_year_options(),
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


monthly_callbacks(dash_access_point, "access_point")
