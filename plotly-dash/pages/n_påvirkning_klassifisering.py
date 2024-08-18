import os
import dash
import pandas as pd
from dash import html
import plotly.express as px
from dash import dash_table
from dash import dcc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
from dash import callback
import utils

current_dir = os.getcwd()
relative_path = 'resultater\\n_påvirkning_klassifisering.csv'  
file_path = os.path.join(current_dir, relative_path)

equation = r'''
$$
N = \frac{365 \cdot C \cdot E \cdot ÅDTT \cdot f \cdot (1.0 + 0.01p)^{20} - 1}{0.01p}
$$
'''

equation_bfaktor = r'''
$$
ESAL = \sum_{n=1}^{i} \left( \frac{w_i}{10} \right)^4 \cdot k_i
$$
'''

df = pd.read_csv(file_path)

# region Til grafene
steder = df['Sted'].unique()

def lag_grafer_for_sted(sted):
    '''Returnerer utvikling av ÅDTT, N, og B-faktor for spesifisert sted.'''
    df_sted = df[df['Sted'] == sted]

    graf_endring_ådtt = dcc.Graph(
        figure=px.line(
            df_sted, 
            x='Startdato', 
            y=['ÅDTT 5.6', 'ÅDTT 7.5'],
            title='Endring i ÅDTT'
        ),
        style={'width': '100%', 'aspect-ratio': '4 / 3', 'box-sizing': 'border-box'}
    )

    graf_endring_n = dcc.Graph(
        figure=px.line(
            df_sted, 
            x='Startdato', 
            y=['N 5.6', 'N 7.5'],
            title='Endring for N'
        ),
        style={'width': '100%', 'aspect-ratio': '4 / 3', 'box-sizing': 'border-box'}
    )

    graf_endring_bfaktor = dcc.Graph(
        figure=px.line(
            df_sted, 
            x='Startdato', 
            y=['B-faktor 5.6', 'B-faktor 7.5'], 
            title=f'Endring B-faktor'
            ),
        style={'width': '100%', 'aspect-ratio': '4 / 3', 'box-sizing': 'border-box'},
    )

    return html.Div(
        children=[
            graf_endring_ådtt,
            graf_endring_n,
            graf_endring_bfaktor
        ],
        style={'display': 'flex', 'flex-direction': 'row', 'width': '100%', 'max-width': '100%'}
    )
    

grafer = [html.Div([
    dmc.Title(sted, order=3),
    lag_grafer_for_sted(sted)
], style={'width': '100%'}) for sted in steder]
# endregion

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Påvirkning av vegfaktorer ved ny klassifisering av tunge kjøretøy', order=2),
                html.Br(),
                dmc.Title("Motivasjon bak statistikken", order=4),
                dmc.Text("""
                    Under konstruksjonen av nye veier benyttes en rekke faktorer for å avgjøre veiens behov.
                    Beregningen av disse faktorene baserer seg blant annet på trafikken fra tunge kjøretøy.
                    Grensen for klassifisering av tunge kjøretøy har lenge ligget på 5.6 meter.
                    Ettersom kjøretøyene som ferdes på de norske veiene har forandret seg en del siden denne grensen ble satt, 
                    er det nå diskusjoner rundt hvorvidt grensen for tunge kjøretøy burde endres for å reflektere endringene i kjøretøyene.
                    Beregningene nedenfor viser hvordan utvalgte faktorer blir påvirket ved å endre 
                    den etablerte grensen på 5.6 meter til 7.5 meter.
                """, size="lg"),

                html.Br(),

                dmc.Text("Følgende faktorer er særlig interessante:", size='lg'),

                dmc.List(
                    [
                        dmc.ListItem(dmc.Text("ÅDTT: gjennomsnittlig antall tunge kjøretøy per døgn i åpningsåret for vegen, benyttes i beregningen av N.", size='lg')),
                        dmc.ListItem( # N
                            dmc.Group(
                                children=[
                                    dmc.Text("N: antall ekvivalente 10 tonns aksler som vil belaste det aktuelle kjørefeltet i dimensjoneringsperioden,\
                                             som er satt til 20 år. N beregnes ut ifra formelen", size='lg'),
                                    dmc.Center(
                                        html.Div([
                                            dcc.Markdown(equation, mathjax=True, style={'fontSize': 14}),
                                            dmc.List([
                                                dmc.ListItem(dmc.Text("C er gjennomsnittlig antall aksler per tungt kjøretøy og er satt lik 2,4 i normalen.", size='lg')),
                                                dmc.ListItem(dmc.Text("""E er gjennomsnittlig ekvivalensfaktor for akslene på tunge kjøretøy. E 
                                                    beregnes ut ifra vekt på de enkelte akslene og deres bidrag til 
                                                    nedbrytning av vegen sammenlignet med en 10 tonns aksel (ut ifra 4. 
                                                    potensregelen). I dagens vegnormal er E=0,427 for veger med tillatt 
                                                    aksellast på 10 tonn""", size='lg'
                                                )),

                                                dmc.Group( # f
                                                    children=[
                                                        dmc.ListItem(dmc.Text("""f er fordelingsfaktor for tungtrafikken i kjørefeltene. Beregnes ut fra 
                                                            mengde tungtrafikk på dimensjonerende kjørefelt i forhold til total 
                                                            mengde tungtrafikk over alle kjørefelt. 
                                                        """, size='lg')),
                                                        dmc.List([
                                                            dmc.ListItem(dmc.Text("1-feltsveg, f = 1,0", size='lg')),
                                                            dmc.ListItem(dmc.Text("2-feltsveg, f = 0,50", size='lg')),
                                                            dmc.ListItem(dmc.Text("4-feltsveg, f = 0,45", size='lg')),
                                                            dmc.ListItem(dmc.Text("6-feltsveg, f = 0,40", size='lg')),
                                                        ], style={'margin-left': '30px'})
                                                    ]
                                                ),

                                                dmc.ListItem(dmc.Text("p er forventet årlig trafikkvekst for tunge kjøretøy (%).", size='lg'))
                                            ])
                                        ], style={'width': '50%'}),
                                        style={'width': '100%'}
                                    ),
                                ],
                                style={'display': 'flex', 'flexDirection': 'row'}
                            ),
                        ),
                        dmc.ListItem(
                            dmc.Group(
                                children=[
                                    dmc.Text("B-faktor: vegslitasjefaktor hentet fra det svenske regelverket. Beregnes som snittet av nedbrytende faktor for individuelle kjøretøy, ESAL, der ESAL beregnes", size='lg'),
                                    dmc.Center(
                                        html.Div([
                                            dcc.Markdown(equation_bfaktor, mathjax=True, style={'fontSize': 14}),
                                            dmc.List([
                                                dmc.ListItem(dmc.Text("i = antall enkeltaksler eller akselgrupper (boggi, trippelaksler osv.).", size='lg')),
                                                dmc.ListItem(dmc.Text("Wi = vekt (tonn) av enkeltaksler eller akselgrupper.", size='lg')),
                                                dmc.Group( # k
                                                    children=[
                                                        dmc.ListItem(dmc.Text("Ki = reduksjonsfaktor for ulike akselgrupper.", size='lg')),
                                                        dmc.List([
                                                            dmc.ListItem(dmc.Text("k = 1 for enkeltaksler.", size='lg')),
                                                            dmc.ListItem(dmc.Text("k = (10/18)⁴ = 0,0952 for boggiaksler", size='lg')),
                                                            dmc.ListItem(dmc.Text("k = (10/24)⁴ = 0,0302 for trippelaksler", size='lg')),
                                                        ], style={'margin-left': '30px'})
                                                    ]
                                                ),

                                                dmc.ListItem(dmc.Text("p er forventet årlig trafikkvekst for tunge kjøretøy (%).", size='lg'))
                                            ])
                                        ], style={'width': '50%'}),
                                        style={'width': '100%'}
                                    ),
                                ],
                                style={'display': 'flex', 'flexDirection': 'row'}
                            ),
                        )
                    ], 
                    style={'margin-left': '30px'}
                ),

                html.Br(),

                dmc.Title("Fremgangsmåte", order=4),
                dmc.Text("""
                    På Ånestad, Øysand, Verdal, og Skibotn er det installert såkalte Kistler-sensorer. Dette er sensorer som er gravd
                    ned i bakken, og registrer trafikken som kjører over de. Registreringene gir blant annet innblikk i kjøretøyets vekt, 
                    antall akslinger, og vektfordelingen over de ulike akslingene. Disse verdiene benyttes som parametre til 
                    de etablerte funksjonene som beregner faktorene.
                """, size="lg"),
                html.Br()
            ],
        ),

        dmc.Paper( # Grafer
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Visuell fremstilling av påvirkningene', order=2),
                html.Br(),
                dmc.Text("""
                    Plottene visualiserer påvirkningen endringen av klassifisering av tunge kjøretøy har på faktorene ÅDTT, N, og B-faktor
                    basert på data fra måleperioder gjort på Øysand, Skibotn, Verdal, og Ånestad.
                    Dette bidrar til å danne et mer nyansert bilde av påvirkningene. 
                """, size='lg'),
                html.Br(),
                *grafer
            ],
        ),  

        dmc.Paper( # Tabellen
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[  
                dmc.Title('Numerisk fremstilling av påvirkningen', order=2),
                html.Br(),
                dmc.Text("""
                    Tabellen viser den samme dataen som plottene ovenfor, altså påvirkningene fra endring av klassifisering av tunge kjøretøy.
                    Formålet med tabellen er å tilby et format som gi enklere tilgang til de konkrete verdiene. 
                """, size='lg'),
                html.Br(),
                dash_table.DataTable(
                    id='table_n_påvirkning_klassifisering',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    sort_action='native',
                    filter_action='native',
                    page_action='native',
                    style_table={'overflowX': 'auto', 'maxWidth': '100%'},

                    style_cell={
                        'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                        'whiteSpace': 'normal',
                        'textAlign': 'left',
                        'padding': '10px',
                    },

                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                    },

                    style_data={
                        'backgroundColor': 'rgb(248, 248, 248)',
                        'color': 'black',
                        'border': '1px solid grey',
                    },

                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(240, 240, 240)'
                        }
                    ],

                    style_as_list_view=True,
                )
            ],
        ), 

        html.Br(),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)
