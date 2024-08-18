# index.py
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# Import pages
from pages import home, aksellastfordelinger, b_faktor, vekt_første_aksel, n_påvirkning_klassifisering, totalvekter, posisjoner, ekvipasje, ekvivalensfaktor, utviklinger_over_tid
from pages import gyro, kapasitet

# Define the layout for the app
def layout():
    return dbc.Container([
        dbc.Navbar(
            dbc.Container([
                dbc.Row([
                dbc.Col(
                    dcc.Link(dbc.NavbarBrand("Sommerstudentene hamar 2024", className="ms-2"), href="/"), 
                    width="auto"
                )
                ],
                align="center",
                className="g-0"),
            ], fluid=True),
            color="primary",
            dark=True,
            className="mb-4",
        ),
        dcc.Location(id='url', refresh=False),
        html.Div(id='breadcrumbs', className='text-start'),  # Add class to align text left
        html.Div(id='page-content', className='text-start')  # Add class to align text left
    ], fluid=True)

# Register the callbacks
def register_callbacks(app):
    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/':
            return home.layout()
        if pathname == '/aksellastfordelinger':
            return aksellastfordelinger.layout()
        if pathname == '/b_faktor':
            return b_faktor.layout()
        if pathname == '/vekt_aksel_semi':
            return vekt_første_aksel.layout()
        if pathname == '/n_paavirkning_klassifisering':
            return n_påvirkning_klassifisering.layout()
        if pathname == '/totalvekter':
            return totalvekter.layout()
        if pathname == '/posisjoner':
            return posisjoner.layout()
        if pathname == '/ekvipasjer':
            return ekvipasje.layout()
        if pathname == '/ekvivalensfaktor':
            return ekvivalensfaktor.layout()
        # if pathname == '/dekktrykk':
        #     return dekktrykk.layout()
        if pathname == '/kapasitet':
            return kapasitet.layout()
        if pathname == '/utviklinger_over_tid':
            return utviklinger_over_tid.layout()
        if pathname == '/gyro':
            return gyro.layout()
        else:
            return '404'
