import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os
from dash import callback
import dash_mantine_components as dmc
import utils

current_dir = os.getcwd()
relative_path = 'resultater\\aksellastfordeling.csv'
file_path = os.path.join(current_dir, relative_path)

df = pd.read_csv(file_path)
df['combo_id'] = "Sted: " + df['location'] + " startdato: " + df['startdate'] + " sluttdato: " + df['enddate']

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title("Aksellastfordelinger fra WIM-installasjonene på Ånestad, Øysand, Skibotn, og Verdal", order=2),

                html.Br(),

                dmc.Text("""
                    Det er godt kjent at nedbrytningen av veier øker eksponentielt med akselvekten av kjøretøy.
                    I det siste har også nedbrytningen som følger av den såkalte 'pumpe-effekten' blitt mer fremtredende.
                    Dette baserer seg på at kjøretøy med flere akslinger pumper vannmassene som ligger i veiens underlag fremover, 
                    som kan forårsake strukturelle skader. 
                    Ved å studere sammenengen mellom aksellastfordelinger og nedbrytning av veg, vil man få et bedre grunnalg for å avgjøre hva som forårsaker slitasje. 
                """, size="lg"),

                html.Br(),
                
                dcc.Dropdown(
                    id='combo-dropdown',
                    options=[{'label': combo, 'value': combo} for combo in df['combo_id'].unique()],
                    value=df['combo_id'].iloc[0],  # Default value
                    style={'width': '100%', 'height': '200%'},
                    maxHeight=500
                ),

                html.Br(),

                html.Div(id='histograms-container', style={'display': 'flex', 'flex-wrap': 'wrap'})
            ],
        ),

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    Output('histograms-container', 'children'),
    [Input('combo-dropdown', 'value')]
)
def update_histograms(combo_id):

    location = combo_id.split(' ')[1]
    start_date = combo_id.split(' ')[3]
    end_date = combo_id.split(' ')[5]
    
    filtered_df = df[(df['location'] == location) & (df['startdate'] == start_date) & (df['enddate'] == end_date)]

    histograms = []

    for axle_group in ['Enkeltaksler', 'Boggiaksler', 'Trippelaksler']:
        
        trace = go.Bar(
            x = filtered_df.columns[6:-1],
            y = filtered_df[filtered_df['axlegroup'] == axle_group].iloc[0, 6:].to_list()
        )

        layouts = go.Layout(
            title=f'Aksellastfordeling for {axle_group}',
            xaxis=dict(title='Vekt, tonn'),
            yaxis=dict(title='Antall'),
            bargap=0.1,
            bargroupgap=0.1,
            width=None, 
            height=500  
        )

        fig = go.Figure(data=[trace], layout=layouts)

        histogram = dcc.Graph(
            id=f'Histogram-{axle_group}',
            figure=fig
        )

        histograms.append(html.Div(histogram, style={'width': '33%', 'display': 'inline-block'}))

    return histograms
