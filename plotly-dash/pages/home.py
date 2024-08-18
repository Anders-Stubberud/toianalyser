# pages/home.py
import os
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import utils

def kolonne_med_informasjonskort(
        image: str,
        tittel: str,
        informativ_tekst: str,
        href: str
    ):
    
    return dbc.Col(
                dbc.Card([
                    dmc.Center(dbc.CardImg(src=f"/assets/{image}", top=True, style={'margin-top': '16px'}),),
                    dbc.CardBody([
                        html.H4(tittel, className="card-title"),
                        html.P(informativ_tekst, className="card-text"),
                        dmc.Center(dbc.Button("Les mer", color="primary", href=href), style={'margin-top': 'auto'})
                    ], style={'display': 'flex', 'flex-direction': 'column'}),
                ], style={'height': '100%'})
    )
    
def layout():
    return html.Div([

        dmc.Paper( # Intro
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title(f"Overordnet", order=2),

                dmc.Text("""
                    Denne siden presenterer utvalgte resultater knyttet til to av prosjektene sommerstudentene ved Statens Vegvesen på Hamar har arbeidet med i 2024.
                    Arbeidet er gjort av Tilde Veie, Lars Røste, og Anders Stubberud i regi av veileder Heine Toftegård.
                """, size='lg'),

                dmc.Text("""
                    Prosjektet 'Prøveordning for tømmervogntog inntil 74 tonn' baserer seg på å benytte dataanalyse for å avgjøre hvorvidt der er gunstig å 
                    øke dagens tillatte totalvekt for tømmertransport fra 60 til 74 tonn.
                """, size='lg'),

                dmc.Text("""
                    Videre er det gjort supplerende beregninger på et WIM-prosjekt (weight-in-motion) i regi av Leif Bakløkk.
                    Prosjektet tar sikte på å utarbeide et verktøy for prosjektering og beregning av nedbrytning av veger.
                """, size='lg'),
            ]
        ),

        html.Br(),

        dmc.Paper( # WIM-data
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title(f"WIM-data", order=2),

                html.Br(),

                dmc.Text("""
                    Teknologi, Drift, og vedlikehold ved Leif Jørgen Bakløkk arbeider med et prosjekt initiert gjennom FOUI-programmet VegDim,
                    der det utvikles et nytt verktøy for prosjektering og beregning av nedbrytning av veger.
                    Det langsiktige målet med prosjektet er å fremskaffe dokumentasjon på vekt-belastningen for hele vegnettet i Norge.
                    Å nå dette langsiktige målet innebærer et relativt stort arbeid, og det er derfor startet
                    en innledende analyse med følgende målsetting:
                """, size="lg"),

                html.Div([
                    dmc.Title("1. Beregne oppdaterte verdier for koeffisientene C og E i vegnormalens formel for beregning av total trafikkbelastning for vegens dimensjoneringsperiode.", order=4),
                    dmc.Title("2. Skaffe oversikt over tilgjengelige WIM-data og kvaliteten av disse dataene som grunnlag for planlegging av videre arbeid med å nå den langsiktige målsettingen.", order=4),
                    dmc.Title("3. Evaluere beregnede verdier med tanke på følgende forhold:", order=4),
                    dmc.List([
                        dmc.ListItem("Sammenligne de oppgitte verdiene i vegnormalen med beregnede verdier ut ifra registrerte aksellaster for trafikken per i dag."),
                        dmc.ListItem("Sammenligne de norske verdiene for «Truck factor» med tilsvarende verdier i Sverige."),
                        dmc.ListItem("Nøyaktigheten av de beregnede verdiene."),
                        dmc.ListItem("Er de beregnede verdiene representative for riksvegene generelt?"),
                        dmc.ListItem("Vurdere metoder for beregning av «Truck factor» der en ikke har tilgjengelige vektdata.")
                    ], style={'margin-left': '20px'})
                ]),

                html.Br(),

                dmc.Text("""
                    Arbeidet som er gjort her er supplerende beregninger som tar sikte på å bidra til prosjektet.
                """, size="lg"),

                html.Br(),

                dbc.Row([

                    kolonne_med_informasjonskort( # Påvirkning av vegfaktorer ved ny klassifisering av tunge kjøretøy
                        image='Påvirkning av vegfaktorer ved ny klassifisering av tunge kjøretøy.png', 
                        tittel="Påvirkning av vegfaktorer ved ny klassifisering av tunge kjøretøy",
                        informativ_tekst="""
                            Under konstruksjonen av nye veier benyttes en rekke faktorer for å avgjøre påkrevde kvaliteter.
                            Flere av disse faktorene har stått uendret som konstanter i lang tid.
                            Ettersom kjøretøyene som kjører rundt på de norske veiene har forandret seg betraktelig siden den tid,
                            er det nyttig å få et innblikk i hvorvidt disse faktorene har endret seg betraktelig.  
                        """,
                        href="/n_paavirkning_klassifisering"
                    ),

                    kolonne_med_informasjonskort( # Aksellastfordelinger
                        image='aksellastfordelinger.png', 
                        tittel="Aksellastfordelinger for enkelt, boggi, og trippelaksler",
                        informativ_tekst="""
                            Nedbrytning av veg er hovedsakelig forårsaket av aksellast, og er til dels påvirket av antall akslinger gjennom en såkalt 'pumpe-effekt'.
                            Sammenhengen mellom aksellastfordelinger og nedbrytning av veger kan bidra med å tydeliggjøre hva nedbrytningen forårsakes av. 
                        """,
                        href="/aksellastfordelinger"
                    ),



                ]),

                html.Br(),

                dbc.Row([

                    kolonne_med_informasjonskort( # Vekt på første aksel av 6-akslede semitrailere
                        image='vekt_første_aksel.png', 
                        tittel="Vekt på første aksel av 6-akslede semitrailere",
                        informativ_tekst="""
                            Nedbrytning av veg er hovedsakelig forårsaket av aksellast, og er til dels påvirket av antall akslinger gjennom en såkalt 'pumpe-effekt'.
                            Sammenhengen mellom aksellastfordelinger og nedbrytning av veger kan bidra med å tydeliggjøre hva nedbrytningen forårsakes av. 
                        """,
                        href="/vekt_aksel_semi"
                    ),

                    kolonne_med_informasjonskort( # B-faktor
                        image='b-faktor.png', 
                        tittel="B-faktor",
                        informativ_tekst="""
                            I Sverige benyttes en såkalt 'B-faktor' som en alternativ indikator på vegslitasje. 
                            Ved å regne ut tilsvarende indikator for de Norske vegstrekningene, danner man et grunnlag for sammenlikning. 
                        """,
                         href="/b_faktor"
                    ),

                ]),

                html.Br(),

                dbc.Row([

                    kolonne_med_informasjonskort( # Totalvekter
                        image='totalvekter.png', 
                        tittel="Totalvekter",
                        informativ_tekst="""
                            Hovedbidraget til nedbrytning av veger kommer fra tunge aksellaster, som er direkte knyttet til kjøretøyets totale vekt. 
                            Ved å ha en totalvekt-oversikt for tunge kjøretøy danner man et grunnlag for å forstå hvordan kjøretøyets totale vekt bidrar til nedbrytningen.
                        """,
                         href="/totalvekter"
                    ),

                    kolonne_med_informasjonskort( # Ekvivalensfaktor
                        image='ekvivalensfaktor.png', 
                        tittel="Ekvivalensfaktor",
                        informativ_tekst="""
                            Arbeidet som er gjort her i forbindese med WIM er supplerende beregninger for et større prosjekt.
                            Her ligger foreløpig rapport, som gir detaljert innsikt i prosjektet. 
                        """,
                         href="/ekvivalensfaktor"
                    ),

                ]),

            ]
        ),

        html.Br(),

        dmc.Paper( # 74-tonns tømmervogntogprosjektet
            radius="md",
            withBorder=True,
            shadow='xs',
            style={'margin-top': '2vh', 'width': '100%', 'padding': '20px'},
            children=[
                dmc.Title(f"74-tonns tømmervogntogprosjektet", order=2),

                dmc.Text("""
                    I perioden 2021-2024 har Statens Vegvesen tillatt utvalgte tømmervogntog en totalvekt opp til 74 tonn. 
                    Motivasjonen bak prosjektet er å undersøke hvordan en eventuell økning av tillat totalvekt for tømmervogntog kan påvirke 
                    blant annet trafikksikkerhet, framkommelighet, miljø- og klimagassutslipp, vegslitasje, bruer, transportkostnader, og konkurranseevnen for næringen.
                    
                    For å bidra til å danne et perspektiv av hvordan disse faktorene blir påvirket av ordningen, tar denne siden for seg beregninger og statistikk 
                    som belyser ulike effekter av ordningen. Dataen som danner grunnlagt for denne analysen er innhentet fra sensorer som er montert på
                    kjøretøyene som deltar i prøveordningen. Dette inkludererer også referansekjøretøy som ikke har fått sin tillatte totalvekt økt.
                    Dataen inkluderer blant annet posisjoner, totalvekter, akselvekter, dekktrykk, temperatur, og gyro-målinger.

                """, size="lg", style={"white-space": "pre-line"}),

                dbc.Row([

                    kolonne_med_informasjonskort( # Utviklinger over tid
                        image='utviklinger over tid.png', 
                        tittel="Hvordan har kjøreatferden utviklet seg over tid?",
                        informativ_tekst="Ved å studere hvordan atferden til kjøretøyene i prosjektet endrer seg over tid, vil man få et innblikk i hva de faktisk kjører med, og hvorvidt de evner å utnytte kapasiteten.",
                        href="/utviklinger_over_tid"
                    ),

                    kolonne_med_informasjonskort( # Ekvipasjer / kjøremønster
                        image='kjøremønster.png', 
                        tittel="Hvor har trafikken fra prøveordningen utartet seg?",
                        informativ_tekst="Kjøremønsteret fra prøveordningen kan bidra til å avdekke sammenhenger mellom økt tillatt totalvekt og lokale påvirkninger.",
                        href="/ekvipasjer"
                    ),

                ]),

                html.Br(),

                dbc.Row([

                    kolonne_med_informasjonskort( # Gyro
                        image='gyro.png', 
                        tittel="Gyro",
                        informativ_tekst="""
                            Vi ønsker å undersøke hvordan trafikksikkerheten påvirkes med tanke på stabilitet. 
                            Det har blitt ettermontert Teltonika FM som samler data for aksellerasjon, bremsing, hastighet og hard sving. 
                            Sensoren består av en GPS og et akselerometer.
                        """,
                        href="/gyro"
                    ),

                    kolonne_med_informasjonskort( # Kapasitet
                        image='kapasitet.png', 
                        tittel="Kapasitet",
                        informativ_tekst="""
                            Kapasitetsutnyttelse refererer til hvor effektivt et system eller en ressurs benyttes i forhold til dens totale tilgjengelige kapasitet.
                            I konteksten av de oppdaterte visualiseringene kan analyser av kapasitetsutnyttelse gi innsikt i hvordan lastebilene utnytter kapasiteten over tid
                            for å se om det vil lønne seg å øke tillat totalvekt fra 60 til 74-tonn.
                        """,
                        href="/kapasitet"
                    ),

                ], ),

            ]
        ),

        html.Br(),
    ], style=utils.STYLE_PAGES_MAIN_HTML_DIV)
