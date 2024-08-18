from dash import html
import dash_mantine_components as dmc
import utils

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Overordnet, vegslitasje og WIM', order=2),
                html.Br(),
                dmc.Text("""
                    Arbeidet som er gjort her i forbindelse med WIM er supplerende beregninger for prosjektet til Leif Jørgen Bakløkk ved teknologi, drift, og vedlikehold.
                    Rapporten nedenfor er det foreløpige arbeidet per 2024-06-07, og gir detaljert innsikt i prosjektet. 
                """, size="lg"),
                html.Br()
            ],
        ),

        html.Br(),

        html.Iframe(
            src='/assets/Rapport WIM - Foreløpig versjon per 2024-06-07.pdf',
            style={
                'width': '100%',
                'height': '1000px',
                'border': 'none'
            }
        ),

        html.Br(),
    
    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

