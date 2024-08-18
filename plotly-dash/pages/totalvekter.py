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
relative_path = 'resultater\\totalvekter.csv'
file_path = os.path.join(current_dir, relative_path)
fil

df = pd.read_csv(file_path)
df['combo_id'] = "Sted: " + df['location'] + " startdato: " + df['startdate'] + " sluttdato: " + df['enddate']

df_per_place

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Overordnet, totalvekter', order=2),
                html.Br(),
                dmc.Title("Motivasjon bak statistikken", order=4),
                dmc.Text("""
                    Hovedbidraget til nedbrytning av veger kommer fra tunge aksellaster, som er direkte knyttet til kjøretøyets totale vekt.
                    Ved å ha en totalvekt-oversikt for tunge kjøretøy danner man et grunnlag for å forstå hvordan kjøretøyets totale vekt bidrar til nedbrytningen. 
                """, size="lg"),
                dmc.Title("Fremgangsmåte", order=4),
                dmc.Text("""
                    På Ånestad, Øysand, Verdal, og Skibotn er det installert såkalte Kistler-sensorer. 
                    Dette er sensorer som er gravd ned i bakken, og registrer trafikken som kjører over de. 
                    Registreringene gir blant annet innblikk i kjøretøyets vekt, antall akslinger, og vektfordelingen over de ulike akslingene. 
                    Resultatene her baserer seg på den totale vekten av kjøretøy som går under kategorien 'tunge kjøretøy'.
                """, size="lg"),
                html.Br()
            ],
        ),

        dmc.Paper( # samlet, for hvert sted
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Totalvekter', order=2),

                html.Br(),

                dmc.Text("""
                    Hovedbidraget til nedbrytning av veger kommer fra tunge aksellaster, som er direkte knyttet til kjøretøyets totale vekt.
                    Ved å ha en totalvekt-oversikt for tunge kjøretøy danner man et grunnlag for å forstå hvordan kjøretøyets totale vekt bidrar til nedbrytningen. 
                """, size="lg"),

                html.Br(),

                dcc.Dropdown(
                    id='combo_dropdown_totalvekter',
                    options=[{'label': combo, 'value': combo} for combo in df_per_place['combo_id'].unique()],
                    value=df['combo_id'].iloc[0],  # Default value
                    style={'width': '100%'}
                ),
                    
                html.Div(id='histograms_container_totalvekter', style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'}),

                html.Br()
            ],
        ),

        dmc.Paper( #
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Totalvekter', order=2),

                html.Br(),

                dmc.Text("""
                    Hovedbidraget til nedbrytning av veger kommer fra tunge aksellaster, som er direkte knyttet til kjøretøyets totale vekt.
                    Ved å ha en totalvekt-oversikt for tunge kjøretøy danner man et grunnlag for å forstå hvordan kjøretøyets totale vekt bidrar til nedbrytningen. 
                """, size="lg"),

                html.Br(),

                dcc.Dropdown(
                    id='combo_dropdown_totalvekter',
                    options=[{'label': combo, 'value': combo} for combo in df['combo_id'].unique()],
                    value=df['combo_id'].iloc[0],  # Default value
                    style={'width': '100%'}
                ),
                    
                html.Div(id='histograms_container_totalvekter', style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'}),

                html.Br()
            ],
        ),

        dmc.Paper( #
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Sammenlikning med svenske verdier', order=2),

                html.Br(),

                dmc.Text("""
                    Sammenlikning med tilsvarende svenske verdier.
                """, size="lg"),

                html.Div([
                    dmc.Image(
                        src="/assets/bk1.png",  # URL of the image
                        alt="bk1",  # Alt text for the image
                        radius="md",  # Optional: radius for rounded corners
                        style={"width": "50%", "height": "auto", "margin": "10px"}
                    ),


                    dmc.Image(
                        src="/assets/bk4.png",  # URL of the image
                        alt="bk4",  # Alt text for the image
                        radius="md",  # Optional: radius for rounded corners
                        style={"width": "50%", "height": "auto", "margin": "10px"}
                    ),
                ], style={'display': 'flex', 'flex-direction': 'row'}),

                html.Br(),

            ],
        ),

        html.Br(),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    Output('histograms_container_totalvekter', 'children'),
    [Input('combo_dropdown_totalvekter', 'value')]
)
def update_histograms(combo_id):

    location = combo_id.split(' ')[1]
    start_date = combo_id.split(' ')[3]
    end_date = combo_id.split(' ')[5]
    
    filtered_df = df[(df['location'] == location) & (df['startdate'] == start_date) & (df['enddate'] == end_date)]

    histograms = []

    trace = go.Bar(
        x = filtered_df.columns[3:-1],
        y = filtered_df.iloc[0, 3:-1].to_list()
    )

    layouts = go.Layout(
        title=f'{location} {start_date} {end_date}',
        xaxis=dict(title='Vekt'),
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

    histograms.append(html.Div(histogram, style={'width': '90%'}))

    return histograms
