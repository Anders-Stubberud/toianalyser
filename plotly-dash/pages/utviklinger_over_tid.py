import os
import json
import utils
import pickle
import random
import pandas as pd
import polars as pl
import plotly.express as px
from dash import dcc, html, dash_table
import plotly.graph_objects as go
from pyproj import CRS, Transformer
from shapely.ops import unary_union
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
from dash import dcc, html, callback, Input
from shapely.geometry import Polygon, MultiPolygon, Point

current_dir = os.path.dirname(os.path.abspath(__file__))
path_utviklinger_over_tid = os.path.join(current_dir, '..', '..', 'resultater', 'utviklinger over tid')
path_utviklinger_2022 = os.path.join(current_dir, '..', '..', 'resultater', 'videreutvikling statistikk 2022')
FORDELING_TURER_MED_VEKT = 'fordeling turer med vekt'
UTVIKLING_KAPASITETSUTNYTTELSE = 'utvikling kapasitetsutnyttelse'
UTVIKLING_MAKSIMAL_KJØREVEKT = 'utvikling maksimal kjørevekt'

# region Lager 'fig': kart som viser oversikt over de ulike seksjonene
source_crs = CRS.from_epsg(32633)
target_crs = CRS.from_epsg(4326)
transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'LINX-data', 'selected_kommuner.json')
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

file_path_sections = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'LINX-data', 'sections.pkl')
with open(file_path_sections, 'rb') as file:
    sections = pickle.load(file)
    area_to_section = {value: key for key, values in sections.items() for value in values}

section_polygons = {}

def random_rgba_color(base_color, variation=0):
    """Generate a random RGBA color with slight variation from base color."""
    base_r, base_g, base_b = base_color
    r = min(255, max(0, int(base_r + random.uniform(-variation * 255, variation * 255))))
    g = min(255, max(0, int(base_g + random.uniform(-variation * 255, variation * 255))))
    b = min(255, max(0, int(base_b + random.uniform(-variation * 255, variation * 255))))
    a = round(random.uniform(0.3, 0.35), 2)
    return f"rgba({r},{g},{b},{a})"

def find_point_within_polygon(polygon):
    """Find a point within a polygon (ensures marker stays within)."""
    if isinstance(polygon, MultiPolygon):
        for poly in polygon.geoms:
            centroid = poly.centroid
            if poly.contains(centroid):
                return centroid.x, centroid.y
    else:
        centroid = polygon.centroid
        if polygon.contains(centroid):
            return centroid.x, centroid.y
    for point in polygon.exterior.coords:
        if polygon.contains(Point(point)):
            return point[0], point[1]
    return polygon.exterior.coords[0]

for feature in data['features']:
    area_name = feature['properties'].get('n')
    section_name = area_to_section.get(area_name, 'Unknown')

    coords = feature['geometry']['coordinates'][0]
    lon_lat_coords = [transformer.transform(coord[0], coord[1]) for coord in coords]

    if section_name not in section_polygons:
        section_polygons[section_name] = []

    section_polygons[section_name].append(lon_lat_coords)

fig = go.Figure()

for section_name, polygons in section_polygons.items():

    combined_polygon = unary_union([Polygon(p) for p in polygons])

    center_lon, center_lat = find_point_within_polygon(combined_polygon)

    if isinstance(combined_polygon, MultiPolygon):
        lon_lat_coords = [list(p.exterior.coords) for p in combined_polygon.geoms]
    else:
        lon_lat_coords = [list(combined_polygon.exterior.coords)]

    lon = [coord[0] for coords in lon_lat_coords for coord in coords] + [lon_lat_coords[0][0][0]]
    lat = [coord[1] for coords in lon_lat_coords for coord in coords] + [lon_lat_coords[0][0][1]]

    base_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    section_color = f"rgba(200, 200, 200, 0.15)"

    fig.add_trace(go.Scattermapbox(
        mode = "lines+markers",
        lon = lon,
        lat = lat,
        fill = "toself",
        fillcolor = section_color,
        line=dict(color='black', width=5),
        name=section_name
    ))

    for feature in data['features']:
        area_name = feature['properties'].get('n')
        if area_to_section.get(area_name) == section_name:
            coords = feature['geometry']['coordinates'][0]
            lon_lat_coords = [transformer.transform(coord[0], coord[1]) for coord in coords]
            if len(lon_lat_coords) > 0:
                lon_area = [coord[0] for coord in lon_lat_coords] + [lon_lat_coords[0][0]]
                lat_area = [coord[1] for coord in lon_lat_coords] + [lon_lat_coords[0][1]]
                area_color =  f"rgba(200, 200, 200, 0.15)" #random_rgba_color(base_color, variation=0.3)  # Slightly different color

                fig.add_trace(go.Scattermapbox(
                    mode = "lines+markers",
                    lon = lon_area,
                    lat = lat_area,
                    fill = "toself",
                    fillcolor = area_color,
                    line=dict(color=area_color, width=1),
                    name=area_name,
                    hoverinfo='name',
                    textposition='top center',
                    textfont=dict(size=10),
                    showlegend=False
                ))

    fig.add_trace(go.Scattermapbox(
        mode = "markers+text",
        lon = [center_lon],
        lat = [center_lat],
        marker=dict(size=10, color='black'),
        text=[{
            'section1': 'seksjon 1',
            'section2': 'seksjon 2',
            'section3': 'seksjon 3',
            'section4': 'seksjon 4'
        }[section_name]],
        textfont=dict(size=15),
        textposition='top center',
        showlegend=False
    ))

fig.update_layout(
    mapbox = {
        'style': "open-street-map",
        'center': {'lon': center_lon, 'lat': center_lat},
        'zoom': 6,
    },
    margin = {'l':0, 'r':0, 'b':0, 't':0},
    showlegend=False
)
# endregion

# region Fig's for videreutvikling fra 2022
def display_2022_property(df: pd.DataFrame):
    # Filter out columns with '2024'
    df = df[[col for col in df.columns if '2024' not in col]]
    
    df_copy = df.copy()

    # Add the 'Snitt alle år' column to the copy
    df_copy['Snitt alle år'] = df_copy[['Snitt 2021', 'Snitt 2022', 'Snitt 2023']].mean(axis=1)
    
    cols_order = [col for col in df_copy.columns if col != 'Snitt alle år'] 
    cols_order.insert(cols_order.index('Snitt 2023') + 1, 'Snitt alle år')
    df_copy = df_copy[cols_order] 

    # Perform the melt operation
    df_long = df_copy.melt(id_vars=['Ekvipasje'], 
                      value_vars=[col for col in df.columns if 'Snitt' in col],
                      var_name='Year', 
                      value_name='Value')

    df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})')

    fig = go.Figure()
    for ekvipasje in df_long['Ekvipasje'].unique():
        df_ekvipasje = df_long[df_long['Ekvipasje'] == ekvipasje]
        fig.add_trace(go.Scatter(
            x=df_ekvipasje['Year'],
            y=df_ekvipasje['Value'],
            mode='lines+markers',
            name=ekvipasje
        ))

    fig.update_layout(
        xaxis_title='År',
        yaxis_title='Snitt',
        xaxis=dict(type='category')
    )

    # DataTable for displaying the original DataFrame
    table = dash_table.DataTable(
        id='table_n_påvirkning_klassifisering',
        columns=[{"name": i, "id": i} for i in df_copy.columns],
        data=df_copy.round(2).to_dict('records'),
        sort_action='native',
        filter_action='native',
        page_action='native',
        style_table={'overflowX': 'auto', 'maxWidth': '100%'},

        style_cell={
            'width': '100px',
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

    # Map divisors to the 'Ekvipasje' column
    divisors = {
        '3-akslet trekkvogn med 4-akslet tilhenger': 60,
        '3-akslet trekkvogn med 5-akslet tilhenger': 65,
        '4-akslet trekkvogn med 4-akslet tilhenger': 68,
        '4-akslet trekkvogn med 5-akslet tilhenger': 74
    }

    df_copy = df.copy()

    # Add the 'Divisor' column to the copy using map
    df_copy['Divisor'] = df_copy['Ekvipasje'].map(divisors)

    # Divide the relevant columns by the 'Divisor'
    columns_to_divide = ['Snitt 2021', 'Snitt 2022', 'Snitt 2023']
    df_per_tonn = df_copy.copy()[['Ekvipasje', 'Snitt 2021', 'Snitt 2022', 'Snitt 2023', 'Divisor']]
    df_per_tonn[columns_to_divide] = df_per_tonn[columns_to_divide].div(df_per_tonn['Divisor'], axis=0)
    df_per_tonn['Gjennomsnitt per tonn'] = df_per_tonn[columns_to_divide].mean(axis=1)

    # Drop the 'Divisor' column
    df_per_tonn = df_per_tonn.drop(columns='Divisor')

    # DataTable for displaying the calculated DataFrame
    table_tonnage = dash_table.DataTable(
        id='table_n_påvirkning_klassifisering',
        columns=[{"name": i, "id": i} for i in df_per_tonn.columns],
        data=df_per_tonn.round(5).to_dict('records'),
        sort_action='native',
        filter_action='native',
        page_action='native',
        style_table={'overflowX': 'auto', 'maxWidth': '100%'},

        style_cell={
            'width': '100px',
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

    return fig, table, table_tonnage

def card_2022_property(fig=None, tab1=None, tab2=None, title=None, text1='', text2='Vi velger så å sette gjennomsnittet opp mot antall tonn som lastes. Dette gir følgende verdier:', text3=''):
    return dmc.Paper(
        radius="md",
        withBorder=True,
        shadow='xs',
        style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
        children=[
            html.Div([
                dmc.Title(title, order=2),
                html.Br(),
                dcc.Graph(figure=fig),
                dmc.Text(text1, size="lg"),
                html.Br(),
                tab1,
                html.Br(),
                dmc.Text(text2, size="lg"),
                html.Br(),
                tab2,
                html.Br(),
                dmc.Text(text3, size="lg"),
            ])
        ]
    )

df_videreutvikling_2022_adblue = pd.read_csv(os.path.join(path_utviklinger_2022, 'adblue.csv'))
df_videreutvikling_2022_c02 = pd.read_csv(os.path.join(path_utviklinger_2022, 'co2.csv'))
df_videreutvikling_2022_snittforbruk_kjøring = pd.read_csv(os.path.join(path_utviklinger_2022, 'snittforbruk kjøring.csv'))
df_videreutvikling_2022_snittforbruk_totalt = pd.read_csv(os.path.join(path_utviklinger_2022, 'snittforbruk totalt.csv'))
df_videreutvikling_2022_snittforbruk = pd.read_csv(os.path.join(path_utviklinger_2022, 'snittforbruk.csv'))
df_videreutvikling_2022_snitthastighet = pd.read_csv(os.path.join(path_utviklinger_2022, 'snitthastighet.csv'))

fig_adblue, table_adblue, table_tonnage_adblue = display_2022_property(df_videreutvikling_2022_adblue)
fig_co2, table_co2, table_tonnage_co2 = display_2022_property(df_videreutvikling_2022_c02)
fig_snittforbruk_kjoring, table_snittforbruk_kjoring, table_tonnage_kjoring = display_2022_property(df_videreutvikling_2022_snittforbruk_kjøring)
fig_snittforbruk_totalt, table_snittforbruk_totalt, table_tonnage_totalt = display_2022_property(df_videreutvikling_2022_snittforbruk_totalt)
fig_snittforbruk, table_snittforbruk, table_tonnage_snittforbruk = display_2022_property(df_videreutvikling_2022_snittforbruk)
fig_snitthastighet, table_snitthastighet, table_tonnage_snitthastighet = display_2022_property(df_videreutvikling_2022_snitthastighet)
# endregion

def layout():
    return html.Div([

        dmc.Paper( # Overordnet informasjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Overordnet, utviklinger over tid', order=2),
                html.Br(),
                dmc.Title("Motivasjon bak statistikken", order=4),
                dmc.Text("""
                    Under prosjektet har de sensor-utstyrte tømmervogntogene hovedsakelig utfoldet seg i visse seksjoner, som er oppført nedenfor.
                    Ved å opprette separat statistikk for samtlige kombinasjoner av ekviapasjer og seksjoner, åpner man opp for muligheten til 
                    å oppdage sammenhenger mellom ekvipasjenes trafikk og faktorer som vegslitasje, utslipp, etc
                """, size="lg"),
                dmc.Title("Fremgangsmåte", order=4),
                dmc.Text("""
                    Resultatene har blitt funnet ved å sammenstille 2 ulike datakilder: kjøretøysdata og posisjonsdata.
                    Kjøretøysdataen inneholder informasjon om hver enkelt tur tilbakelagt av hvert individuelle kjøretøy som deltar i prøveprosjektet.
                    Dette inkluderer data som blant annet VIN-nummeret til kjøretøyet, dato for turen, tilbakelagt distanse, og vekt under full last.
                    Posisjonsdataen inneholder hovedsakelig tidsstemplinger sammen med VIN-nummer, lengde- og breddegrad. 
                    Ettersom kjøretøysdataen ikke gir uttrykk for hvor kjøretøyet har kjørt med full last, og posisjonsdataen ikke gir uttrykk for vekt på gitt posisjon,
                    så har problemet blitt noe forenklet. Det har blitt antatt at kjøretøyets last under hele turen tilsvarer den maksimale oppførte vekten fra kjøretøysdataen,
                    og at kjøretøyet kjørte rundt med denne lasten i ruten som blir dannet av lengde/breddegradsparene fra posisjonsdaten for kombinasjonen av kjøretøyets VIN-nummer
                    og datoen som er oppført i kjøretøysdataen.
                    Kombinasjonen av ekvipasjen kjøretøyet tilhører og seksjonene kjøretøyet har kjørt gjennom danner dermed statistikk basert på de tilhørende dataene fra kjøretøysdataen.
                """, size="lg"),
                html.Br()
            ],
        ),

        dmc.Paper( # Dropwdowns for ekipasje og seksjon
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Velg ekvipasje og område', order=2),
                html.Br(),
                dmc.Text("Velg ekvipasje og område for statistikk.", size="lg"),
                html.Br(),
                html.Div([
                    dmc.Text('Viser nå informasjon for', size='lg'),
                    dmc.Title(id='valgt_ekvipasje', order=4, style={'padding-left': '8px', 'padding-right': '8px'}),
                    dmc.Text('innenfor området', size='lg'),
                    dmc.Title(id='valgt_seksjon', order=4, style={'padding-left': '8px', 'padding-right': '8px'})
                ], style={'display': 'flex'}),
                html.Div([ # selve dropdownene
                    dcc.Dropdown(
                        id='ekvipasje_utvikling_over_tid_dropdown',
                        options=[{'label': ekvipasje, 'value': ekvipasje} for ekvipasje in (
                            '3-akslet trekkvogn med 4-akslet tilhenger',
                            '3-akslet trekkvogn med 5-akslet tilhenger',
                            '4-akslet trekkvogn med 4-akslet tilhenger',
                            '4-akslet trekkvogn med 5-akslet tilhenger',
                        )],
                        placeholder='Velg ekvipasje',
                        style={'flex': '1'}
                    ),

                    dcc.Dropdown(
                        id='seksjon_utvikling_over_tid_dropdown',
                        options=[{'label': seksjon, 'value': seksjon} for seksjon in (
                            'seksjon 1',
                            'seksjon 2',
                            'seksjon 3',
                            'seksjon 4'
                        )],
                        placeholder='Velg seksjon',
                        style={'flex': '1'}
                    ),
                ], style={'width': '100%', 'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'}),
    
                html.Br(),
                dmc.Text("De ulike ekvipasjene har følgende lastgrenser:", size="lg"),
                dmc.List(
                    [
                        dmc.ListItem("3-akslet trekkvogn med 4-akslet tilhenger: 60 tonn"),
                        dmc.ListItem("3-akslet trekkvogn med 5-akslet tilhenger: 65 tonn"),
                        dmc.ListItem("4-akslet trekkvogn med 4-akslet tilhenger: 68 tonn"),
                        dmc.ListItem("4-akslet trekkvogn med 5-akslet tilhenger: 74 tonn"),
                    ]
                ),
                dmc.Text("Seksjonene består av følgende kommuner:", size="lg"),
                dmc.List(
                    [
                        dmc.ListItem("Seksjon 1: Stor-Elvdal og Åmot"),
                        dmc.ListItem("Seksjon 2: Hamar og Løten"),
                        dmc.ListItem("Seksjon 3: Trysil og Elverum"),
                        dmc.ListItem("Seksjon 4: Våler, Åsnes, og Grue"),
                    ]
                ),
                html.Br(),
                
                html.Div([
                    dcc.Graph(figure=fig, style={'height': '50vh'})
                ])
            ]),
    
        dmc.Paper( # lineplot snitt kjørevekt
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Utvikling i gjennomsnittlig maksimal kjørevekt over tid', order=2),
                html.Br(),
                dmc.Text("""
                    Følgende plot viser ekvipasjens utvikling i gjennomsnittlig maksimal kjørevekt innenfor spesifisert seksjon over tid. 
                """, size="lg"),
                dmc.Text("""
                    Maksimal kjørevekt er vekten kjøretøyet hadde når gods ble fraktet, og ekskluderer dermed eksempelvis transportetapper uten gods.  
                """, size="lg"),
                dmc.Text("""
                    Motivasjonen bak plot'et er å få et inntrykk av hvordan vogntogenes last endrer seg gjennom sesongene. 
                """, size="lg"),
                html.Br(),
                html.Div(id='snitt_kjørevekt_ekvipasje')
            ]
        ),

        dmc.Paper( # lineplot kapasitetsutnyttelse
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Utvikling i kapasitetsutnyttelse for ekvipasje innenfor seksjon', order=2),
                html.Br(),
                dmc.Text("""
                    Plot'et viser snittet av kapasitetsutnyttelsen innad i ekvipasjen for spesifisert seksjon.
                """, size="lg"),
                dmc.Text("""
                    Kapasitetsutnyttelse uttrykkes her som en prosent, og er beregnet som snittet av vogntogets fullastede vekt over maksimal tillat vekt, ganget med 100.
                """, size="lg"),
                dmc.Text("""
                    Motivasjonen bak plottet er å se til hvilken grad de ulike ekvipasjene i prøveprosjektet utnytter kapasiteten sin.
                """, size="lg"),
                html.Br(),
                html.Div(id='kapasitetsutnyttelse_ekvipasje')
            ]
        ),
        
        dmc.Paper( # histogram turer med vekt
            radius="md", # or p=10 for border-radius of 10px
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title('Oversikt antall turer innad i vekt-intervaller', order=2),
                dmc.Text("""
                    Histogrammet viser det totale antallet tilbakelagte kjøreturer for ulike vekt-intervaller, for valgt ekvipasje og seksjon.  
                """, size="lg"),
                dmc.Text("""
                    Motivasjonen bak histogrammet er å få et innblikk hvilken last de ulike ekvipasjene velger å benytte seg av innad i de ulike seksjonene. 
                """, size="lg"),
                html.Br(),
                html.Div(id='turer_med_vekt_ekvipasje')
            ]
        ),
        
        card_2022_property( # adblue
            fig=fig_adblue, 
            tab1=table_adblue, 
            tab2=table_tonnage_adblue, 
            title="Analyse av AdBluesnitt (l/mil)",
            text1="""
            Dersom man tar utgangspunkt i gjennomsnittet, ser man at 65 tonn (3 + 5 ekvipasjen) bruker 80% av det 74 tonnskjøretøyet bruker. Til sammenligning bruker 68 tonn 92% av det 74 tonn bruker. 

            Det er vanskelig å få noe konkret ut av dette, men det tyder på at det generelt er noe høyere forbruk på 74 tonn.  

            Det er verdt å undersøke om hvorfor 60 tonnskjøretøyet har markant høyere verdier enn resten av kjøretøyene. 
            """,
            text3="Her kommer altså 65 tonns konfigurasjonen best ut. "
        ),

        card_2022_property( # snittforbruk totalt
            fig=fig_snittforbruk_totalt, 
            tab1=table_snittforbruk_totalt, 
            # table_tonnage_totalt, # de har den ikke med i 2022 rapporten, så utelater den
            title="Analyse av Snittforbruk totalt (l/mil)",
            text1="""
            Disse dataene inneholder også data på når lastebilen står i ro. 
            Dette er mindre relevant og det velges derfor å ikke kommentere dataene over. 
            """,
            text2=''
        ),

        card_2022_property( # snittforbruk kjøring
            fig=fig_snittforbruk_kjoring, 
            tab1=table_snittforbruk_kjoring, 
            tab2=table_tonnage_kjoring, 
            title="Analyse av Snittforbruk kjøring (l/mil)",
            text1="""
            Generelt er det en lineær trend i totalvekt kontra forbruk. Det som imidlertid er litt spesielt, er at tømmervogntogene på 65 tonn har et noe høyere forbruk enn 68 tonn. Dette er noe som bør undersøkes. 

            Dersom man tar utgangspunkt i gjennomsnittet, ser man at 68 tonn bruker 85.22% av det 74 tonnskjøretøyet bruker, 65 tonn breuker 89% av det 74 tonn bruker, og 60 tonn kommer inn på 84.69%                 
            """,
            text3="""
            Her kommer altså 68 tonns konfigurasjonen best ut. 
            Det er verdt å merke seg at det er en viss usikkerhet i om flere av tømmervogntogene i Dag Skjølaas liste faktisk kjører med 65 tonn, 
            da de ikke har dispensasjon og det finnes for dårlige vektmålingsdata til å fastslå dette. 
            Det er også interessant at 68 tonn kommer bedre ut enn 74 tonn.         
            """
        ),

       card_2022_property( # snitthastighet
            fig=fig_snitthastighet, 
            tab1=table_snitthastighet, 
            # table_tonnage_snitthastighet, # ikke med i 2022 rapporten
            title="Analyse av Snitthastighet",
            text1="""
            Det er interessant at gjennomsnittshastigheten øker når kjøretøyene blir tyngre. 
            Det er også en trend at de lettere kjøretøyene har en høyere makshastighet. 
            For å trekke en konklusjon her er det nødvendig å gå ned på et høyere detaljnivå. 
            """,
            text2=''
        ),

        card_2022_property( # co2
            fig=fig_co2, 
            tab1=table_co2, 
            tab2=table_tonnage_co2, 
            title="Analyse av CO2 snitt (kg/km)",
            text1="""
            Basert på det totale utslippet er det en trend at tyngre kjøretøy slipper ut større mengder Co2, hvilket ikke er uventet. 

            Dersom man tar utgangspunkt i gjennomsnittet, så slipper 60 tonn ut 84.11% av 74 tonn, 65 tonn kommer inn på 82.78%, og 68 tonn på 89.4%.     
            """,
            text3="""
            Her kommer altså 65 tonns konfigurasjonen best ut. 
            Det er verdt å merke seg at det er en viss usikkerhet i om flere av tømmervogntogene i Dag Skjølaas 
            liste faktisk kjører med 65 tonn, da de ikke har dispensasjon og det finnes for dårlige vektmålingsdata 
            til å fastslå dette. Det er også interessant at det er forholdvis liten forskjell på tvers av konfigurasjonene.            
            """
        ),

        card_2022_property( # snittforbruk
            fig=fig_snittforbruk, 
            tab1=table_snittforbruk, 
            tab2=table_tonnage_snittforbruk, 
            title="Analyse av Snittforbruk (l/time)",
            text1="""
            Generelt er det en trend for at tyngre kjøretøy har et høyere snittforbruk. Imidlertid er det spesielt at 65 og 68 tonns konfigurasjonene har økt forbruket sitt drastisk over årene. Dette burde undersøkes nærmere. 

            Det er verdt å merke seg at tomgangskjøring er med i tallene som denne delen av analysen bygger på. 
            """,
            text3="""
            Her kommer altså 68 tonns konfigurasjonen best ut. 
            Det er verdt å merke seg at det er en viss usikkerhet i om flere av tømmervogntogene i Dag Skjølaas liste faktisk kjører med 65 tonn, 
            da de ikke har dispensasjon og det finnes for dårlige vektmålingsdata til å fastslå dette. 
            """
        ),

        html.Br(),

        # dmc.Paper( # Lag matrise her
        #     radius="md",
        #     withBorder=True,
        #     shadow='xs',
        #     style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
        #     children=[
        #         dmc.Title('Matrise', order=2),
        #         dmc.Text("""
        #             Info om hvordan valgmatrise fungerer. 
        #         """, size="lg"),
        #     ]
        # ),

        # html.Br(),

        

    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)

@callback(
    [
        Output('snitt_kjørevekt_ekvipasje', 'children'),
        Output('kapasitetsutnyttelse_ekvipasje', 'children'),
        Output('turer_med_vekt_ekvipasje', 'children'),
        Output('valgt_ekvipasje', 'children'),
        Output('valgt_seksjon', 'children'),
    ],
    [
        Input('ekvipasje_utvikling_over_tid_dropdown', 'value'),
        Input('seksjon_utvikling_over_tid_dropdown', 'value')
    ]
)
def oppdater_utviklinger(valgt_ekvipasje, valgt_seksjon):
    ekvipasje = valgt_ekvipasje if valgt_ekvipasje else '4-akslet trekkvogn med 4-akslet tilhenger'
    seksjon = valgt_seksjon if valgt_seksjon else 'seksjon 3'

    seksjon_filename = { # litt hatløsning men skitt au
        'seksjon 1': 'section1',
        'seksjon 2': 'section2',
        'seksjon 3': 'section3',
        'seksjon 4': 'section4'
    }[seksjon]

    # region maksimal kjørevekt
    df_maksimal_kjørevekt = pl.read_csv(os.path.join(path_utviklinger_over_tid, f'{UTVIKLING_MAKSIMAL_KJØREVEKT} {seksjon_filename} {ekvipasje}.csv'))
    df_maksimal_kjørevekt = df_maksimal_kjørevekt.with_columns(
        pl.concat_str([
            pl.col('År').cast(pl.Utf8), 
            pl.lit('-'), 
            pl.col('Måned').cast(pl.Utf8).str.zfill(2)
        ]).str.strptime(pl.Date, format="%Y-%m").alias('Date')
    )
    df_maksimal_kjørevekt = df_maksimal_kjørevekt.to_pandas()
    fig_maksimal_kjørevekt = px.line(df_maksimal_kjørevekt, x='Date', y='Snitt Max vekt')
    fig_maksimal_kjørevekt.update_layout(
        xaxis_title='Date',
        xaxis=dict(
            tickformat='%B %Y'
        )
    )
    snitt_kjørevekt_ekvipasje = dcc.Graph(figure=fig_maksimal_kjørevekt)
    # endregion

    # region kapasitetsutnyttelse
    df_kapasitetsutnyttelse = pl.read_csv(os.path.join(path_utviklinger_over_tid, f'{UTVIKLING_KAPASITETSUTNYTTELSE} {seksjon_filename} {ekvipasje}.csv'))
    df_kapasitetsutnyttelse = df_kapasitetsutnyttelse.with_columns(
        pl.concat_str([
            pl.col('År').cast(pl.Utf8), 
            pl.lit('-'), 
            pl.col('Måned').cast(pl.Utf8).str.zfill(2)
        ]).str.strptime(pl.Date, format="%Y-%m").alias('Date')
    )
    print(df_kapasitetsutnyttelse)
    df_kapasitetsutnyttelse = df_kapasitetsutnyttelse.to_pandas()
    # df_kapasitetsutnyttelse = df_kapasitetsutnyttelse[df_kapasitetsutnyttelse['VIN lastebil/tilhenger'] == df_kapasitetsutnyttelse.groupby('VIN lastebil/tilhenger')['Snitt kapasitetsutnyttelse'].mean().idxmax()]
    fig_kapasitetsutnyttelse = px.line(df_kapasitetsutnyttelse, x='Date', y='Snitt kapasitetsutnyttelse')
    kapasitetsutnyttelse_ekvipasje = dcc.Graph(figure=fig_kapasitetsutnyttelse)
    # endregion

    # region turer med vekt
    df_turer_med_vekt_pl = pl.read_csv(os.path.join(path_utviklinger_over_tid, f'{FORDELING_TURER_MED_VEKT} {seksjon_filename} {ekvipasje}.csv'))
    df_turer_med_vekt_pd = df_turer_med_vekt_pl.to_pandas()
    fig_turer_med_vekt = go.Figure()
    for _, row in df_turer_med_vekt_pd.iterrows():
        fig_turer_med_vekt.add_trace(go.Bar(
            x=[row['Bin Edge Start'], row['Bin Edge End']],
            y=[0, row['Count']],
            width=row['Bin Edge End'] - row['Bin Edge Start'],
            name=f'{row["Bin Edge Start"]}-{row["Bin Edge End"]}',
            orientation='v',
            showlegend=False
        ))
    fig_turer_med_vekt.update_layout(
        xaxis_title='Intervall av last, KG',
        yaxis_title='Antall kjørte turer',
        barmode='overlay',
        xaxis=dict(
            tickvals=df_turer_med_vekt_pd['Bin Edge Start'].tolist() + df_turer_med_vekt_pd['Bin Edge End'].tolist(),
            ticktext=[f'{int(row["Bin Edge Start"])}-{int(row["Bin Edge End"])}' for _, row in df_turer_med_vekt_pd.iterrows()],
            tickformat=','
        )
    )
    turer_med_vekt_ekvipasje = dcc.Graph(figure=fig_turer_med_vekt)
    # endregion

    return snitt_kjørevekt_ekvipasje, kapasitetsutnyttelse_ekvipasje, turer_med_vekt_ekvipasje, ekvipasje, seksjon
