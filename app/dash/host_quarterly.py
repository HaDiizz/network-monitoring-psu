from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_required
from dash import callback_context, Input, Output

dash_host_quarterly = dash.Dash(__name__, server=server,
                      url_base_pathname='/admin/hosts/quarterly/',
                      external_stylesheets=['../static/css/dash/main.css']
                      )

for view_func in server.view_functions:
    if view_func.startswith(dash_host_quarterly.config.url_base_pathname):
        server.view_functions[view_func] = login_required(
            server.view_functions[view_func])

dash_host_quarterly.layout = html.Div([
    html.H1('Host Quarterly')
])

@dash_host_quarterly.callback(
    dash.Output('output', 'children'),
    [dash.Input('button', 'n_clicks')]
)
def update_output(n_clicks):
    if n_clicks is None:
        return ''

    # Get the year and month variables from the Dash context.
    year = dash.ctx.get("year")
    month = dash.ctx.get("month")

    # Print the year and month variables to the console.
    print('Year:', year)
    print('Month:', month)

    # Return a response that displays the year and month.
    return f'Year: {year}, Month: {month}'