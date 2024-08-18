import dash
from dash import dcc, html, callback, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
import pickle
import utils
import dash_mantine_components as dmc

def pickle_load_file(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)
    
path_results_kapasitet = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resultater', 'kapasitet')
marks = pickle_load_file(os.path.join(path_results_kapasitet, 'marks.pkl'))
date_to_number = {v: k for k, v in marks.items()}

date_marks = {k: pd.to_datetime(v) for k, v in marks.items()}
all_dates_dt = sorted(date_marks.values())
default_date = marks[0]
min_date = all_dates_dt[0]  
max_date = all_dates_dt[-1]  

def layout():

    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Overordnet, Kapasitetsutnyttelse', order=2),
                html.Br(),

                # Overordnet informasjon om Kapasitetsutnyttelse
                dmc.Text("""
                    Kapasitetsutnyttelse refererer til hvor effektivt et system eller en ressurs benyttes i forhold til dens totale tilgjengelige kapasitet. 
                    I konteksten av de oppdaterte visualiseringene kan analyser av kapasitetsutnyttelse gi innsikt i hvordan lastebilene utnytter kapasiteten over tid 
                    for å se om det vil lønne seg å øke tillat totalvekt fra 60 til 74-tonn.

                """, size="lg", style={'white-space': 'pre-line'}),

                html.Br()
            ],
        ),

        dmc.Paper(
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title("Visualisering av aktuell vekt over tid", order=2),

                # informasjon om hver av tabs'ene her
                dmc.Text("""
                    Denne delen av analysen viser vektsdata over tid for hver vektklasse, for å gi et bedre innblikk i kapasitetsutnyttelse. 
                    Her er hva du finner:

                    • Endring i Vekt per Dag: Viser hvordan vekten varierer daglig og gir innsikt i kortsiktige trender.

                    • Statistikk: Gir en oppsummering av dataene med statistikk for blandt annet gjennomsnitt og max og min verdi.

                    • Endring i Vekt per År: Analyserer langsiktige endringer i vekt på årsbasis, og avslører langsiktige trender og sesongmessige effekter.
                """, size="lg", style={'white-space': 'pre-line'}),

                html.Br(),
                dcc.Tabs(id='tabs', value='weight-tab', children=[
                    dcc.Tab(label='Endring i vekt per dag', value='weight-tab', children=[
                        html.Div(
                            style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'},
                            children=[
                                html.H4("Velg en dato:", style={'margin-bottom': '10px'}),
                                dcc.DatePickerSingle(
                                    id='date-slider',
                                    date=default_date,
                                    min_date_allowed=min_date,
                                    max_date_allowed=max_date,
                                    placeholder='Velg en dato'
                                ),
                                html.Div(id='graphs-container', style={'margin-top': '20px'}),
                            ]
                        )
                    ]),

                    dcc.Tab(label='Statistikk', value='year-tab', children=[
                        html.H4("Velg et år:", style={'margin-bottom': '10px', 'margin-top': '10px'}),
                        dcc.Dropdown(
                            id='year-dropdown',
                            style={'width': '50%', 'margin-bottom': '10px'}
                        ),
                        html.Div(id='yearly-stats-table', style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'})
                    ]),

                    dcc.Tab(label='Endring i vekt per år', value='stats-tab', children=[
                        html.H4("Velg et år:", style={'margin-bottom': '10px', 'margin-top': '10px'}),
                        dcc.Dropdown(
                            id='year-dropdown-graphs',
                            style={'width': '50%', 'margin-bottom': '10px'}
                        ),
                        html.Div(id='yearly-graphs-container', style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'})
                    ]),

                ]),
            ],
        ),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    Output('graphs-container', 'children'),
    [Input('tabs', 'value'),
     Input('date-slider', 'date')],
)
def update_graphs(active_tab, selected_date):
    try:    
        return pickle_load_file(os.path.join(path_results_kapasitet, f'update_graphs weight-tab {date_to_number[selected_date]}.pkl'))
    except:
        return dmc.Alert(
            title="Ingen data for denne datoen.",
            color="red",
            children=f"Vi kunne ikke finne data for datoen {selected_date}. Vennligst velg en annen dato."
        )

@callback(
    [Output('year-dropdown', 'options'),
    Output('year-dropdown', 'value')],
    Input('tabs', 'value'),
    prevent_initial_call = True
)
def update_year_dropdown(active_tab):
    # return pickle_load_file(os.path.join(path_results_kapasitet, f'update_year_dropdown.pkl'))
    return ([{'label': '2021', 'value': 2021}, {'label': '2022', 'value': 2022}, {'label': '2023', 'value': 2023}, {'label': '2024', 'value': 2024}], 2021)

@callback(
    Output('yearly-stats-table', 'children', allow_duplicate=True),
    [Input('year-dropdown', 'value')],
    prevent_initial_call=True
)
def update_yearly_stats_table(selected_year):
    return pickle_load_file(os.path.join(path_results_kapasitet, f'update_yearly_stats_table {selected_year}.pkl'))

@callback(
    [Output('year-dropdown-graphs', 'options'),
    Output('year-dropdown-graphs', 'value')],
    Input('tabs', 'value'),
    prevent_initial_call = True
)
def update_year_dropdown(active_tab):
    # return pickle_load_file(os.path.join(path_results_kapasitet, f'update_year_dropdown.pkl'))
    return ([{'label': '2021', 'value': 2021}, {'label': '2022', 'value': 2022}, {'label': '2023', 'value': 2023}, {'label': '2024', 'value': 2024}], 2021)

@callback(
    Output('yearly-graphs-container', 'children', allow_duplicate=True),
     Input('year-dropdown-graphs', 'value'),
    prevent_initial_call=True
)
def update_yearly_graphs(selected_year=2021):
    return pickle_load_file(os.path.join(path_results_kapasitet, f'update_yearly_graphs {selected_year}.pkl'))

if __name__ == '__main__':
    # update_yearly_graphs
    for year in [2021, 2022, 2023, 2024]:
        graphs = update_yearly_graphs(year)
        filename = os.path.join(path_results_kapasitet, f'update_yearly_graphs {year}.pkl')
        if not os.path.exists(filename):
            with open (filename, 'wb') as file:
                pickle.dump(graphs, file)

    # update_year_dropdown x 2 
    stats = update_year_dropdown('stats-tab')
    filename = os.path.join(path_results_kapasitet, f'update_year_dropdown.pkl')
    if not os.path.exists(filename):
        with open (filename, 'wb') as file:
            pickle.dump(graphs, file)

    # update_yearly_stats_table
    for year in [2021, 2022, 2023, 2024]:
        graphs = update_yearly_stats_table(year)
        filename = os.path.join(path_results_kapasitet, f'update_yearly_stats_table {year}.pkl')
        if not os.path.exists(filename):
            with open (filename, 'wb') as file:
                pickle.dump(graphs, file)

    # update_graphs
    for date_index in range(len(dataframes['74 tonn']['Dato'].unique())):
        graphs = update_graphs('weight-tab', date_index)
        filename = os.path.join(path_results_kapasitet, f'update_graphs weight-tab {date_index}.pkl')
        if not os.path.exists(filename):
            with open (filename, 'wb') as file:
                pickle.dump(graphs, file)