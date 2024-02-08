import dash
import dash_core_components as dcc
import dash_html_components as html
from ... import models
from ...helpers.utils import sla_status_list


def get_color(sla, ok, critical):
    if sla >= ok:
        return "green"
    elif sla < ok and sla > critical:
        return "#FACC15"
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
        sla = item['availability']
        key = (year, month)
        if key in cumulative_sla:
            cumulative_sla[key] += sla
            record_count[key] += 1
        else:
            cumulative_sla[key] = sla
            record_count[key] = 1
    return cumulative_sla, record_count


def monthly_callbacks(dash_app, selection):
    @dash_app.callback(
        [dash.dependencies.Output('cards-row', 'children'),
         dash.dependencies.Output('sla-percentage-detail', 'children'),
         dash.dependencies.Output('average-sla-per-year', 'children'),
         dash.dependencies.Output('sla-graph', 'figure')
         ],
        [dash.dependencies.Input('year-dropdown', 'value')]
    )
    def update_cards(selected_year):

        sla_requirement = None
        if selection == "host":
            sla_requirement = models.SLAConfig.objects(year=selected_year, category="Host").first()
        elif selection == "access_point":
            sla_requirement = models.SLAConfig.objects(year=selected_year, category="Access Point").first()            
        else:
            sla_requirement = models.SLAConfig.objects(year=selected_year, category="Service").first()            

        if sla_requirement is None:
            sla_requirement = sla_status_list()
        if selection == "host":
            host_monthly_data = models.Host.objects(year=selected_year)
            filtered_data = [
                item for item in host_monthly_data if item['year'] == selected_year]
        elif selection == "access_point":
            accessPoint_monthly_data = models.AccessPoint.objects(year=selected_year)
            filtered_data = [
                item for item in accessPoint_monthly_data if item['year'] == selected_year]
        else:
            service_monthly_data = models.Service.objects(year=selected_year)
            filtered_data = [
                item for item in service_monthly_data if item['year'] == selected_year]
        
        cumulative_sla, record_count = calculate_cumulative_sla(filtered_data)

        cards = [
            html.A(
                html.Div(
                    html.Div([
                        html.P(get_month(month)),
                        html.P(
                            f"SLA: {( round(cumulative_sla.get((year, month), 0) / record_count.get((year, month), 1) * 100, 4) / 100):.4f}%",
                            style={'font-size': '12px'}
                        ),
                    ],
                        className="text-white justify-center text-center p-3")
                ),
                style={'width': '90px', 'height': '90px', 'background': get_color(
                    cumulative_sla.get((year, month), 0) / record_count.get((year, month), 1), sla_requirement["ok_status"], sla_requirement["critical_status"])},
                className='p-5 text-center flex justify-center card place-self-center',
                href = f"hosts/{year}/{month}" if selection == "host" else (f"access-points/{year}/{month}" if selection == "access_point" else f"services/{year}/{month}")
            )
            for (year, month), cumulative_sla_value in cumulative_sla.items()
        ]

        service_percentage = [
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="bx bxs-circle pt-1",
                               style={"color": "green"}),
                        html.Span(
                            f"OK Status: ≥ {sla_requirement['ok_status']}%"),
                    ], className="flex gap-5"),
                    html.Div([
                        html.I(className="bx bxs-circle pt-1",
                               style={"color": "#FACC15"}),
                        html.Span(
                            f"WARNING Status: > {sla_requirement['critical_status']}% and < {sla_requirement['ok_status']}%"),
                    ], className="flex gap-5"),
                    html.Div([
                        html.I(className="bx bxs-circle pt-1",
                               style={"color": "red"}),
                        html.Span(
                            f"CRITICAL Status: ≤ {sla_requirement['critical_status']}%"),
                    ], className="flex gap-5"),
                ], className="grid gap-5"),
                html.Div([
                    html.A([
                        "SLA Configuration",
                        html.I(className="bx bxs-cog pt-1"),
                    ],
                        className="flex gap-5",
                        style={"color": "#8D33FF"},
                        href="/admin/service-level-agreement"),
                ]),
            ], className="flex justify-between border m-5 gap-5", style={"padding": "2rem", "border-radius": "2rem"})
        ]

        average_sla_per_year = {
            year: cumulative_sla[year] / record_count[year] for year in cumulative_sla}
        total_sum = 0
        for value in average_sla_per_year.values():
            total_sum += value

        sla_avg = "{:.4f}".format(round(total_sum/len(average_sla_per_year), 8))

        graph_figure = {
            'data': [
                {'x': [f"{get_month(month)} {year}" for year, month in cumulative_sla.keys()],
                 'y': ['{:.4f}'.format(round(cumulative_sla_value / record_count.get((year, month), 1), 8)) for (year, month), cumulative_sla_value in cumulative_sla.items()],
                 'type': 'line',
                 'name': 'Average SLA'}
            ],
            'layout': {
                'title': 'Average SLA by Month and Year',
                'xaxis': {'title': 'Month and Year'},
                'yaxis': {'title': 'Average SLA'}
            }
        }

        return cards, service_percentage, f"SLA Average in {selected_year} is {sla_avg}%", graph_figure
