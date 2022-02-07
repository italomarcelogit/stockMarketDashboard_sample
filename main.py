import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# 1 ---- setup ---- #
pathApp = './'
load_figure_template(["bootstrap", "darkly"])

# if source is csv file
# dados = pd.read_csv(f'{pathApp}data_stock.csv')

# using mongodb Atlas Sandbox
def mongoConecta(url, database, collection):
    mongo_url = url
    cliente = pymongo.MongoClient(mongo_url)
    DB = cliente[database]
    DC = DB[collection]
    return DC
db = mongoConecta(url="mongodb+srv://MYUser:MYPassword@URLsandbox.XYZ14.mongodb.net/XXXXXXX", 
                      database='MyDatabase', collection='MyDatacollection')
dados = pd.DataFrame(list(db.find({}, { '_id': 0 })))

ld = str(dados.date.sort_values(ascending=False).unique()[0]).split(' ')[0]
dados_high = dados[dados.indicator.isin(['high'])]
symbols = dados_high.symbol.sort_values().unique().tolist()

# 2 ---- container builder ---- #
elementos = [
    dbc.Row([
        dbc.Col([
            html.Img(src='/assets/logo.png', style={'width': '60%'})
        ], width=1),
        dbc.Col([
            html.H1(f"ISM - Italo Stock Market Dashboard"),
            dbc.Row([
                dbc.Col([
                    html.P(f"Date reference:")
                ], width=1),
                dbc.Col([
                    html.H6(f"{ld}")
                ], width=8),
                dbc.Col([
                    html.Div(
                        [
                            html.Span(className="fa fa-moon"),
                            dbc.Switch(value=True, id="theme", className="d-inline-block ml-2", ),
                            html.Span(className="fa fa-sun"),
                        ],
                        className="d-inline-block",
                    )

                ]),
            ]),

        ], width=11)
    ], justify='around')]
row = []
for symbol in symbols:
    symbol_coluna = dbc.Col(
        [
            dbc.Card([
                
                dbc.CardBody([
                    
                    dbc.Row([
                        dbc.Col([
                            html.Img(src=f'/assets/{symbol}.png', style={'width': '3rem'}, className='ml-4 bg-white')
                        ], width=2),
                        dbc.Col([
                            html.H4(f"{symbol} ")
                        ], width=3),
                        dbc.Col([
                            html.Span(children="xxxx", id=f"icone-{symbol}", className="")
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id=f'daily-line-{symbol}', figure={},
                                      config={'displayModeBar': False})
                        ], width=12)

                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button('low price', color='warning')
                        ], width={'size': 4, 'offset': 1}),
                        dbc.Col([
                            dbc.Button('high price', color='info')
                        ], width={'size': 5, 'offset': 2}),

                    ], justify='between'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(id=f'low-price-{symbol}', children={},
                                      className="mt-2 p-1 "),
                        ], width={'size': 4, 'offset': 1}),
                        dbc.Col([
                            dbc.Label(id=f'high-price-{symbol}', children={},
                                      className="mt-2 p-1"),
                        ], width={'size': 5, 'offset': 2})
                    ], justify="between"),
                ])
            ], style={'witdh': '24rem'}, className='mt-3')
        ], width=3)
    row.append(symbol_coluna)
    if len(row) == 4:
        elementos.append(dbc.Row(row, justify='center'))
if len(row) < 4:
    elementos.append(dbc.Row(row, justify='center'))
elementos.append(dcc.Interval(id='update', n_intervals=0, interval=1000 * 25))
elementos.append(html.Div(id="blank_output"))

# 3---- layout ---- #
app = dash.Dash('meuApp', external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
                meta_tags=[{'name': 'viewport', 
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server
app.title = 'Italo - Example Dashboard - Stock Finance'
app.layout = dbc.Container(elementos, fluid=True)

# 4---- callbacks ---- #
app.clientside_callback(
    """
    function(themeToggle) {
        //  To use different themes,  change these links:
        const theme1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css"
        const theme2 = "https://cdn.jsdelivr.net/npm/bootswatch@5.1.0/dist/darkly/bootstrap.min.css"
        const stylesheet = document.querySelector('link[rel=stylesheet][href^="https://cdn.jsdelivr"]')        
        var themeLink = themeToggle ? theme1 : theme2;
        stylesheet.href = themeLink
    }
    """,
    Output("blank_output", "children"),
    Input("theme", "value"),
)

outputs1 = [Output(f'daily-line-{i}', 'figure') for i in symbols]
@app.callback(
    outputs1,
    Input('update', 'n_intervals')
)
def update_graph(timer):
    results = []
    for symbol in symbols:
        dff = dados_high[dados_high.symbol == symbol]
        dff_rv = dff.iloc[::-1]
        fig = px.line(dff_rv, x='date', y='rate',
                      range_y=[dff_rv['rate'].min(), dff_rv['rate'].max()],
                      height=120).update_layout(margin=dict(t=0, r=0, l=0, b=20),
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(0,0,0,0)',
                                                yaxis=dict(
                                                    title=None,
                                                    showgrid=False,
                                                    showticklabels=False
                                                ),
                                                xaxis=dict(
                                                    title=None,
                                                    showgrid=False,
                                                    showticklabels=False
                                                ))
        

        day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
        day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]

        if day_end >= day_start:
            fig.update_traces(fill='tozeroy', line={'color': 'green'})
        elif day_end < day_start:
            fig.update_traces(fill='tozeroy',
                              line={'color': 'darkred'})
        results.append(fig)
    return results


outputs21 = [Output(f'icone-{i}', 'className') for i in symbols]  
@app.callback(
    outputs21,
    Input('update', 'n_intervals')
)
def update_result1(timer):
    results = []
    for symbol in symbols:
        dff = dados_high[dados_high.symbol == symbol]
        dff_rv = dff.iloc[::-1]
        day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
        day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]
        
        if day_end >= day_start:
            results.append("fa fa-arrow-up text-success")
        elif day_end < day_start:
            results.append("fa fa-arrow-down text-danger")  
    return results


outputs22 = [Output(f'icone-{i}', 'children') for i in symbols]  
@app.callback(
    outputs22,
    Input('update', 'n_intervals')
)
def update_result1(timer):
    results = []
    for symbol in symbols:
        dff = dados_high[dados_high.symbol == symbol]
        dff_rv = dff.iloc[::-1]
        day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
        day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]
        value = 100-(day_start*100/day_end)
        results.append(f"{value:.2f}%")
        
    return results





outputs3 = [Output(f'low-price-{i}', 'children') for i in symbols]
@app.callback(
    outputs3,
    Input('update', 'n_intervals')
)
def funcao(timer):
    rate = []
    for i in symbols:
        r = dados[(dados.symbol == i) & (dados.indicator.isin(['low']))]['rate'].min()
        rate.append(f"USD {r:.2f}")
    return rate


outputs4 = [Output(f'high-price-{i}', 'children') for i in symbols]
@app.callback(
    outputs4,
    Input('update', 'n_intervals')
)
def funcao(timer):
    rate = []
    for i in symbols:
        r = dados[(dados.symbol == i) & (dados.indicator.isin(['low']))]['rate'].max()
        rate.append(f"USD {r:.2f}")
    return rate


if __name__ == '__main__':
    app.run_server(debug=True, port=4321)
