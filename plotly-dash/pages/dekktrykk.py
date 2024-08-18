import pandas as pd
import json
import plotly.express as px
from dash import dcc, html, callback, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go

def set_filename_dekktrykk():
    file_paths = [
        'analyse_linx_74t_2023/posdata24.csv',
        'analyse_linx_74t_2023/posrapport23.csv',
        'analyse_linx_74t_2023/posrapport22.csv',
        'analyse_linx_74t_2023/posrapport21.csv'
    ]
    
    # Les og kombiner alle filene
    dataframes = []
    for file_path in file_paths:
        data = pd.read_csv(file_path, sep=',', dtype={'Dekkmåling': 'str', 'Hard akselerasjon': 'str', 'Hard bremsing': 'str', 'Hard sving': 'str'}, low_memory=False)
        data.columns = data.columns.str.strip()
        dataframes.append(data)
    
    combined_data = pd.concat(dataframes, ignore_index=True)
    return combined_data

def find_dekktrykk():
    """
    Lager et nytt datasett på et mer oversiktlig format
    
    """
    df = set_filename_dekktrykk()
    rows = []

    for index, row in df.iterrows():
        vin = row['VIN']
        dato_tid = row['Dato']
        dato, tid = dato_tid.split(' ')
        tid = tid.split('.')[0]
        vekt = row['Aktuell vekt']
        dekkmaaling_str = row['Dekkmåling']  
 
        if pd.notna(dekkmaaling_str):
            try:
                dekkmaaling_json = json.loads(dekkmaaling_str.replace("'", '"'))
                for dekkmaaling in dekkmaaling_json:
                    tire_info = dekkmaaling.get('Tire', {})
                    axel = tire_info.get('Axle')
                    side = tire_info.get('Side')
                    position = tire_info.get('Position')
                    pressure = dekkmaaling.get("Pressure")
                    if pressure is not None and pressure!=0.05:
                        rows.append([vin, dato, tid, vekt, axel, side, position, pressure])
                 
            except json.JSONDecodeError as e:
                print(f"Feil ved parsing av JSON-streng i rad {index}: {e}")
    
    if not rows:
        print("Ingen gyldige dekkmålinger funnet.")
        return None
    else:
        dekkmaaling_df = pd.DataFrame(rows, columns=['VIN', 'Dato', 'Tid', 'Aktuell vekt', 'Axel', 'Side', 'Position', 'Pressure'])
        dekkmaaling_df['Dato'] = pd.to_datetime(dekkmaaling_df['Dato'])
        dekkmaaling_df['Tid'] = pd.to_datetime(dekkmaaling_df['Tid'], format='%H:%M:%S').dt.time
        return dekkmaaling_df

df = find_dekktrykk()
    
def find_regnr(vin_list):
    file_path = 'analyse_linx_74t_2023/Eiendelsrapport_20240709081303.csv'
    df = pd.read_csv(file_path, sep=';')
    vin_regnr_map = {}
    for vin in vin_list:
        match = df[df['VIN'] == vin]
        if not match.empty:
            vin_regnr_map[vin] = match['Regnr'].values[0]
        else:
            vin_regnr_map[vin] = None
    return vin_regnr_map    

def generate_scatter_plot(vin_data, selected_axel):
    vin_data['Label'] = vin_data.apply(lambda row: f"Aksel {row['Axel']}, Side {row['Side']}, Posisjon {row['Position']}", axis=1)
    fig = px.scatter(vin_data, x='Aktuell vekt', y='Pressure', color='Label', title=f'Vekt vs Lufttrykk for aksel {selected_axel}')
    return fig

def plot_pressure_over_time(vin, date, show_weight):
    
    vin_data = df[(df['VIN'] == vin) & (df['Dato'] == date)]
    
    if vin_data.empty:
        print("Ingen data funnet for denne kombinasjonen av VIN og dato.")
        return
    
    # Opprette plottet
    vin_data = vin_data.sort_values(by='Tid')
    fig = go.Figure()

    for axel in vin_data['Axel'].unique():
        axel_data = vin_data[vin_data['Axel'] == axel]
        for side in axel_data['Side'].unique():
            side_data = axel_data[axel_data['Side'] == side]
            for position in side_data['Position'].unique():
                position_data = side_data[side_data['Position'] == position]
                fig.add_trace(go.Scatter(
                    x=position_data['Tid'],
                    y=position_data['Pressure'],
                    mode='lines+markers',
                    name=f'Aksel {axel}, Side {side}, Posisjon {position}'
                ))

    if show_weight:
        fig.add_trace(go.Scatter(
            x=vin_data['Tid'],
            y=vin_data['Aktuell vekt'],
            mode='lines+markers',
            name='Aktuell vekt',
            yaxis='y2'
        ))

    fig.update_layout(
        title=f'Dekktrykk og Aktuell Vekt over tid {date}',
        xaxis_title='Tid',
        yaxis=dict(
            title='Dekktrykk (bar)',
            side='left'
        ),
        yaxis2=dict(
            title='Aktuell vekt (kg)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend_title='Kombinasjoner'
    )

    return fig

vin_regnr_map = find_regnr(df['VIN'].unique())

def generate_statistics():
    # Beregn maks, min og gjennomsnittlig dekktrykk for hver kombinasjon av VIN, aksel, side og posisjon
    stats = df.groupby(['VIN','Axel', 'Side', 'Position']).agg(
        max_pressure=('Pressure', 'max'),
        min_pressure=('Pressure', 'min'),
        avg_pressure=('Pressure', 'mean')
    ).reset_index()
    
    return stats

def layout():

    return html.Div([

        html.H1("Dekktrykk"),
        dcc.Dropdown(
            id = 'vin-dropdown',
            options = [{'label': f"{regnr}", 'value': vin} for vin, regnr in vin_regnr_map.items() if regnr is not None],
            placeholder = "Select Regnr"
        ),

        dcc.Tabs([
            dcc.Tab(label='Sammenlign med vekt', children=[
                dcc.Checklist(
                    id='axel-checklist',
                    options=[{'label': f'Aksel {axel}', 'value': axel} for axel in df['Axel'].unique()],
                    value=[],
                    inline=True,
                    labelStyle={'display': 'inline-block'}
                ),
                html.Div(id='graphs-container')
            ]),
            dcc.Tab(label='Se over tid', children=[
                dcc.DatePickerSingle(
                    id='date-picker',
                    min_date_allowed=df['Dato'].min().date(),
                    max_date_allowed=df['Dato'].max().date(),
                    initial_visible_month=df['Dato'].min().date(),
                    date=str(df['Dato'].min().date())
                ),
            
                dcc.Graph(id='time-series-plot'),
                dcc.Graph(id='weight-over-time-plot')
            ]),
            dcc.Tab(label='Statistikk', children=[
                html.Div(id='statistics-table')
            ])
        ])
    ])

@callback(
    Output('axel-checklist', 'options'),
    Input('vin-dropdown', 'value')
)

def set_axel_options(selected_vin):
    if selected_vin is None:
        return []
    vin_data = df[df['VIN'] == selected_vin]
    return [{'label': f'Aksel {axel}', 'value': axel} for axel in vin_data['Axel'].unique()]

@callback(
    Output('graphs-container', 'children'),
    Input('vin-dropdown', 'value'),
    Input('axel-checklist', 'value')
)

def update_graphs(selected_vin, selected_axels):
    if selected_vin is None or not selected_axels:
        return []
    graphs = []
    for axel in selected_axels:
        vin_data = df[(df['VIN'] == selected_vin) & (df['Axel'] == axel)]
        vin_data['Label'] = vin_data.apply(lambda row: f"Aksel {row['Axel']}, Side {row['Side']}, Posisjon {row['Position']}", axis=1)
        fig = generate_scatter_plot(vin_data, selected_vin)
        graphs.append(dcc.Graph(figure=fig, style={'height': '400px'}))
    return graphs

@callback(
    [Output('time-series-plot', 'figure'),
    Output('weight-over-time-plot', 'figure')],
    Input('vin-dropdown', 'value'),
    Input('date-picker', 'date')
)

def update_time_series_plot(selected_vin, selected_date):
    if selected_vin is None or selected_date is None:
        return {}
    selected_date = pd.to_datetime(selected_date)
    pressure_fig = plot_pressure_over_time(selected_vin, selected_date, show_weight=False)
    weight_fig = plot_weight_over_time(selected_vin, selected_date)
    return pressure_fig, weight_fig

def plot_weight_over_time(vin, date):
    df = find_dekktrykk()
    
    # Filtrere data for spesifikt VIN og dato
    vin_data = df[(df['VIN'] == vin) & (df['Dato'] == date)]
    
    if vin_data.empty:
        print("Ingen data funnet for denne kombinasjonen av VIN og dato.")
        fig = go.Figure()
        fig.update_layout(
            title=f'Aktuell vekt over tid for VIN {vin} på {date}',
            xaxis_title='Tid',
            yaxis_title='Aktuell vekt (kg)',
            legend_title='Vekt'
        )
        return fig
    
    # Sortere data etter tid
    vin_data = vin_data.sort_values(by='Tid')
    
    # Opprette plottet
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=vin_data['Tid'],
        y=vin_data['Aktuell vekt'],
        mode='lines+markers',
        name='Aktuell vekt'
    ))

    fig.update_layout(
        title=f'Aktuell vekt over tid for VIN {vin} på {date}',
        xaxis_title='Tid',
        yaxis_title='Aktuell vekt (kg)',
        legend_title='Vekt'
    )

    return fig


@callback(
    Output('statistics-table', 'children'),
    Input('vin-dropdown', 'value')
)
def update_statistics(selected_vin):
    if selected_vin is None:
        return []
    stats = generate_statistics()
    vin_stats = stats[stats['VIN'] == selected_vin]
    
    return dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in vin_stats.columns],
        data=vin_stats.to_dict('records')
    )