
from dash import dcc, html, callback, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

'''
Leser CSV-fil for hver vektklasse og legger til i dataframes

'''

# Globale konstanter for tomvekter (fra TØI rapport) og realsitiske vektgrenser for å filtrere bort ekstreme verdier
vehicle_empty_weight = {
    '74 tonn': 23405,
    '68 tonn': 22430,
    '65 tonn': 22757,
    '60 tonn': 21782
}

weight_limits = {'74 tonn': 80000, '68 tonn': 80000, '65 tonn': 75000, '60 tonn': 70000}

# Et datasett for hver ekvipasje 
def set_filename():
    file_paths = {
        '74 tonn': r'LINX-data\posisjonsdata\Filtrert_data\74_tonn.csv',
        '68 tonn': r'LINX-data\posisjonsdata\Filtrert_data\68_tonn.csv',
        '65 tonn': r'LINX-data\posisjonsdata\Filtrert_data\65_tonn.csv',
        '60 tonn': r'LINX-data\posisjonsdata\Filtrert_data\60_tonn.csv'
    }

    dataframes = {}

    for weight_class, file_path in file_paths.items():
        df = pd.read_csv(file_path, sep = ',', low_memory = False)
        df.columns = df.columns.str.strip()
        dataframes[weight_class] = df

    return dataframes

#Leser CSV-fil med statistikk for gjennomsnitt, max, min, osv
def read_statistics(weight_class):
    file_path = f'resultater\kapasitet\stats_{weight_class}.csv'
    return pd.read_csv(file_path)

dataframes = set_filename()

#Funskjon for å gjøre om VIN-nummer til regnummer for enklere avlesning
def find_regnr(vin):
    file_path = 'LINX-data\eiendelsrapport\Eiendelsrapport_20240705063004.csv'
    df = pd.read_csv(file_path, sep=';')
    match = df[df['VIN'] == vin]
    return match['Regnr'].values[0] if not match.empty else None

'''

Definerer layout i webgrensesnittet

'''

def layout():

    return html.Div([

        html.H1("Kapasitetsutnyttelse"),
        html.H2("Visualisering av aktuell vekt over tid"),
        dcc.Tabs(id='tabs', value='weight-tab', children=[
                dcc.Tab(label='Endring i vekt per dag', value='weight-tab', children=[
                    dcc.Slider(
                        id='date-slider',
                        min=0,
                        max=len(dataframes['74 tonn']['Dato'].unique()) - 1,
                        value=0,
                        marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(dataframes['74 tonn']['Dato'].unique())},
                        step=None
                    ),
                    html.Div(id='graphs-container'),
                ]),

                dcc.Tab(label='Statistikk', value='year-tab', children=[
                    dcc.Dropdown(id='year-dropdown'),
                    html.Div(id = 'yearly-stats-table')
                ]),

                dcc.Tab(label='Endring i vekt per år', value='stats-tab', children=[
                    dcc.Dropdown(id='year-dropdown-graphs'),
                    html.Div(id = 'yearly-graphs-container')
                ]),

            ]),
        ])

@callback(
    Output('graphs-container', 'children', allow_duplicate=True),
    [Input('tabs', 'value'),
     Input('date-slider', 'value')],
    prevent_initial_call=True
)

def update_graphs(active_tab, selected_date):
    if active_tab != 'weight-tab':
        return [],""
    
    date = list(dataframes['74 tonn']['Dato'].unique())[selected_date]
    graphs = []

    for weight_class, df in dataframes.items():
        df_filtered = df[df['Dato'] == date]
        if df_filtered.empty:
            continue

        fig = go.Figure()

        for vin in df_filtered['VIN'].unique():
            vin_data = df_filtered[df_filtered['VIN'] == vin].sort_values(by='Tid')
            fig.add_trace(go.Scatter (
                x = vin_data['Tid'],
                y = vin_data['Aktuell vekt'],
                mode = 'lines+markers',
                name = find_regnr(vin)
            ))

            fig.add_shape(
                x0=vin_data['Tid'].min(),
                x1=vin_data['Tid'].max(),
                type ='line',
                y0=weight_limits[weight_class],
                y1=weight_limits[weight_class],
                line=dict(color='Red', dash='dash'),
                name=f'Maksgrense {weight_class}'
            )

        fig.update_layout(
            title=f'Aktuell vekt for {weight_class} på {date}',
            xaxis_title='Tid',
            yaxis_title='Aktuell vekt (kg)',
            legend_title ='Regnr'
        )
        graphs.append(dcc.Graph(figure=fig, style={'height': '400px'}))
    
    return graphs

@callback(
    [Output('year-dropdown', 'options'),
    Output('year-dropdown', 'value')],
    Input('tabs', 'value'),
    prevent_initial_call = True
)

def update_year_dropdown(active_tab):
    if active_tab != 'year-tab':
        return [], None
    years = dataframes['74 tonn']['Dato'].apply(lambda x: x.year).unique()
    options = [{'label': str(year), 'value': year} for year in years]
    return options, options[0]['value']

@callback(
    Output('yearly-stats-table', 'children', allow_duplicate=True),
    [Input('year-dropdown', 'value')],
    prevent_initial_call=True
)
def update_yearly_stats_table(selected_year):
    weight_class_tables = []
    
    for weight_class in weight_limits.keys():
        stats_df = read_statistics(weight_class)
        stats_df = stats_df[stats_df['year'] == selected_year]
        weight_class_tables.append(html.Div([
            html.H3(f'{weight_class}'),
            dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in stats_df.columns],
                data=stats_df.to_dict('records')
            )
        ]))

    return weight_class_tables

@callback(
    [Output('year-dropdown-graphs', 'options'),
    Output('year-dropdown-graphs', 'value')],
    Input('tabs', 'value'),
    prevent_initial_call = True
)

def update_year_dropdown(active_tab):
    if active_tab != 'stats-tab':
        return [], None
    years = dataframes['74 tonn']['Dato'].apply(lambda x: x.year).unique()
    options = [{'label': str(year), 'value': year} for year in years]
    return options, options[0]['value']


@callback(
    Output('yearly-graphs-container', 'children', allow_duplicate=True),
     Input('year-dropdown-graphs', 'value'),
    prevent_initial_call=True
)

def update_yearly_graphs(selected_year):
    graphs = []
    
    for weight_class, df in dataframes.items():
        df_filtered = df[df['Dato'].apply(lambda x: x.year) == selected_year]
        if df_filtered.empty:
            continue

        empty_weight = vehicle_empty_weight[weight_class]
        df_filtered = df_filtered[df_filtered['Aktuell vekt'] > empty_weight + 5000]

        df_filtered['Måned'] = pd.to_datetime(df_filtered['Dato']).dt.to_period('M')
        df_grouped = df_filtered.groupby('Måned').agg({'Aktuell vekt': 'mean'}).reset_index()

        fig = go.Figure()

        for vin in df_filtered['VIN'].unique():
            vin_data = df_filtered[df_filtered['VIN'] == vin]
            monthly_avg = vin_data.groupby(vin_data['Dato'].apply(lambda x: x.strftime('%Y-%m'))).agg({'Aktuell vekt': 'mean'}).reset_index()
            fig.add_trace(go.Scatter(
                x=monthly_avg['Dato'],
                y=monthly_avg['Aktuell vekt'],
                mode='lines+markers',
                name=find_regnr(vin)
            ))

        fig.add_shape(
            x0=df_grouped['Måned'].min().to_timestamp(),
            x1=df_grouped['Måned'].max().to_timestamp(),
            type='line',
            y0=weight_limits[weight_class],
            y1=weight_limits[weight_class],
            line=dict(color='Red', dash='dash'),
            name=f'Maksgrense {weight_class}'
        )

        fig.update_layout(
            title=f'Aktuell vekt for {weight_class} i {selected_year}',
            xaxis_title='Måned',
            yaxis_title='Gjennomsnittsvekt (kg)',
            legend_title='Regnr',
            xaxis=dict(type='category')
        )
        graphs.append(dcc.Graph(figure=fig, style={'height': '400px'}))

    return graphs

