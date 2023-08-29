from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_required
import datetime
from dash.dependencies import Input, Output

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


def get_color(sla):
    if sla > 50:
        return "green"
    else:
        return "red"


def get_month(month):
    if month == 1:
        return "JAN"
    elif month == 2:
        return "FEB"
    elif month == 3:
        return "MAR"
    elif month == 4:
        return "APR"
    elif month == 5:
        return "MAY"
    elif month == 6:
        return "JUN"
    elif month == 7:
        return "JUL"
    elif month == 8:
        return "AUG"
    elif month == 9:
        return "SEP"
    elif month == 10:
        return "OCT"
    elif month == 11:
        return "NOV"
    elif month == 12:
        return "DEC"


def calculate_cumulative_sla(data):
    cumulative_sla = {}
    record_count = {}
    for item in data:
        year = item['year']
        month = item['month']
        sla = item['sla']
        key = (year, month)
        if key in cumulative_sla:
            cumulative_sla[key] += sla
            record_count[key] += 1
        else:
            cumulative_sla[key] = sla
            record_count[key] = 1
    return cumulative_sla, record_count

def monthly_callbacks(dash_host):
    @dash_host.callback(
        [dash.dependencies.Output('cards-row', 'children'),
         dash.dependencies.Output('average-sla-per-year', 'children'),
         dash.dependencies.Output('sla-graph', 'figure')
        ],
        [dash.dependencies.Input('year-dropdown', 'value')]
    )
    def update_cards(selected_year):
        filtered_data = [
            item for item in mock_host_monthly if item['year'] == selected_year]
        cumulative_sla, record_count = calculate_cumulative_sla(filtered_data)

        cards = [
            html.A(
                html.Div(
                    html.Div([
                        html.P(get_month(month)),
                        html.P(
                            f"SLA: {cumulative_sla.get((year, month), 0) / record_count.get((year, month), 1):.2f}%",
                            style={'font-size': '12px'}
                            ),
                    ],
                        className="text-white justify-center text-center p-3")
                ),
                style={'width': '90px', 'height': '90px', 'background': get_color(
                    cumulative_sla.get((year, month), 0) / record_count.get((year, month), 1))},
                className='p-5 text-center flex justify-center card place-self-center',
                href=f"hosts/{year}/{month}"
            )
            for (year, month), cumulative_sla_value in cumulative_sla.items()
        ]

        #Cal AVG OF SLA PER YEAR
        average_sla_per_year = {year: cumulative_sla[year] / record_count[year] for year in cumulative_sla}
        total_sum = 0
        for value in average_sla_per_year.values():
            total_sum += value

        sla_avg = "{:.{}f}".format((total_sum/len(average_sla_per_year)),2)
        #

        graph_figure = {
        'data': [
            {'x': [f"{get_month(month)} {year}" for year, month in cumulative_sla.keys()],
             'y': [cumulative_sla_value / record_count.get((year, month), 1) for (year, month), cumulative_sla_value in cumulative_sla.items()],
             'type': 'line',
             'name': 'Average SLA'}
        ],
        'layout': {
            'title': 'Average SLA by Month and Year',
            'xaxis': {'title': 'Month and Year'},
            'yaxis': {'title': 'Average SLA'}
        }
    }

        return cards, f"SLA Average in {datetime.datetime.now().year} is {sla_avg}",graph_figure
