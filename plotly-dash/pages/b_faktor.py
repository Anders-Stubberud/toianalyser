import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os
import dash_mantine_components as dmc
import plotly.express as px
from dash import callback
from uuid import uuid4
from datetime import datetime
import utils

current_dir = os.getcwd()
relative_path_kistler = 'resultater\\b-faktor_kistler.csv'
relative_path_bwim = 'resultater\\b-faktor_bwim.csv'
file_path_kistler = os.path.join(current_dir, relative_path_kistler)
file_path_bwim = os.path.join(current_dir, relative_path_bwim)

df_kistler = pd.read_csv(file_path_kistler)
df_bwim = pd.read_csv(file_path_bwim)
df = pd.concat((df_kistler, df_bwim))

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Overordnet om B-faktor og ESAL-fordeling', order=2),
                html.Br(),
                dmc.Title("Motivasjon bak statistikken", order=4),
                dmc.Text("""
                    I Sverige benyttes en såkalt 'B-faktor' som en indikator på vegslitasje. 
                    B-faktoren beregnes som snittet av ESAL-verdiene fra trafikken som har kjørt på vegen, hvorav ESAL-verdiene gir uttrykk for relativ nedbrytende effekt i forhold til en 10-tonns aksel. 
                    Ved å beregne B-faktoren dannes et grunnlag for å sammenlikne med tilsvarende verdier fra Sverige. 
                    Plot av ESAL-fordelingen gir et visuelt bilde av hvordan B-faktoren blir til, altså hvordan kjøretøy tilhørende ulike vektklasser bidrar til nedbrytningen av veien.
                """, size="lg"),
                dmc.Title("Fremgangsmåte", order=4),
                dmc.Text("""
                    På Ånestad, Øysand, Verdal, og Skibotn er det installert såkalte Kistler-sensorer. 
                    Dette er sensorer som er gravd ned i bakken, og registrer trafikken som kjører over de. 
                    Registreringene gir blant annet innblikk i kjøretøyets vekt, antall akslinger, og vektfordelingen over de ulike akslingene. 
                    Disse verdiene benyttes som parametre til de etablerte formlene som beregner ESAL-verdier og B-faktor. 
                """, size="lg"),
                html.Br()
            ],
        ),
        
        dmc.Paper( # B-faktor og ESAL-fordeling
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[

                dmc.Title('B-faktor og ESAL-fordeling', order=2),
                html.Br(),
                dmc.Text("""
                    Velg mellom B-faktor og ESAL-fordeling, samt stedet for statistikk. 
                """, size="lg"),

                html.Div([
                    dmc.Text('Viser nå informasjon for', size='lg'),
                    dmc.Title(id='mode_output', order=4, style={'padding-left': '8px', 'padding-right': '8px'}),
                    dmc.Text('innenfor området', size='lg'),
                    dmc.Title(id='place_output', order=4, style={'padding-left': '8px', 'padding-right': '8px'})
                ], style={'display': 'flex'}),

                html.Br(),

                html.Div([
                    dcc.Dropdown(
                        placeholder='Velg mellom utvikling i B-faktor eller ESAL-fordeling',
                        id='mode',
                        options=[{'label': mode, 'value': mode} for mode in ['ESAL-fordeling', 'Utvikling i B-faktor']],
                        style={'width': '100%', 'height': '200%'},
                        maxHeight=500
                    ),

                    dcc.Dropdown(
                        placeholder='Velg sted',
                        id='place',
                        options=[{'label': place, 'value': place} for place in df['location'].unique()],
                        style={'width': '100%', 'height': '200%'},
                        maxHeight=500
                    ),
                ], style={'display': 'flex', 'flex-direction': 'row'}),

                html.Div([
                    html.Div(id='histograms-container_b_factor_kistler', style={'display': 'flex', 'flex-wrap': 'wrap'}),
                    html.Div(id='idlegend', style={'margin-top': '10%'})
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}
                )
            ],
        ),

        html.Br(),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    [
        Output('histograms-container_b_factor_kistler', 'children'),
        Output('idlegend', 'children'),
        Output('mode_output', 'children'),
        Output('place_output', 'children')
    ],
    [
    Input('mode', 'value'),
    Input('place', 'value')
    ]
)
def update_histograms(valgt_modus, valgt_sted):

    mode = valgt_modus if valgt_modus is not None else 'Utvikling i B-faktor'
    place = valgt_sted if valgt_sted is not None else 'Verdal'

    ldf = df[df['location'] == place] if place is not None else df[df['location'] == 'Verdal']
    plots, legend = [], None

    if mode == 'ESAL-fordeling':

        for i in range(len(ldf)):

            startdate, enddate, bfactor = ldf.iloc[i, 1:4]

            trace = go.Bar(
                x = ldf.columns[4:],
                y = ldf.iloc[i, 4:].to_list()
            )

            layouts = go.Layout(
                title=f'ESAL-fordeling for {place} fra {startdate} til {enddate}',
                xaxis=dict(title=f'ESAL-verdi<br><span style="font-size:12px;">Tilhørende B-faktor: {bfactor:.2f}</span>'),
                yaxis=dict(title='Antall'),
                bargap=0.1,
                bargroupgap=0.1,
                width=None, 
                height=500  
            )

            fig = go.Figure(data=[trace], layout=layouts)

            histogram = dcc.Graph(
                id=f'Histogram-{place}-{i}',
                figure=fig
            )

            plots.append(histogram)

    # if mode == 'Utvikling i B-faktor' and place is not None:
    else:

        ldf = ldf.sort_values('startdate')

        startdates = ldf['startdate'].to_list()
        enddates = ldf['enddate'].to_list()
        bfactors = ldf['B-faktor'].to_list()

        x_line = []
        for start, end in zip(startdates, enddates):
            x_line.extend([start, end , None])

        y_line = []
        for b in bfactors:
            y_line.extend([b, b, None])
            
        season_colors = {
            'Vinter': 'rgba(0, 0, 255, 0.5)',    
            'Vår': 'rgba(173, 255, 47, 0.5)', 
            'Sommer': 'rgba(255, 0, 0, 0.5)',    
            'Høst': 'rgba(255, 100, 0, 0.5)'   
        }

        def generate_seasons(startdate, enddate):
            startyear, startmonth = int(startdate.split('-')[0]), int(startdate.split('-')[1])
            endyear, endmonth = int(enddate.split('-')[0]), int(enddate.split('-')[1])

            if 3 <= startmonth < 6:
                sm = 3
            elif 6 <= startmonth < 9:
                sm = 6
            elif 9 <= startmonth < 12:
                sm = 9
            else:
                sm = 12

            if 3 <= endmonth < 6:
                em = 3
            elif 6 <= endmonth < 9:
                em = 6
            elif 9 <= endmonth < 12:
                em = 9
            else:
                em = 12

            sy = startyear if not (1 <= startyear <= 2) else startyear - 1
            ey = endyear if not (1 <= endyear <= 2) else endyear - 1

            seasons = []

            for year in range(sy, ey + 1):

                for month in [3, 6, 9, 12]:

                    if (year == sy and month < sm) or (year == ey and month > em):
                        continue

                    start = datetime(year=year, month=month, day=1)
                    end = datetime(year=(year if month < 12 else year + 1), month=(month + 3 if month < 12 else 3), day=1)
                    season = 'Vår' if month == 3 else\
                             'Sommer' if month == 6 else\
                             'Høst' if month == 9 else\
                             'Vinter'
            
                    seasons.append((start, end, season))
            
            return seasons

        seasons = generate_seasons(startdates[0], enddates[-1])

        shapes = []
        for season in seasons:
            x0 = season[0]
            x1 = season[1]
            color = season_colors[season[2]]
            shapes.append(
                dict(
                    type='rect',
                    xref='x',
                    yref='paper',
                    x0=x0,
                    y0=0,
                    x1=x1,
                    y1=1,
                    fillcolor=color,
                    opacity=0.3,
                    line=dict(width=0)
                )
            )

        fig = go.Figure( # TODO få den bredere, typ 90%, driver bare å krymper og er rar når jeg setter width=90%
            data=[
                go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode="lines",
                    showlegend=False,
                    marker=dict(
                        color="black"
                    )
                ),
                go.Scatter(
                    x=startdates,
                    y=bfactors,
                    mode="markers",
                    name="måleperiode start",
                    marker=dict(
                        color="green",
                        size=10
                    )
                    
                ),
                go.Scatter(
                    x=enddates,
                    y=bfactors,
                    mode="markers",
                    name="måleperiode slutt",
                    marker=dict(
                        color="blue",
                        size=10
                    )   
                ),
            ],
            layout=go.Layout(
                title='Utvikling i B-faktor',
                xaxis=dict(title='Måleperioder'),
                yaxis=dict(title='B-faktor'),
                shapes=shapes, 
                height=500,
            ), 
        )

        line_plot = dcc.Graph(
            id=f'LinePlot-{uuid4()}',
            figure=fig,
        )

        plots.append(line_plot)

        legend_items = [
            html.Div(
                style={'display': 'flex', 'align-items': 'center', 'margin': '5px'},
                children=[
                    html.Div(style={'background-color': color, 'width': '20px', 'height': '20px', 'margin-right': '10px'}),
                    html.Span(season)
                ]
            ) for season, color in season_colors.items()
        ]

        legend = html.Div(
            children=legend_items,
            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start'}
        )

    return plots, legend, mode, place
