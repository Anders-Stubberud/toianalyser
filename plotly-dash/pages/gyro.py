from dash import dcc, html, callback
from dash.dependencies import Input, Output
import os
import dash_mantine_components as dmc
import pickle
import utils
import pandas as pd
from datetime import datetime

path_results_gyro = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resultater', 'gyro')
GYRODATA = 'gyrodata'
VEKTDATA = 'vektdata'
HASTIGHETSDATA = 'hastighetsdata'

with open(os.path.join(path_results_gyro, f'all_dates.pkl'), 'rb') as file:
    all_dates_dt = pickle.load(file)

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Overordnet, Stabilitetsanalyse', order=2),
                html.Br(),
                dmc.Title("Stabilitetsanalyse", order=4),
                # Overordnet informajson om Gyro-data
                dmc.Text("""
                    Vi ønsker å undersøke hvordan trafikksikkerheten påvirkes med tanke på stabilitet.
                    
                    Det har blitt ettermontert Teltonika FM som samler data for aksellerasjon, bremsing, hastighet og hard sving.
                    Sensoren består av en GPS og et akselerometer. Link til mer info finner du her:
                """, size='lg'),
                dcc.Markdown('''
                    [Teltonika Green Driving Solution](https://wiki.teltonika-gps.com/index.php?title=Green_Driving_Solution&mobileaction=toggle_view_desktop)
                ''', style={'font-size': '18px'}
                ),
                html.Br()
            ],
        ),

        dmc.Paper(  # Main container
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title("Stabilitetsanalyse", order=4),

                # informasjon om hver av tabs'ene her
                dmc.Text("""
                    I analysen tar vi i bruk data fra posisjonsrapporten for 2023 og 2024, ettersom sensorene ble ettermontert i 2023. Vi har filtrert ut all data hvor kjøretøyet har 
                    en hastighet på under 20 km/t for å redusere feil i målingene. 
                    Det er registert målinger for hard sving for èn lastebil og x hengere. Grunnen til at sensorene er montert på hengerne er for å få posisjonsdata 
                    slik at man lettere kan se hvilke ekvipasjer som har kjørt sammen.
                        Terskelen for hva som anses som trafikkfarlig er når lastebilen overstiger 0,34 g i en sving, da dette skal være nok til at lastebilen velter.
                         Denne terskelen er bestemt av produsenten som man om ønskelig kan se nærmere på i linken over. 
                    
                         Fra analysen ser man at mange av verdiene overstiger 0,34 g. Dette kan skyldes at sensorene ikke ble festet godt nok ved montering. 
                         Plasseringen av sensoren kan også være med å påvirke. 

                    • Endring i Gyrodata og Vekt per Dag: Visualiserer endringer i data fra aksellerometer og vekt over tid for hver vektklasse.
                    Dette gjør det mulig å se om det er en sammenheng mellom last og ustabilitet.
                    Denne fanen gir en oversikt over hvilken last lastebilen kjørte med når den fikk et utslag for "Hard sving" og viser utvikling over tid. 
                    Den tillater deg å se detaljerte grafer for hvert enkelt kjøretøy ved valgte datoer. 

                    • Statistikk: Viser en tabell med statistikk basert på gyrodata. Tabellen oppsummerer relevante 
                    statistiske målinger som gjennomsnitt max og min verdi, og gir en kort oppsummering av 
                    dataene.

                    • Kartvisualisering: Presenterer en geografisk kartvisualisering av dataene. Kartet gir en visuell 
                    fremstilling av hvordan dataene er distribuert geografisk og brukes for å se om det er noen spesielle steder hvor det er mer utslag.

                    • Vekt- og hastighetpåvirkning: Viser spredningsdiagrammer som illustrerer forholdet mellom aksellerasjon og ulike variabler som vekt og hastighet. 
                    
                """, size="lg", style={'white-space': 'pre-line'}),

                html.Br(),
                
                dcc.Tabs(id='tabs', value='gyro-tab', children=[
                    dcc.Tab(label='Endring i gyrodata og vekt per dag', value='gyro-tab', children=[
                        html.Div(
                            style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'},
                            children=[
                                html.H4("Velg en dato:", style={'margin-bottom': '10px'}),
                                dcc.DatePickerSingle(
                                    id='date-slider',
                                    date=all_dates_dt[3],  # Default date
                                    min_date_allowed=all_dates_dt[0],
                                    max_date_allowed=all_dates_dt[-1],
                                    placeholder='Select a date'
                                ),
                                html.Div(id='gyro-graphs-container', style={'margin-top': '20px'}),
                            ]
                        )
                    ]),
                    dcc.Tab(label='Statistikk', value='stats-tab', children=[
                        html.Div(
                            style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'},
                            children=[
                                html.H4("Statistikkdata", style={'margin-bottom': '10px'}),
                                dcc.Loading(
                                    id="loading",
                                    type="circle",
                                    children=[
                                        html.Div(id='gyro-stats-table')
                                    ]
                                )
                            ]
                        )
                    ]),
                    dcc.Tab(label='Kartvisualisering', value='map-tab', children=[
                        html.Div(
                            style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'},
                            children=[
                                dcc.Loading(
                                    id="loading-map",
                                    type="circle",
                                    children=[
                                        dcc.Graph(
                                            id='map-plot',
                                            style={'height': '60vh', 'width': '100%'}
                                        )
                                    ]
                                )
                            ]
                        )
                    ]),
                    dcc.Tab(label='Vekt- og hastighetpåvirkning', value='scatter-tab', children=[
                        html.Div(
                            style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px', 'background-color': '#f9f9f9'},
                            children=[
                                html.H4("Spredningsdiagrammer", style={'margin-bottom': '10px'}),
                                dcc.Loading(
                                    id="loading-scatter",
                                    type="circle",
                                    children=[
                                        html.Div(id='scatter-graphs-container')
                                    ]
                                )
                            ]
                        )
                    ]),
                ]),
            ],
        ),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    Output('gyro-graphs-container', 'children'),
    [Input('tabs', 'value'),
     Input('date-slider', 'date')],
)
def update_graphs(active_tab, selected_date):
    if not selected_date:
        selected_date = all_dates_dt[3]
    
    # Convert selected_date to Timestamp
    selected_date_ts = pd.Timestamp(selected_date)
    
    # Find the index of the selected date
    date_index = next((i for i, date in enumerate(all_dates_dt) if date.date() == selected_date_ts.date()), None)
    
    if date_index is None:
        return dmc.Alert(
            title="Ingen data for denne datoen.",
            color="red",
            children=f"Vi kunne ikke finne data for datoen {selected_date}. Vennligst velg en annen dato."
        )
    
    graphs = []
    for file_name in [
        os.path.join(path_results_gyro, 'gyrodata', f'{active_tab} {date_index} {GYRODATA}.pkl'),
        os.path.join(path_results_gyro, 'gyrodata', f'{active_tab} {date_index} {VEKTDATA}.pkl'),
        os.path.join(path_results_gyro, 'gyrodata', f'{active_tab} {date_index} {HASTIGHETSDATA}.pkl'),
    ]:
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                figure = pickle.load(file)
                graphs.append(dcc.Graph(figure=figure, style={'height': '400px'}))
        else:
            return dmc.Alert(
                title="Datafil ikke funnet.",
                color="orange",
                children=f"Filen {file_name} ble ikke funnet. Vennligst sjekk at datafilene eksisterer."
            )

    return graphs

@callback(
    Output('gyro-stats-table', 'children', allow_duplicate=True),
    [Input('tabs', 'value')],
    prevent_initial_call=True
)
def update_statistics(selected_tab): # statistikk
    if selected_tab != 'stats-tab':
        return []
    
    with open(os.path.join(path_results_gyro, f'{selected_tab}.pkl'), 'rb') as file:
        return pickle.load(file)

@callback(
    Output('map-plot', 'figure'),
    [Input('tabs', 'value')],
    prevent_initial_call = True
)
def update_map_plot(active_tab): # kartvisualisering 
    if active_tab != 'map-tab':
        return {}

    with open(os.path.join(path_results_gyro, f'{active_tab}.pkl'), 'rb') as file:
        return pickle.load(file)
    
@callback(
    Output('scatter-graphs-container', 'children'),
    [Input('tabs', 'value')],
    prevent_initial_call = True
)
def weight_speed_scatter(active_tab): # vektpåvirkning
    if active_tab != 'scatter-tab':
        return []

    with open(os.path.join(path_results_gyro, f'{active_tab}.pkl'), 'rb') as file:
        return pickle.load(file)
