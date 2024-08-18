# region Imports
import os
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table, callback, Input
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
from .ekvipasjer.bil_og_henger import get_vehicle_combination_information
from .ekvipasjer.km_per_år_ekvipasje import ekvipasje_density_heatmap, ekvipasje_distance_years
import utils
# endregion

# region Konstanter
ekvipasjer = (
    '3-akslet trekkvogn med 4-akslet tilhenger',
    '3-akslet trekkvogn med 5-akslet tilhenger',
    '4-akslet trekkvogn med 4-akslet tilhenger',
    '4-akslet trekkvogn med 5-akslet tilhenger',
)

default_ekvipasje = ekvipasjer[-1]
EKVIPASJER_KM_WEIGHT_RIDES = 'ekvipasjer_distanse_vekt_turer'
DATAFRAMES_EKVIPASJE = 'dataframes_ekvipasje'
DENSITY_HEATMAP_COORIDNATES = 'koordinater_heatmap_'
CSV_EXTENSION = '.csv'
# endregion

# region Filstier
current_dir = os.path.dirname(os.path.abspath(__file__))

relative_path_results = os.path.join('..', '..', 'resultater')
# endregion

def layout():

    return html.Div([

        dmc.Paper( # Intro
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Kjøremønster', order=2),

                dmc.Text("""
                    Kjøremønsteret til prøveordningens kjøretøy kan bidra til å avdekke sammenhenger mellom økt tillat totalvekt og ulike hendelser med lokal påvirkning.
                    Eksempelvis danner det et grunnlag for å sammenlikne prøveordningens trafikk med trafikkulykker, dyrepåkjørsler, og slitasje på veier og broer.
                         
                    Resultatene har utelukkende blitt funnet ved bruk av posisjonsdataen. 
                """, size="lg", style={"white-space": "pre-line"}),
            ]
        ),

        html.Br(),

        html.Div([

            dmc.Paper( # heatmap
                radius="md",
                withBorder=True,
                shadow='xs',
                style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
                children=[
                    dmc.Title('Fordeling av trafikk', order=2),

                    dmc.Text("""
                    Kartet viser hvor trafikken tilhørende spesifisert ekvipasje fra prøveordningen har utartet seg. Sterkere farger (se stolpen til høyre) indikerer mer trafikk.    
                    Kartet har blitt laget ved å gruppere posisjonsdataen etter ekvipasjene de ulike kjøretøyene tilhører. 
                    Ved å spesifisere en ekvipasje lastes alle lengde- og breddegradspar for samtlige år tilhørende ekvipasjen opp i kartet.
                    """, size="lg", style={"white-space": "pre-line"}),

                    html.Br(),

                    dcc.Dropdown(
                        id='ekvipasje-dropdown-1',
                        options=[{'label': ekvipasje, 'value': ekvipasje} for ekvipasje in ekvipasjer],
                        placeholder=default_ekvipasje,
                    ),

                    html.Div(id='density_heatmap', style={'width': '100%', 'height': '75vh'})
                ]
            ),

            dmc.Paper(
                radius="md", # or p=10 for border-radius of 10px
                withBorder=True,
                shadow='xs',
                style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
                children=[
                    dmc.Title('Tilbakelagt distanse', order=2),
                    dmc.Text("""
                    Grafen viser utviklingen av samlet tilbakelagt distanse for ekvipasjen i løpet av prøveordningen. 
                    
                    Distansene har en viss feilmargin, da de er beregnet ved å summere distansene mellom etterfølgende lengde- og breddegradpar.
                    """, size="lg", style={"white-space": "pre-line"}),
                    html.Div([
                        html.Div(id='km-histogram', style={'width': '100%'}),
                    ], style={'display': 'flex'})
                ]
            ),

            # dmc.Paper( # 'dette er matchenee vi fant'
            #     radius="md", # or p=10 for border-radius of 10px
            #     withBorder=True,
            #     shadow='xs',
            #     style={'margin-top': '2vh', 'width': '100%'},
            #     children=[
            #         dmc.Title('"Dette er de matchene vi fant..."', order=2),
            #         dmc.Text("undertekst...", size="md"),
            #         html.Div(id='tables-container', style={'margin-top': '2%', 'width': '95%', 'margin-right': 'auto', 'margin-left': 'auto'}),
            #         html.Br(),
            #         # dcc.Dropdown(
            #         #     id='regnr_bil_regnr_henger',
            #         #     placeholder="Undersøk ekvipasje",
            #         # ),
            #         # dcc.Dropdown(
            #         #     id='undersøk-ekvipasje-date',
            #         #     placeholder="Dato for ekvipasje-søk",
            #         # ),
            #     ]
            # ),

        ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)  

@callback(
    [
        Output('density_heatmap', 'children'), 
        # Output('tables-container', 'children'),
        Output('km-histogram', 'children'),
        # Output('weight-histogram', 'children'),
        # Output('rides-histogram', 'children'),
    ],
    [Input('ekvipasje-dropdown-1', 'value')]
)#
def update_content(selected_ekvipasje):

    if selected_ekvipasje is None:
        selected_ekvipasje = default_ekvipasje

    dataframes = get_vehicle_combination_information(selected_ekvipasje)
    dataframes = [df[['Regnr_lastebil', 'VIN_lastebil', 'Regnr_tilhenger', 'VIN_tilhenger']] for df in dataframes]

    density_heatmap_coordinates_filepath = os.path.join(current_dir, relative_path_results, DENSITY_HEATMAP_COORIDNATES + selected_ekvipasje + CSV_EXTENSION)
    density_heatmap_coordinates = pd.read_csv(density_heatmap_coordinates_filepath)
    density_heatmap_coordinates = density_heatmap_coordinates.values.tolist()

    ekvipasjer_km_weight_rides_filepath = os.path.join(current_dir, relative_path_results, EKVIPASJER_KM_WEIGHT_RIDES + CSV_EXTENSION)
    ekvipasjer_km_weight_rides = pd.read_csv(ekvipasjer_km_weight_rides_filepath)
    ekvipasjer_km_weight_rides = ekvipasjer_km_weight_rides[ekvipasjer_km_weight_rides['Ekvipasje'] == selected_ekvipasje]

    try:
        mean_lat = sum(coord[0] for coord in density_heatmap_coordinates) / len(density_heatmap_coordinates)
        mean_lon = sum(coord[1] for coord in density_heatmap_coordinates) / len(density_heatmap_coordinates)
    except ZeroDivisionError:
        mean_lat = 60
        mean_lon = 10

    # region heatmap
    fig = px.density_mapbox(
        pd.DataFrame(density_heatmap_coordinates, columns=['Latitude', 'Longitude']),
        lat='Latitude',
        lon='Longitude',
        radius=3,
        center=dict(lat=mean_lat, lon=mean_lon),
        zoom=7,
        mapbox_style="open-street-map",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        mapbox=dict(
            style="open-street-map",
            zoom=7,
            center=dict(lat=mean_lat, lon=mean_lon)
        ),
    )

    heatmap_graph = dcc.Graph(figure=fig, style={'height': '90%'})
    # endregion

    # TODO kanskje legge inn en funksjon som lar bruker trykke på en bil+henger combo, deretter kan man vise på kartet med blått/rødt hvor bil/henger har kjørt?
    # region tabell
    tables = []
    for year, df in zip(range(2021, 2025), dataframes):
        tables.append(html.H5(f'Data for {year}'))
        tables.append(dash_table.DataTable(
            columns=[{"name": i.replace('_', ' '), "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_cell={
                'fontSize': 12,      # Smaller font size
                'padding': '5px',    # Less padding
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'center' # Center align text
            },
            style_table={
                'maxHeight': '300px',  # Limit table height
                'width': '100%',       # Adjust table width
                'minWidth': '100%',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'textAlign': 'center' # Center align header text
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)',
                }
            ],
        ))
    # endregion

    # region histogram km
    fig_km = px.line(
        ekvipasjer_km_weight_rides,
        x='år',
        y='distanse',
        markers=True,
        labels={'år': 'Year', 'distanse': 'Distance (km)'}
    )

    fig_km.update_layout(
        xaxis_title='År',
        yaxis_title='Distanse (km)',
        showlegend=True,
            xaxis=dict(
        tickmode='array',  # Use array mode to specify tick values
        tickvals=ekvipasjer_km_weight_rides['år'].unique(),  # Set tick values to unique years
        ticktext=[int(year) for year in ekvipasjer_km_weight_rides['år'].unique()]  # Format as integers
    ),
    )

    km_histogram = dcc.Graph(figure=fig_km)
    # endregion 

    # region histogram weight
    fig_weight = px.bar(
        ekvipasjer_km_weight_rides,
        x='år',
        y='vekt'
    )

    weight_histogram = dcc.Graph(figure=fig_weight)
    # endregion

    # region histogram rides 
    fig_rides = px.bar(
        ekvipasjer_km_weight_rides,
        x='år',
        y='turer'
    )

    rides_histogram = dcc.Graph(figure=fig_rides)
    # endregion

    return heatmap_graph, km_histogram