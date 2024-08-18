from dash import Dash, dcc, html, dash_table, callback, Input, Output
import pandas as pd

# Les statistikk fra CSV-fil
def read_statistics(stat_col):
    file_path = f'LINX-data/kjøretøysdata/stats_forbruk/stats_{stat_col}.csv'
    return pd.read_csv(file_path)

def layout():
    return html.Div([
    html.H1("Oversikt over forbruk og utslipp"),
    dcc.Tabs(id='tabs', value='snitthastighet-tab', children=[
        dcc.Tab(label='Snitthastighet', value='snitthastighet-tab', children=[
            html.Div(id='snitthastighet-table-container')
        ]),
    ]),
])
callback(
    Output('snitthastighet-table-container', 'children'),
    Input('tabs', 'value'),
    prevent_initial_call=True
)
def update_snitthastighet_table(tab):
    if tab != 'snitthastighet-tab':
        return []

    stats_df = read_statistics('Snitthastighet')

    return [
        html.H3('Statistikk for Snitthastighet'),
        dash_table.DataTable(
            columns=[{'name': i, 'id': i} for i in stats_df.columns],
            data=stats_df.to_dict('records'),
        )
    ]



