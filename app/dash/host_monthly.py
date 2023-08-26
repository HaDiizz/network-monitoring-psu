from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_required

mock_host_monthly = [
    {
        "_id": 1,
        "host_id": 1,
        "month": 1,
        "year": 2021,
        "sla": 90.8
    },
    {
        "_id": 2,
        "host_id": 2,
        "month": 1,
        "year": 2021,
        "sla": 40.5
    },
    {
        "_id": 3,
        "host_id": 1,
        "month": 2,
        "year": 2021,
        "sla": 80.5
    },
    {
        "_id": 4,
        "host_id": 1,
        "month": 3,
        "year": 2021,
        "sla": 75.2
    },
    {
        "_id": 5,
        "host_id": 1,
        "month": 4,
        "year": 2021,
        "sla": 88.1
    },
    {
        "_id": 6,
        "host_id": 1,
        "month": 5,
        "year": 2021,
        "sla": 92.4
    },
    {
        "_id": 7,
        "host_id": 1,
        "month": 6,
        "year": 2021,
        "sla": 85.7
    },
    {
        "_id": 8,
        "host_id": 1,
        "month": 7,
        "year": 2021,
        "sla": 90.2
    },
    {
        "_id": 9,
        "host_id": 1,
        "month": 8,
        "year": 2021,
        "sla": 81.5
    },
    {
        "_id": 10,
        "host_id": 1,
        "month": 9,
        "year": 2021,
        "sla": 89.8
    },
    {
        "_id": 11,
        "host_id": 1,
        "month": 10,
        "year": 2021,
        "sla": 78.9
    },
    {
        "_id": 12,
        "host_id": 1,
        "month": 11,
        "year": 2021,
        "sla": 92.2
    },
    {
        "_id": 13,
        "host_id": 1,
        "month": 12,
        "year": 2021,
        "sla": 84.1
    },
    {
        "_id": 14,
        "host_id": 1,
        "month": 1,
        "year": 2022,
        "sla": 87.4
    },
    {
        "_id": 15,
        "host_id": 1,
        "month": 2,
        "year": 2022,
        "sla": 79.6
    },
    {
        "_id": 16,
        "host_id": 1,
        "month": 3,
        "year": 2022,
        "sla": 93.1
    },
    {
        "_id": 17,
        "host_id": 1,
        "month": 4,
        "year": 2022,
        "sla": 80.9
    },
    {
        "_id": 19,
        "host_id": 2,
        "month": 1,
        "year": 2022,
        "sla": 50.4
    },
    {
        "_id": 20,
        "host_id": 2,
        "month": 2,
        "year": 2022,
        "sla": 42.3
    },
    {
        "_id": 21,
        "host_id": 2,
        "month": 3,
        "year": 2022,
        "sla": 53.1
    },
    {
        "_id": 22,
        "host_id": 2,
        "month": 4,
        "year": 2022,
        "sla": 43.8
    },
    {
        "_id": 23,
        "host_id": 2,
        "month": 5,
        "year": 2022,
        "sla": 51.5
    },
    {
        "_id": 24,
        "host_id": 2,
        "month": 6,
        "year": 2022,
        "sla": 44.7
    },
    {
        "_id": 25,
        "host_id": 2,
        "month": 7,
        "year": 2022,
        "sla": 52.4
    },
    {
        "_id": 26,
        "host_id": 2,
        "month": 8,
        "year": 2022,
        "sla": 45.6
    },
    {
        "_id": 27,
        "host_id": 2,
        "month": 9,
        "year": 2022,
        "sla": 53.3
    },
    {
        "_id": 28,
        "host_id": 2,
        "month": 10,
        "year": 2022,
        "sla": 46.5
    },
    {
        "_id": 29,
        "host_id": 2,
        "month": 11,
        "year": 2022,
        "sla": 54.2
    },
    {
        "_id": 30,
        "host_id": 2,
        "month": 12,
        "year": 2022,
        "sla": 47.4
    },
    {
        "_id": 31,
        "host_id": 2,
        "month": 1,
        "year": 2023,
        "sla": 55.1
    },
    {
        "_id": 32,
        "host_id": 2,
        "month": 2,
        "year": 2023,
        "sla": 48.3
    },
    {
        "_id": 33,
        "host_id": 2,
        "month": 3,
        "year": 2023,
        "sla": 56
    },
    {
        "_id": 34,
        "host_id": 2,
        "month": 4,
        "year": 2023,
        "sla": 49.2
    },
    {
        "_id": 35,
        "host_id": 2,
        "month": 5,
        "year": 2023,
        "sla": 56.9
    },
    {
        "_id": 36,
        "host_id": 3,
        "month": 1,
        "year": 2021,
        "sla": 95.1
    },
    {
        "_id": 37,
        "host_id": 3,
        "month": 2,
        "year": 2021,
        "sla": 86.9
    },
    {
        "_id": 38,
        "host_id": 3,
        "month": 3,
        "year": 2021,
        "sla": 97.2
    },
    {
        "_id": 39,
        "host_id": 3,
        "month": 4,
        "year": 2021,
        "sla": 88.7
    },
    {
        "_id": 40,
        "host_id": 3,
        "month": 5,
        "year": 2021,
        "sla": 98.3
    },
    {
        "_id": 41,
        "host_id": 3,
        "month": 6,
        "year": 2021,
        "sla": 89.6
    },
    {
        "_id": 42,
        "host_id": 3,
        "month": 7,
        "year": 2021,
        "sla": 99.4
    },
    {
        "_id": 43,
        "host_id": 3,
        "month": 8,
        "year": 2021,
        "sla": 90.5
    },
    {
        "_id": 44,
        "host_id": 3,
        "month": 9,
        "year": 2021,
        "sla": 100.5
    },
    {
        "_id": 45,
        "host_id": 3,
        "month": 10,
        "year": 2021,
        "sla": 91.4
    },
    {
        "_id": 46,
        "host_id": 3,
        "month": 11,
        "year": 2021,
        "sla": 101.6
    },
    {
        "_id": 47,
        "host_id": 3,
        "month": 12,
        "year": 2021,
        "sla": 92.3
    },
    {
        "_id": 48,
        "host_id": 3,
        "month": 1,
        "year": 2022,
        "sla": 102.7
    },
    {
        "_id": 49,
        "host_id": 3,
        "month": 2,
        "year": 2022,
        "sla": 93.2
    },
    {
        "_id": 50,
        "host_id": 3,
        "month": 3,
        "year": 2022,
        "sla": 103.8
    },
    {
        "_id": 51,
        "host_id": 3,
        "month": 4,
        "year": 2022,
        "sla": 94.1
    },
    {
        "_id": 52,
        "host_id": 3,
        "month": 5,
        "year": 2022,
        "sla": 104.9
    },
    {
        "_id": 53,
        "host_id": 3,
        "month": 6,
        "year": 2022,
        "sla": 95
    }
]


dash_host = dash.Dash(__name__, server=server,
                      url_base_pathname='/admin/hosts/',
                      external_stylesheets=['../static/css/dash/main.css']
                      )

for view_func in server.view_functions:
    if view_func.startswith(dash_host.config.url_base_pathname):
        server.view_functions[view_func] = login_required(
            server.view_functions[view_func])


summary_result = []


def get_month():
    return


def get_color(total_sla):
    return


dash_host.layout = html.Div([
    html.H1("Host Monthly", className="text-4xl font-bold pb-5"),
    html.Div([
        html.Div([
            html.Div(
                [
                    # html.Div(get_month(date)),
                ],
                className=f"card text-white m-1 justify-center text-center",
                # style={'width': '120px', 'height': '80px',
                #    'background': get_color(total_sla)}
            )
            # for date, total_sla in summary_result.items()
        ],
            className="flex justify-center"
        )
    ])
])
