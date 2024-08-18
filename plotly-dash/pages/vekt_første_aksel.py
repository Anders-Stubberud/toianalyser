import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os
import dash_mantine_components as dmc
from dash import callback
from uuid import uuid4
import utils

current_dir = os.getcwd()
relative_path_bwim = 'resultater\\vekt_første_aksel_bwim.csv'
file_path_bwim = os.path.join(current_dir, relative_path_bwim)
relative_path_kistler = 'resultater\\vekt_første_aksel_kistler.csv'
file_path_kistler = os.path.join(current_dir, relative_path_kistler)

df_bwim = pd.read_csv(file_path_bwim)
df_kistler = pd.read_csv(file_path_kistler)
df = pd.concat((df_bwim, df_kistler))
df['combo_id'] = "Sted: " + df['location'] + " startdato: " + df['startdate'] + " sluttdato: " + df['enddate']

def layout():
    return html.Div([
        dmc.Paper( # Overordnet informasjon
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Vekt på første aksel av 6-akslede semitrailere', order=2),
                html.Br(),
                dmc.Title("Motivasjon bak statistikken", order=4),
                dmc.Text("""
                    Statens vegvesen benytter seg blant annet av Kistler-sensorer for å gjøre vektmålinger av kjøretøy i fart.
                    Dette er induktive sløyfer som er gravd ned under veien.
                    For at disse sensorene skal registrere riktig vekt, er det nødvendig å kalibrere de.
                    Denne kalibreringen baserer seg på at et referansekjøretøy med kjente akselvekter kjører over sensorer.
                    Det er vanlig å benytte akselvekten på den første akslingen, ettersom vekten på nettopp denne akslingen forholder seg forholdsvis lik uavhengig av last på kjøretøyet.
                    Statistikken er dermed ment å supplere kalibreringsprosessen for Kistler-sensorene. 
                """, size="lg"),
                dmc.Title("Fremgangsmåte", order=4),
                dmc.Text("""
                    Resultatene har blitt funnet ved å benytte data fra WIM-installasjonene på Ånestad, Øysand, Skibotn, og Verdal, samt BWIM-installasjonene på Tangensvingen og Sørbryn.
                    For å hente ut 6-akslede semitrailere har det hovedsakelig blitt tatt utgangspunkt i de etterfølgende distansene på akslingene, gjennom
                """, size="lg"),
                dmc.Code(
                    children=[
                        html.Pre("""
                            df_semitrailers_with_6_axles = df.filter(
                                (pl.col(AXLES_COUNT) == 6) &
                                (pl.col(AXLE_DISTANCE_2) > 2.8) &
                                (pl.col(AXLE_DISTANCE_2) < 3.6) &
                                (pl.col(AXLE_DISTANCE_3) > 1.3) &
                                (pl.col(AXLE_DISTANCE_3) < 1.8)
                            )
                        """)
                    ]
                ),
                dmc.Text("""
                    Videre har ekstreme utstikkere blitt filtrert vekk. Her har grensen blitt satt ved 2 standardavvik, da dette inkluderer 96% av dataen under antagelsen av normalfordeling.
                """, size="lg"),
                html.Br()
            ],
        ),
        
        dmc.Paper( # Overordnet informasjon
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dcc.Dropdown(
                    id='combo_dropdown_vekt_første_aksel',
                    options=[{'label': combo, 'value': combo} for combo in df['combo_id'].unique()],
                    value=df['combo_id'].iloc[0],  # Default value
                    style={'width': '100%', 'height': '200%'},
                    maxHeight=500
                ),
                html.Div(id='histograms_container_vekt_første_aksel', style={'display': 'flex', 'justify-content': 'center'}),
            ],
        ),

        html.Br(),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    Output('histograms_container_vekt_første_aksel', 'children'),
    [Input('combo_dropdown_vekt_første_aksel', 'value')]
)
def update_histograms(combo_id):

    location = combo_id.split(' ')[1]
    start_date = combo_id.split(' ')[3]
    end_date = combo_id.split(' ')[5]
    
    filtered_df = df[(df['location'] == location) & (df['startdate'] == start_date) & (df['enddate'] == end_date)]

    mean = filtered_df['mean'].iloc[0]
    median = filtered_df['median'].iloc[0]
    std = filtered_df['std'].iloc[0]

    histograms = []
        
    trace = go.Bar(
        x = filtered_df.columns[6:-1],
        y = filtered_df.iloc[0, 6:-1].to_list()
    )

    layouts = go.Layout(
        title=f'{location} {start_date} {end_date}',
        xaxis=dict(title=f'Vekt første aksel<br><span style="font-size:12px;">Snitt: {mean:.2f} | Median: {median:.2f} | standardavvik: {std:.2f}</span>'),
        yaxis=dict(title='Antall'),
        bargap=0.1,
        bargroupgap=0.1,
        width=None, 
        height=500  
    )

    fig = go.Figure(data=[trace], layout=layouts)

    histogram = dcc.Graph(
        id=f'Histogram-{uuid4()}',
        figure=fig
    )

    histograms.append(html.Div(histogram, style={'width': '33%', 'display': 'inline-block'}))

    return histograms
