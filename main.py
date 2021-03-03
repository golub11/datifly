import base64
import io
import json
import math

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Ucitavanje postojecih CSS fajlova sa interneta
# external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.9.0/feather.min.js',
#                  'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js',
#                'https://code.jquery.com/jquery-3.5.1.slim.min.js']

external_scripts = ['https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js',
                    'https://kit.fontawesome.com/66470fcb10.js']

# Ucitavanje CDN bootstrap biblioteke
external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts,
                suppress_callback_exceptions=True)

server=app.server
app.title='Datifly project'


colorscales = ['bluered', 'portland', 'cividis', 'darkmint', 'greys', 'inferno', 'viridis']
# pio.templates.default = "plotly_dark"
# za drzave json poligoni
with open('countries.geojson') as response:
    countries = json.load(response)

# with open('geo-srbija.geojson',encoding="utf-8") as response:
#     data = response.readlines()
#     regioni_srbija = json.load(response)

with open('geo-srb.geojson') as f:
    regioni_srbija = json.load(f)

with open('slo-regioni.geojson', encoding="utf-8") as f:
    regioni_slovenija = json.load(f)


geo_slo = pd.DataFrame(regioni_slovenija['features'])
geo_srbija  = pd.DataFrame(regioni_srbija['features'])

geo_okruzi = []
for i in range(0,len(geo_srbija)):
    geo_okruzi.append(geo_srbija['properties'][i]['name'])

geo_slovenija = []
for i in range(0,len(geo_srbija)):
    geo_slovenija.append(geo_srbija['properties'][i]['name'])


geo_names = []
geo_short = []

geo_locations = pd.DataFrame(countries['features'])
for i in range(0,len(geo_locations)):
    geo_names.append(geo_locations['properties'][i]['ADMIN'])
    geo_short.append(geo_locations['properties'][i]['ISO_A3'])

choose_figure = html.Div(className="grid-figure-container row text-center",
                         style={"display": "grid", "gridTemplateColumns": "auto auto"}, children=[
        html.Div([html.Button([], id="map-chart", n_clicks=0, disabled=True),
                  html.I(className="fas fa-info-circle", id="info-map")]),
        html.Div([
            html.Button([], id="scatter-maps-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-scatter-maps")]),
        html.Div([
            html.Button([], id="density-maps-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-density-maps")
        ]),
        html.Div([
            html.Button([], id="bubble-maps-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-bubble-maps")
        ]),
        html.Div([
            html.Button([], id="bar-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-bar")
        ]),
        html.Div([
            html.Button([], id="pie-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-pie")
        ]),
        html.Div([
            html.Button([], id="scatter-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-scatter")
        ]),
        html.Div([
            html.Button([], id="bubble-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-bubble")
        ]),
        html.Div([
            html.Button([], id="line-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-line")
        ]),
        html.Div([
            html.Button([], id="histogram-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-histogram")
        ]),

        html.Div([
            html.Button([], id="heat-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-heatmap")
        ]),
        html.Div([
            html.Button([], id="box-plot-chart", n_clicks=0, disabled=True),
            html.I(className="fas fa-info-circle", id="info-box-plot")
        ])
    ])

# Kod za navigacioni meni sa strane
nav_bar = html.Nav(className="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0 shadow", children=[
    html.A([html.I([],className="fas fa-chart-bar mr-1 text-white"),"Datifly project"], className="navbar-brand col-md-3 col-lg-2 mr-0 px-3")
])

# kod za upload dataseta
upload_component = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Do not allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(["ili izaberite ugradjene podatke:  ",dbc.Button('Za Srbiju', color="primary", className="mr-2", id="srbija",n_clicks=0),dbc.Button('Za Svet',color="success",id="svet",n_clicks=0)],
             style={
                 'width': '100%',
                 'height': '60px',
                 'lineHeight': '40px',
             }),
    # dbc.Modal([dbc.Input(type="text", placeholder="Text to replace")],is_open=True),
    html.Div(id='output-data-upload'),
    html.Div(id='output-columns-upload'),
    html.Div(id='output-only-columns'),
    html.Div(id="testing-div"),
])

#
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

#df2 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group", width=500, height=350)

df = pd.DataFrame()
cols = []
type_of_feature = {}
dimensions = []
measures = []
date_time = []
reset_opacity = {"opacity": "0.4"}

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

PAGE_SIZE = 8

def load_and_parse_prepopulated_data(filename):
    try:
        if 'csv' in filename:
            type_of_feature.clear()
            measures.clear()
            date_time.clear()
            dimensions.clear()
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(filename, encoding = 'utf-8', error_bad_lines=False)

            for i in range(0, df.columns.size):
                if df.columns[i].lower() == 'month':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'year':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'day':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'week':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'hours':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'longitude' or df.columns[i].lower() == 'long' or df.columns[i].lower() == 'lon':
                    type_of_feature[df.columns[i]] ="Longitude"
                    dimensions.append(df.columns[i])
                elif df.columns[i].lower() == 'latitude' or df.columns[i].lower() == 'lat':
                    type_of_feature[df.columns[i]] = "Latitude"
                    dimensions.append(df.columns[i])
                elif isinstance(df[df.columns[i]][0], str):
                    dimensions.append(df.columns[i])
                else:
                    measures.append(df.columns[i])
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     type_of_feature.clear()
        #     measures.clear()
        #     date_time.clear()
        #     dimensions.clear()
        #     df = pd.read_excel(io.BytesIO(decoded))
        #     for i in range(0, df.columns.size):
        #         if df.columns[i].lower() == 'month':
        #             type_of_feature[df.columns[i]] = 'Date (month)'
        #         elif df.columns[i].lower() == 'year':
        #             type_of_feature[df.columns[i]] = 'Date (year)'
        #         elif df.columns[i].lower() == 'day':
        #             type_of_feature[df.columns[i]] = 'Date (day)'
        #         elif df.columns[i].lower() == 'week':
        #             type_of_feature[df.columns[i]] = 'Date (week)'
        #         elif df.columns[i].lower() == 'hours':
        #             type_of_feature[df.columns[i]] = 'Date (hours)'
        #         elif df.columns[i].lower() == 'longitude'or df.columns[i].lower() == 'long':
        #             type_of_feature[df.columns[i]] = 'Longitude'
        #         elif df.columns[i].lower() == 'latitude' or df.columns[i].lower() == 'lat':
        #             type_of_feature[df.columns[i]] = 'Latitude'
        #         elif isinstance(df[df.columns[i]][0], str):
        #             type_of_feature[df.columns[i]] = 'Dimension'
        #             dimensions.append(df.columns[i])
        #         else:
        #             type_of_feature[df.columns[i]] = 'Measure'
        #             measures.append(df.columns[i])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return html.Div([
        html.H5(filename),
        html.Br(),
        dcc.Tabs(id='tabs-example', value='', children=[
            dcc.Tab(label='Preparation', value='Data'),
            dcc.Tab(label='Visualisation', value='Visualisation'),
        ]),
        html.Div(id='tabs-example-content'),
        dcc.Store(id="storage-for-data", storage_type="memory", data=df.to_dict('records')),
        html.Br(),
        dbc.Button("Klikni za sintaksu filtriranja: ",id="filter-syntax",n_clicks=0),
        dbc.Modal([
            dbc.ModalHeader("Sintaksa za filtriranje numeričkih kolona: "),
            dbc.ModalBody("eq n,> n,< n, n je realan broj"),
            dbc.ModalHeader("Sintaksa za filtriranje teksualnih kolona(dovoljna su i prva par karktera trazenog teksta): "),
            dbc.ModalBody("eq 'tekst', eq 'tek' "),
            dbc.ModalFooter(
                dbc.Button("Zatvori", id="close-info-filter-btn", className="ml-auto")
            )
        ], id="modal-filter-chart"),html.Br(),
        html.Label("Data preview:"),
        dash_table.DataTable(
            id='table',
            columns=[{'name': i, 'id': i, 'deletable': True, 'renamable': True} for i in df.columns],
            style_table={'height': '250px', 'overflowY': 'auto','left':'0','border':'1px solid #6c757d'},
            #row_deletable=True,

            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom',

            filter_action='custom',
            filter_query='',

            sort_action='custom',
            sort_mode='multi',
            sort_by=[],

            style_data={
                'width': '100px', 'minWidth': '60px', 'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            }
        ),
        html.Br(),
        html.Br(),
        html.Hr(),  # horizontal line
        html.Br(),


    ],style={"position":"relative"})




def load_and_parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            type_of_feature.clear()
            measures.clear()
            date_time.clear()
            dimensions.clear()
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), error_bad_lines=False)

            for i in range(0, df.columns.size):
                if df.columns[i].lower() == 'month':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'year':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'day':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'week':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'hours':
                    date_time.append(df.columns[i])
                elif df.columns[i].lower() == 'longitude' or df.columns[i].lower() == 'long' or df.columns[i].lower() == 'lon':
                    type_of_feature[df.columns[i]] ="Longitude"
                    dimensions.append(df.columns[i])
                elif df.columns[i].lower() == 'latitude' or df.columns[i].lower() == 'lat':
                    type_of_feature[df.columns[i]] = "Latitude"
                    dimensions.append(df.columns[i])
                elif isinstance(df[df.columns[i]][0], str):
                    dimensions.append(df.columns[i])
                else:
                    measures.append(df.columns[i])
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     type_of_feature.clear()
        #     measures.clear()
        #     date_time.clear()
        #     dimensions.clear()
        #     df = pd.read_excel(io.BytesIO(decoded))
        #     for i in range(0, df.columns.size):
        #         if df.columns[i].lower() == 'month':
        #             type_of_feature[df.columns[i]] = 'Date (month)'
        #         elif df.columns[i].lower() == 'year':
        #             type_of_feature[df.columns[i]] = 'Date (year)'
        #         elif df.columns[i].lower() == 'day':
        #             type_of_feature[df.columns[i]] = 'Date (day)'
        #         elif df.columns[i].lower() == 'week':
        #             type_of_feature[df.columns[i]] = 'Date (week)'
        #         elif df.columns[i].lower() == 'hours':
        #             type_of_feature[df.columns[i]] = 'Date (hours)'
        #         elif df.columns[i].lower() == 'longitude'or df.columns[i].lower() == 'long':
        #             type_of_feature[df.columns[i]] = 'Longitude'
        #         elif df.columns[i].lower() == 'latitude' or df.columns[i].lower() == 'lat':
        #             type_of_feature[df.columns[i]] = 'Latitude'
        #         elif isinstance(df[df.columns[i]][0], str):
        #             type_of_feature[df.columns[i]] = 'Dimension'
        #             dimensions.append(df.columns[i])
        #         else:
        #             type_of_feature[df.columns[i]] = 'Measure'
        #             measures.append(df.columns[i])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return html.Div([
        html.H5(filename),
        html.Br(),
        dcc.Tabs(id='tabs-example', value='', children=[
            dcc.Tab(label='Preparation', value='Data'),
            dcc.Tab(label='Visualisation', value='Visualisation'),
        ]),
        html.Div(id='tabs-example-content'),
        dcc.Store(id="storage-for-data", storage_type="memory", data=df.to_dict('records')),
        html.Br(),
        html.Label("Data preview:"),
        dash_table.DataTable(
            id='table',
            columns=[{'name': i, 'id': i, 'deletable': True, 'renamable': True} for i in df.columns],
            style_table={'height': '250px', 'overflowY': 'auto','left':'0','border':'1px solid #6c757d'},
            #row_deletable=True,

            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom',

            filter_action='custom',
            filter_query='',

            sort_action='custom',
            sort_mode='multi',
            sort_by=[],

            style_data={
                'width': '100px', 'minWidth': '60px', 'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            }
        ),
        html.Br(),
        html.Br(),
        html.Hr(),  # horizontal line
        html.Br(),


    ],style={"position":"relative"})


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


# CALLBACK FOR LOADING & SHOWING DATA AND ALSO STORING IN DCC.STORE
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
              Input('srbija', 'n_clicks'),
              Input('svet', 'n_clicks')],
              [State('upload-data', 'filename')])
def show_table(list_of_contents, srbijaDS, svetDS, list_of_names):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if list_of_contents is not None:
        tmp = load_and_parse_contents(list_of_contents, list_of_names)
        return (tmp)  # , kolone
    elif "srbija" in changed_id:
        tmp = load_and_parse_prepopulated_data('test.csv')
        return (tmp)  # , kolone
    elif "svet" in changed_id:
        tmp = load_and_parse_prepopulated_data('svet.csv')
        return (tmp)  # , kolone

    else:
        return dash.no_update

# CALLBACK FOR SIDEBAR UPDATE UI
@app.callback(Output('sidebar-features', 'children'),
              [Input("table", "columns"),
               Input("storage-for-data", "data"),
               ])
def render_sidebar(cols,data):
    global measures
    global date_time
    global dimensions
    return (html.Label("Ukupno "+str(len(measures)+len(dimensions)+len(date_time)) +" dimenzija",className="ml-3 text-light"),html.H6(
        className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted ",
        children=[

            html.H2("Kategorije",id="dimensions-sidebar"),
        ]),
          html.Ul(className="nav flex-column", children=[
              html.Li(className="nav-item", children=[
                  html.P([html.I([],className="fas fa-font mr-1"),dimensions[i]], className="nav-link active mb-0")
              ]) for i in range(0, len(dimensions))
          ]),
          html.H6(
              className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted",
              children=[
                  html.H2("Numeričke",id="measures-sidebar"),
              ]),
          html.Ul(className="nav flex-column", children=[
              html.Li(className="nav-item", children=[
                  html.P([html.I([],className="fab fa-slack-hash mr-1"),measures[i]], className="nav-link mb-0 text-success")
              ]) for i in range(0, len(measures))
          ]),
        html.H6(
            className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted",
            children=[
                html.Span("Kalendar",id="date-sidebar"),
            ]),
        html.Ul(className="nav flex-column", children=[
            html.Li(className="nav-item", children=[
                html.P([html.I([],className="far fa-calendar-alt mr-1"),date_time[i]], className="nav-link mb-0 text-warning")
            ]) for i in range(0, len(date_time))
        ]),

    )

# CALLBACK FOR FILTERING/SORTING/PAGING DATATABLE
@app.callback(
    Output('table', 'data'),
    [Input('table', "page_current"),
     Input('table', "page_size"),
     Input('table', 'sort_by'),
     Input('table', 'filter_query')],
    State("storage-for-data", "data"))
def update_table(page_current, page_size, sort_by, filter, data):
    filtering_expressions = filter.split(' && ')
    dff = pd.DataFrame.from_dict(data)
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    df2 = pd.DataFrame.from_dict(data)
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[page_current * page_size:(page_current + 1) * page_size].to_dict('records')

#
# # ADD NEW COLUMN CALLBACK
# @app.callback(
#     Output('table', 'columns'),
#     [Input('new-column-button', 'n_clicks')],
#     [State('new-column-name', 'value'),
#      State('table', 'columns')])
# def add_new_column(n_clicks, value, existing_columns):
#     if n_clicks > 0:
#         existing_columns.append({
#             'id': value, 'name': value,
#             'renamable': True, 'deletable': True
#         })
#     return existing_columns
@app.callback([Output("add-column-toast","is_open"),
               Output("find-and-replace-toast","is_open"),
               Output("replace-with-value-toast","is_open"),
               Output("text-to-count-toast","is_open"),
               Output("groupby-toast","is_open"),
               ],
              Input("rename-btn","n_clicks"),
              Input("text-btn","n_clicks"),
              Input("custom-value-btn","n_clicks"),
              #Input("count-btn","n_clicks"),
              Input("groupby-btn","n_clicks"),
              State("storage-for-data", "data"),
              State("selected-columns", "value")
              )
def show_toasts(rename, replace_text,replace_value,groupby_count_btn,data,values):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # dff = pd.DataFrame.from_dict(data)
    if values is not None:
        if "rename-btn" in changed_id:
            return True, False, False, False, False
        if "text-btn" in changed_id:
            return False, True, False, False, False
        if "custom-value-btn" in changed_id:
            return False, False, True, False, False
        # if "count-btn" in changed_id:
        #     return False, False, False, True, False
        if "groupby-btn" in changed_id:
            return False, False, False, False,True
        if "count-btn" in changed_id:
            return False, False, False, True, False
    raise PreventUpdate
# CALLBACKs FOR EDITING DATASET
@app.callback([Output("testing-div", "children"),
               Output("storage-for-data", "data")],
              [Input("standardize-btn", "n_clicks"),
               Input('remove-nulls-btn', 'n_clicks'),
               Input('remove-column-btn', 'n_clicks'),
               Input("confirm-replacing-btn", "n_clicks"),
               Input("average-btn", "n_clicks"),
               Input("mode-btn", "n_clicks"),
               Input("change-to-string", "n_clicks"),
               Input("change-to-int", "n_clicks"),
               Input("change-to-date", "n_clicks"),
               Input("change-to-longitude", "n_clicks"),
               Input("change-to-latitude", "n_clicks"),
               Input("change-to-country", "n_clicks"),
               Input("confirm-group-by", "n_clicks"),
               Input("text-to-count-btn", "n_clicks"),
               Input("rename-column-button", "n_clicks"),
               Input("replace-with-value-btn", "n_clicks")],
              [State("storage-for-data", "data"),
               State("selected-columns", "value"), #STATE DRUGIH TOAST-A
               State("to-replace", "value"),
               State("value", "value"),
               State("agg-radio-btn", "value"),
               State("replace-with-custom-value-input","value"),
               State("groupby-value-input","value"),
               State("text-to-count-input","value"),
               State("rename-column-input","value"),
               State("add-column-counted-btn","value"),
               ])
def changing_dataset(a, b, c, d, e, f, to_string, to_int, to_date,to_lon,to_lat,to_country,groupby_btn,text_to_count_btn,new_col_btn,replace_btn,data, values, to_replace,value,agg_radio_button,replace_null_with,groupby,text_to_count_input, new_name_col,add_counted_col):
    from statistics import mode

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    dff = pd.DataFrame.from_dict(data)
    if values is not None:
        if "change-to-string" in changed_id:

            for i in values:
                dff[i] = dff[i].astype(str)
                #update UI
                measures.remove(i)
                dimensions.append(i)
            return html.P(["changing int to string"]), pd.DataFrame.to_dict(dff)


        if "change-to-int" in changed_id:
            for i in values:
                 dff[i] = pd.to_numeric(dff[i])
                 dimensions.remove(i)
                 measures.append(i)
            return html.P(["changing string to int"]), pd.DataFrame.to_dict(dff)

        #radi
        if "rename-column-button" in changed_id:

            # rename selected columnn in DataFrame
            if values is not None and new_name_col is not None:
                dff.rename(columns={values[0]: new_name_col}, inplace=True, errors="raise")

                if values[0] in measures:
                    measures.remove(values[0])
                    measures.append(new_name_col)
                elif values[0] in dimensions:
                    dimensions.remove(values[0])
                    dimensions.append(new_name_col)
                return html.P(["renaming"]), pd.DataFrame.to_dict(dff)
            else:
                raise PreventUpdate

        # radi
        if "standardize-btn" in changed_id:
            # standardize selected columnn in DataFrame
            for col in values:
                if isinstance(dff[col], str):
                    return 1
                else:
                    normalized_df = (dff[col] - dff[col].min()) / (dff[col].max() - dff[col].min())
                    dff[col] = normalized_df

            return html.P(["standardizing"]), pd.DataFrame.to_dict(dff)
        # radi
        if "remove-nulls-btn" in changed_id:
            #         #remove nulls from selected columng in DataFrame
            dff.dropna()
            return html.P(["removing nulls"]), pd.DataFrame.to_dict(dff)
        #radi
        elif "remove-column-btn" in changed_id:
            #         #remove whole column from loaded DataFrame
            dff = dff.drop(columns=[values[0]])
            if values[0] in measures:
                measures.remove(values[0])
            elif values[0] in dimensions:
                dimensions.remove(values[0])
            else:
                date_time.remove(values[0])
            return html.P(["deleting column"]), pd.DataFrame.to_dict(dff)

        # if "text-to-count-btn" in changed_id:
        #     counted_text = dff[values[0]].value_counts()
        #     col = pd.Series()
        #     for i in values:
        #         if i in dimensions:
        #             col = dff[dff[i] == text_to_count_input]
        #             if len(add_counted_col)>0:
        #                 dff['counted_'+i] = col.values
        #                 measures.append('counted_'+i)
        #         else:
        #             col = dff[dff[i]==text_to_count_input]
        #             if len(add_counted_col) > 0:
        #                 dff['counted_' + i] = col.values
        #                 measures.append('counted_' + i)
        #
        #     return html.P(["Counting text matches"]), pd.DataFrame.to_dict(dff)

        # radi
        # FIND AND REPLACE WITH:
        if "confirm-replacing-btn" in changed_id:
            if values[0] in dimensions:
                dff = dff.replace(to_replace=to_replace, value=value)
            else:
                to_replace = int(to_replace)
                value= int(value)
                dff = dff.replace(to_replace=to_replace, value=value)

            return html.P(["replacing text"]), pd.DataFrame.to_dict(dff)

        # !!check missing values and null
        elif "replace-with-value-btn" in changed_id:
            if values[0] in measures:
                to_change = replace_null_with
                dff = dff.fillna(value=to_change)
                return html.P(["replacing null with custom value"]), pd.DataFrame.to_dict(dff)
            else:
                #nije moguce zameniti null sa celobrojnom vrednoscu
                # jer kolona nije measure vec dimension
                return dash.no_update
        elif "average-btn" in changed_id:
            # i = 0
            average_col = {}
            for col in values:
                if col in measures:
                    average_col = {col: (sum(dff[col]) / len(dff[col]))}
            #         vs[col] = average_col
            # if len(vs)>0:
                    dff = dff.fillna(value=average_col)
            if len(average_col) > 0:
                return html.P(["replacing with average value"]), pd.DataFrame.to_dict(dff)
            else:
                return dash.no_update
        elif "mode-btn" in changed_id:
            mode_col = {}
            for col in values:
                if col in measures:
                    mode_col = {col: (mode(dff[col]))}
            #         vs[col] = mode_col
            # if len(vs) > 0:
                    dff = dff.fillna(value=mode_col)

            if len(mode_col) > 0:
             return html.P(["replacing with mode"]), pd.DataFrame.to_dict(dff)
            else:
                return dash.no_update

        # GROUP BY {STATISTICAL PARAMATER} POPRAVITI!!
        # clicked on button group by
        if "confirm-group-by" in changed_id:
            # LISTEN FOR VALUE, AGG FUN
            if agg_radio_button == 1:
                if groupby in measures:
                    grouped_df = create_agg_variable(values, 'sum', groupby, dff)
                    grouped_df= pd.Series.to_frame(grouped_df)
                    index = grouped_df.index
                    grouped_df[values[0]] = index
                    grouped_df = grouped_df[[values[0],groupby]]
                    #preview grouped
                    sumTable = dash_table.DataTable(
                        columns = [{"name":"SUM_"+i,"id":i} for i in grouped_df.columns],
                        data=grouped_df.to_dict('records'),
                    )
                    html_code = html.Div([dbc.Modal([
                                dbc.ModalHeader("Group by "+values[0]+" (SUM)"),
                                dbc.ModalBody([
                                    sumTable
                                ]),
                                dbc.ModalFooter(
                                    dbc.Button("Zatvori", id="close-sum", className="ml-auto")
                                )
                            ], id="modal-sum",is_open=True,style={"height":"100%"})]),
                    return html_code, pd.DataFrame.to_dict(dff)
                else:
                    dash.no_update
            elif agg_radio_button == 2:
                if groupby in measures:
                    grouped_df = create_agg_variable(values, 'avg', groupby, dff)
                    grouped_df = pd.Series.to_frame(grouped_df)
                    index = grouped_df.index
                    grouped_df[values[0]] = index
                    grouped_df = grouped_df[[values[0], groupby]]
                    # preview grouped
                    sumTable = dash_table.DataTable(
                        columns=[{"name": "AVG_" + i, "id": i} for i in grouped_df.columns],
                        data=grouped_df.to_dict('records'),
                    )
                    html_code = html.Div([dbc.Modal([
                        dbc.ModalHeader("Group by " + values[0] + " (AVG)"),
                        dbc.ModalBody([
                            sumTable
                        ]),
                        dbc.ModalFooter(
                            dbc.Button("Zatvori", id="close-avg", className="ml-auto")
                        )
                    ], id="modal-avg", is_open=True, style={"height": "100%"})]),
                    return html_code, pd.DataFrame.to_dict(dff)
                else:
                    dash.no_update
            elif agg_radio_button == 3:
                if groupby in measures:
                    grouped_df = create_agg_variable(values, 'min', groupby, dff)
                    grouped_df = pd.Series.to_frame(grouped_df)
                    index = grouped_df.index
                    grouped_df[values[0]] = index
                    grouped_df = grouped_df[[values[0], groupby]]
                    # preview grouped
                    sumTable = dash_table.DataTable(
                        columns=[{"name": "MIN_" + i, "id": i} for i in grouped_df.columns],
                        data=grouped_df.to_dict('records'),
                    )
                    html_code = html.Div([dbc.Modal([
                        dbc.ModalHeader("Group by " + values[0] + " (MIN)"),
                        dbc.ModalBody([
                            sumTable
                        ]),
                        dbc.ModalFooter(
                            dbc.Button("Zatvori", id="close-sum", className="ml-auto")
                        )
                    ], id="modal-min", is_open=True, style={"height": "100%"})]),
                    return html_code, pd.DataFrame.to_dict(dff)

                else:
                    dash.no_update

            elif agg_radio_button == 4:
                if groupby in measures:
                    grouped_df = create_agg_variable(values, 'max', groupby, dff)
                    grouped_df = pd.Series.to_frame(grouped_df)
                    index = grouped_df.index
                    grouped_df[values[0]] = index
                    grouped_df = grouped_df[[values[0], groupby]]
                    # preview grouped
                    sumTable = dash_table.DataTable(
                        columns=[{"name": "MAX_" + i, "id": i} for i in grouped_df.columns],
                        data=grouped_df.to_dict('records'),
                    )
                    html_code = html.Div([dbc.Modal([
                        dbc.ModalHeader("Group by " + values[0] + " (MAX)"),
                        dbc.ModalBody([
                            sumTable
                        ]),
                        dbc.ModalFooter(
                            dbc.Button("Zatvori", id="close-max", className="ml-auto")
                        )
                    ], id="modal-max", is_open=True, style={"height": "100%"})]),
                    return html_code, pd.DataFrame.to_dict(dff)

                else:
                    dash.no_update
            # else:
            #     GROUP BY AND COUNT
            else:
                dash.no_update
        else:
            dash.no_update

    else:
        raise PreventUpdate

# # GROUP BY {STATISTICAL PARAMATER}
# @app.callback(Output("promeni-id", "i state/prop"),
#               [Input("math-func", "n_clicks")])
# def group_by_callback(a,b,c,d,e):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if "math-func" in changed_id:
#         return 0
# where condition
#

@app.callback(
    Output("modal-max", "is_open"),
    [Input("close-max", "n_clicks")],
    [State("modal-max", "is_open")],
)
def groupby_max(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("modal-min", "is_open"),
    [Input("close-min", "n_clicks")],
    [State("modal-min", "is_open")],
)
def groupby_min(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("modal-avg", "is_open"),
    [Input("close-avg", "n_clicks")],
    [State("modal-avg", "is_open")],
)
def groupby_avg(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("modal-sum", "is_open"),
    [Input("close-sum", "n_clicks")],
    [State("modal-sum", "is_open")],
)
def groupby_sum(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("modal-map-chart", "is_open"),
    [Input("info-map", "n_clicks"),
     Input("close-info-map-btn", "n_clicks")],
    [State("modal-map-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-scatter-map-chart", "is_open"),
    [Input("info-scatter-maps", "n_clicks"),
     Input("close-info-scatter-map-btn", "n_clicks")],
    [State("modal-scatter-map-chart", "is_open")],
)
def info_about_scatter_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-density-map-chart", "is_open"),
    [Input("info-density-maps", "n_clicks"),
     Input("close-info-density-map-btn", "n_clicks")],
    [State("modal-density-map-chart", "is_open")],
)
def info_about_density_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-bubble-map-chart", "is_open"),
    [Input("info-bubble-maps", "n_clicks"),
     Input("close-info-bubble-map-btn", "n_clicks")],
    [State("modal-bubble-map-chart", "is_open")],
)
def info_about_bubble_maps_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-bar-chart", "is_open"),
    [Input("info-bar", "n_clicks"),
     Input("close-info-bar-btn", "n_clicks")],
    [State("modal-bar-chart", "is_open")],
)
def info_about_bar_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-pie-chart", "is_open"),
    [Input("info-pie", "n_clicks"),
     Input("close-info-pie-btn", "n_clicks")],
    [State("modal-pie-chart", "is_open")],
)
def info_about_pie_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-scatter-chart", "is_open"),
    [Input("info-scatter", "n_clicks"),
     Input("close-info-scatter-btn", "n_clicks")],
    [State("modal-scatter-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-bubble-chart", "is_open"),
    [Input("info-bubble", "n_clicks"),
     Input("close-info-bubble-btn", "n_clicks")],
    [State("modal-bubble-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-line-chart", "is_open"),
    [Input("info-line", "n_clicks"),
     Input("close-info-line-btn", "n_clicks")],
    [State("modal-line-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-filter-chart", "is_open"),
    [Input("filter-syntax", "n_clicks"),
     Input("close-info-filter-btn", "n_clicks")],
    [State("modal-filter-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-heat-chart", "is_open"),
    [Input("info-heatmap", "n_clicks"),
     Input("close-info-heatmap-btn", "n_clicks")],
    [State("modal-heat-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal-box-chart", "is_open"),
    [Input("info-box-plot", "n_clicks"),
     Input("close-info-box-btn", "n_clicks")],
    [State("modal-box-chart", "is_open")],
)
def info_about_map_chart(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(Output('map-chart', 'style'),
              Output('map-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('dropdown-geo-code', 'value'),
               State('storage-for-data', 'data')])
def suggest_map_chart(n_clicks, columns, rows,geo, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    t = []
    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                if len(dimensions) > 2 and len(type_of_feature)>1:
                 if type_of_feature[columns[0]] == "Latitude" and type_of_feature[rows[0]] == "Longitude":
                    stil = {"opacity": "1.0"}
                    t.append(stil)
                    t.append(False)
                    return t
        if geo is not None:
            stil = {"opacity": "1.0"}
            t.append(stil)
            t.append(False)
            return t
    return reset_opacity,True


@app.callback(Output('pie-chart', 'style'),
              Output('pie-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_pie_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in  dash.callback_context.triggered][0]
    t = []
    if 'check-for-chart' in changed_id:
            if columns is not None and rows is not None:
                if len(columns) == 1 and len(rows) == 1 and columns[0] in dimensions and rows[0] in measures:
                    stil = {"opacity": "1.0"}
                    t.append(stil)
                    t.append(False)
                    return t
    return reset_opacity,True


@app.callback(Output('histogram-chart', 'style'),
              Output('histogram-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_histogram_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is None and rows is not None:
            if len(rows) == 1 and rows[0] in measures:
                stil = {"opacity": "1.0"}
                return stil, False

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(rows) == 1 and rows[0] in measures and len(columns)==0:
                stil = {"opacity": "1.0"}
                return stil, False

    return reset_opacity,True


@app.callback(Output('bar-chart', 'style'),
               Output('bar-chart', 'disabled'),
              Input('check-for-chart','n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows','value'),
               State('storage-for-data', 'data')])
def suggest_bar_chart(n_clicks,columns,rows,data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    t = []
    if 'check-for-chart' in changed_id:
             if columns is not None and rows is not None:
               if len(columns) == 1 and len(rows)==1 and columns[0] in dimensions and rows[0] in measures:
                    stil = {"opacity":"1.0"}
                    t.append(stil)
                    t.append(False)
                    return t
    return reset_opacity,True

@app.callback(Output('scatter-chart', 'style'),
              Output('scatter-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_scatter_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                if columns[0] in measures and rows[0] in measures:
                    stil = {"opacity": "1.0"}
                    return stil, False
    return reset_opacity,True

@app.callback(Output('bubble-chart', 'style'),
              Output('bubble-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_bubble_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                    if columns[0] in measures and rows[0] in measures:
                        stil = {"opacity": "1.0"}
                        return stil, False

    return reset_opacity,True

@app.callback(Output('bubble-maps-chart', 'style'),
              Output('bubble-maps-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('dropdown-geo-code', 'value'),
               State('storage-for-data', 'data')])
def suggest_bubble_maps_chart(n_clicks, columns, rows,geo, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    t=[]
    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                if len(dimensions) > 2 and len(type_of_feature)>1:
                    if type_of_feature[columns[0]] == "Latitude" and type_of_feature[rows[0]] == "Longitude":
                        stil = {"opacity": "1.0"}
                        return stil, False
        if geo is not None:
            stil = {"opacity": "1.0"}
            t.append(stil)
            t.append(False)
            return t
    return reset_opacity,True

@app.callback(Output('density-maps-chart', 'style'),
              Output('density-maps-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_density_maps_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(type_of_feature)>1:
                if len(dimensions) > 2:
                    if len(columns) == 1 and len(rows) == 1 :
                        if type_of_feature[columns[0]] == "Latitude" and type_of_feature[rows[0]] == "Longitude" :
                            stil = {"opacity": "1.0"}
                            return stil, False
    return reset_opacity,True

@app.callback(Output('scatter-maps-chart', 'style'),
              Output('scatter-maps-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_scatter_maps_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(type_of_feature) >1 and len(dimensions) > 2:
                if len(columns) == 1 and len(rows) == 1:
                    if type_of_feature[columns[0]] == "Latitude" and type_of_feature[rows[0]] == "Longitude":
                      stil = {"opacity": "1.0"}
                      return stil, False
    return reset_opacity,True



@app.callback(Output('line-chart', 'style'),
              Output('line-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_line_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                if columns[0] in date_time and rows[0] in measures:
                    stil = {"opacity": "1.0"}
                    return stil, False
    return reset_opacity,True



@app.callback(Output('heat-chart', 'style'),
              Output('heat-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_heatmap_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                if columns[0] in measures and rows[0] in measures:
                    stil = {"opacity": "1.0"}
                    return stil, False
    return reset_opacity,True


@app.callback(Output('box-plot-chart', 'style'),
              Output('box-plot-chart', 'disabled'),
              Input('check-for-chart', 'n_clicks'),
              [State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data')])
def suggest_box_chart(n_clicks, columns, rows, data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'check-for-chart' in changed_id:
         if columns is not None and rows is not None:
            if (len(columns) == 1 and len(rows) == 1):
                if columns[0] in measures and rows[0] in dimensions:
                    stil = {"opacity": "1.0"}
                    return stil, False
         elif columns is not None:
             if (len(columns) == 1):
                if rows is None or len(rows)==1:
                    if columns[0] in measures:
                        stil = {"opacity": "1.0"}
                        return stil, False
    return reset_opacity,True


def create_agg_variable(features, type_aggregation, value, df):
    if features is not None:
        f = features[0]
        if type_aggregation == 'sum':
            if f in date_time or f in dimensions:
                    return df.groupby([features[0]])[value].agg('sum')
        elif type_aggregation == 'min':
            if f in date_time or f in dimensions:
                 return df.groupby([f])[value].agg('min')
        elif type_aggregation == 'max':
            if f in date_time or f in dimensions:
                    return df.groupby([f])[value].agg('max')
        elif type_aggregation == 'avg':
            if f in date_time or f in dimensions:
                    return df.groupby([f])[value].agg('mean')
        elif type_aggregation == 'count':
            # TO DO
            if f in date_time or f in dimensions:
                    return df.groupby([f])[value].agg('count')

@app.callback(Output('div-for-filtering', 'children'),
              Input('dropdown-filter', 'value'),
              State('storage-for-data', 'data')
              )
def show_filter_options(values, data):
    df = pd.DataFrame.from_dict(data)
    htmlCode = []
    if values is not None:
        for i in range(0, len(values)):
            if values[i] in dimensions or values[i] in date_time:
                htmlCode.append(dbc.Checklist(
                    id="filter",
                    options=[
                        {'label': df[values[i]].unique()[j], 'value': df[values[i]].unique()[j]} for j in
                        range(0, df[values[i]].nunique())
                    ]
                ))
                htmlCode.append(html.Button("Filter",id="filter-button"))
                htmlCode.append(html.P("Deselect, and press button first to undo filtering"))
                return htmlCode
            elif values[i] in measures:
                htmlCode.append(dcc.RangeSlider(
                    id='filter',
                    min=df[values[i]].min(),
                    max=df[values[i]].max(),
                    step=math.log2(df[values[i]].max()),
                    value=[df[values[i]].min(), df[values[i]].max()],
                    marks={df[values[i]].min():str(df[values[i]].min()),
                           df[values[i]].max():str(df[values[i]].max())}
                ))
                htmlCode.append(html.Button("Filter", id="filter-button"))
                htmlCode.append(html.P("Deselect, and press button first to undo filtering"))
                return htmlCode
    else:
        raise PreventUpdate


@app.callback(Output('storage-for-figure', 'data'),
              Input('filter-button', 'n_clicks'),
              State('filter','value'),
              State('dropdown-filter', 'value'),
                )
def save_marks(filter_btn,filter,feature):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "filter-button" in changed_id and isinstance(feature[0],str) and filter_btn is not None and filter is not None:
        if filter_btn > 0:
            return {"filter": filter,"feature":feature}
    else:
        raise PreventUpdate


filtered = False
df_filtered = pd.DataFrame()


@app.callback(Output('current-graph', 'figure'),
              [Input('map-chart', 'n_clicks'),
               Input('scatter-maps-chart', 'n_clicks'),
               Input('density-maps-chart', 'n_clicks'),
               Input('bubble-maps-chart', 'n_clicks'),
               Input('bar-chart', 'n_clicks'),
               Input('pie-chart', 'n_clicks'),
               Input('scatter-chart', 'n_clicks'),
               Input('bubble-chart', 'n_clicks'),
               Input('line-chart', 'n_clicks'),
               Input('histogram-chart', 'n_clicks'),
               Input('heat-chart', 'n_clicks'),
               Input('box-plot-chart', 'n_clicks'),
              Input('storage-for-figure', 'data')],
              [ State('dropdown-columns', 'value'),
               State('dropdown-rows', 'value'),
               State('storage-for-data', 'data'),
               State('dropdown-size','value'),
               State('dropdown-detail','value'),
               State('dropdown-color','value'),
               State('size-slider','value'),
               State('radioitems-colorscale','value'),
               State('dropdown-geo-code','value')
               ])
def show_chart(a, b, c, d, e, f, g, h, j, i, k, l, store, columns, rows, data,size, detail, color,slider_size,colorscale,short_code):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # koja slicica je kliknuta
    # # mapu zelimo da prikazemo
    global filtered
    global df_filtered
    global geo_names
    global geo_short
    global geo_okruzi

    if "storage-for-figure" in changed_id:
        if filtered != True:
            df = pd.DataFrame.from_dict(data)
            df_filtered = df
        feature = store['feature'][0]
        if feature is not None and len(store['filter'])>0:
            if feature in dimensions:
                df_filtered = df_filtered[df_filtered[feature].isin(store['filter'])]
            elif feature in date_time: # ukoliko je datum, ispitaj da li je u reprezentaciji stringa ili broja. pa vrati filtrirane godine
                if isinstance(df_filtered[feature][0],str):
                    df_filtered = df_filtered[df_filtered[feature].isin(store['filter'])]
                else:
                    df_filtered = df_filtered[df_filtered[feature] == store['filter'][0]]
            else: # ukoliko je u pitanju measure, ogranici feature sa min i max uzetih sa slajdera za filtriranje num vrednosti
                df_filtered = df_filtered[df_filtered[feature] >= store['filter'][0]]
                df_filtered = df_filtered[df_filtered[feature] <= store['filter'][1]]

            filtered = True
        else:
            filtered = False

    if "map-chart" in changed_id:

        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered
        # if color in measures and colorscale != '':
        key=""
        # ako je kolona code od 3 karaktera
       # if len(df[short_code][0]) == 3:
        #    key="properties.ISO_A3"
        #else:
        #    key="properties.ADMIN"

        fig = px.choropleth_mapbox(df,
                               #geojson=regioni_srbija,
                               geojson=regioni_slovenija,
                               locations=short_code,
                               featureidkey="properties.name",
                               color=color,
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               zoom=3, center={"lat": 40.7000, "lon": 5.7129},
                               opacity=1.0,hover_data=detail)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig
    # el if...

        # bar chart zelimo da prikaze app
    if "bar-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered
        if len(columns) == 1 and len(rows) == 1:
                # ispitati da li je horizontalni
                # ili vertikalni - drugaciji raspored tipova feautura
                xx = columns[0]
                yy = rows[0]
                if color is None:
                    fig = px.bar(df, x=df[xx], y=df[yy],hover_data=detail)
                else:
                    if color in date_time:
                        fig = px.bar(df, x=df[xx], y=df[yy], color=df[color], hover_data=detail,color_continuous_scale=colorscale)

                    else:
                        fig = px.bar(df, x=df[xx], y=df[yy],color=df[color],hover_data=detail)
                return fig
        elif len(columns) > 1 and len(rows) > 1:
            # do extra things
            raise PreventUpdate
        else:
            raise PreventUpdate

    if "pie-chart" in changed_id and len(columns) == 1 and len(rows) == 1:

        df = pd.DataFrame.from_dict(data)
        if filtered:
            df = df_filtered
        if columns[0] in dimensions:
            names = columns[0]  # dimension
            values = rows[0]  # measure
        else:
            values = columns[0]  # measure
            names = rows[0]  # dimension
        fig = px.pie(df, values=values, names=names, title="Pie chart for " + names,hover_data=detail)
        return fig
    # do extra things for num = 2 columns, cat 1

    if "histogram-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered
        fig = px.histogram(df, x=rows[0],hover_data=detail)
        # listen for nbins
        return fig

    if "scatter-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered
         # and
        if len(columns) == 1 and len(rows) == 1:
            if columns[0] in measures and rows[0] in measures:
                if size is not None and size in measures or size in date_time:
                    if (color in measures or color in date_time) and colorscale != '':
                        fig = px.scatter(df, columns[0], rows[0], hover_data=detail, size=size, color=color,
                                         color_continuous_scale=colorscale,size_max=slider_size)
                    else:
                        fig = px.scatter(df, columns[0], rows[0],hover_data=detail,size=size,color=color,size_max=slider_size)
                    return fig
                else:
                    if (color in measures or color in date_time) and colorscale != '':
                         fig = px.scatter(df, columns[0], rows[0], hover_data=detail, color=color,
                                         color_continuous_scale=colorscale,size_max=slider_size)
                    else:
                         fig = px.scatter(df, columns[0], rows[0],hover_data=detail,color=color)
            return fig

    #
    # if "bubble-chart" in changed_id:
    #
        #   aggregation sum of both
        # show on axis. Listen for measure or dimension for color, size, and label for SIMPLE
        # ENABLE ANIMATION OPTION THROUGH SELECTED TIME SERIES - YEARS, MONTHS...

    if "line-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered

        fig = px.line(df, x=columns[0], y=rows[0], color=color,title=rows[0] + " through time",hover_data=detail)
        fig.update_traces(mode="markers+lines")
        return fig

        # scale same axis - merge axis
        # do aggregation sum for rows. place on same chart different lines
        # show legend
        # forecast osposobi neki algoritam
        # koji ce da predvidi desavanja u narednom periodu sa measures
        # prikazati na chartu sa manjim opacity

    if "heat-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered

        if (color in measures or color in date_time):
            fig = px.density_heatmap(df, x=columns[0], y=rows[0],hover_data=detail,color_continuous_scale=colorscale)
            return fig
        else:
            fig = px.density_heatmap(df, x=columns[0], y=rows[0],hover_data=detail)
            return fig

    if "box-plot-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered

        if columns is not None and rows is not None:
            if len(columns) == 1 and len(rows) == 1:
                fig = px.box(df, x=columns[0], y=rows[0],hover_data=detail,color=color)
                return fig
        else:
            fig = px.box(df, y=columns[0], hover_data=detail,color=color)
            return fig

    # if "scatter-maps-chart" in changed_id:
        # listen for color, size, color_continuous_scale, size_max, zoom
    #             # .. hover_name...
    #   px.set_mapbox_access_token(open(".mapbox_token").read())
    #           fig = px.scatter_mapbox(...)
    #           return fig
    #             # ICON LOOKING
    #
    #
    if "density-maps-chart" in changed_id:
         df = pd.DataFrame.from_dict(data)
         if filtered != False:
            df = df_filtered
         # listen for z=size, radius, zoom, mapbox_style
         if (color in measures or color in date_time):
                fig = px.density_mapbox(df, lat=columns[0],lon=rows[0], z=detail,color_continuous_scale=colorscale, radius=slider_size,
                            center=dict(lat=0, lon=180), zoom=0,
                            mapbox_style="stamen-terrain")
         else:
                fig = px.density_mapbox(df, lat=columns[0],lon=rows[0], z=detail, radius=slider_size,
                            center=dict(lat=0, lon=180), zoom=0,
                            mapbox_style="stamen-terrain")
         return fig

    if "bubble-maps-chart" in changed_id:
        df = pd.DataFrame.from_dict(data)
        if filtered != False:
            df = df_filtered

        key = ""
        if short_code is not None:
            if len(df[short_code][0]) == 3:
                key = "ISO_A3"
            elif len(df[short_code][0]) > 3:
                df_filtered = df
                df = df_filtered.replace(geo_names, geo_short)
                key="NAMES"
            else:
                pass

        if size is not None and color is not None:
            # LISTEN FOR PARAMETERS :
            #HOVER NAME/detail,
            #enable ANIMAION_FRAME=YEAR
            if key != "":
                fig = px.scatter_geo(df, locations= short_code,size=size,color=color,hover_data=detail,size_max=slider_size)
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                return fig
            else:
                fig = px.scatter_geo(df, lat=columns[0], lon=rows[0], size=size, color=color, hover_data=detail,
                                     size_max=slider_size)
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                return fig

        elif size is None and color is not None:
            if key == "":
                fig = px.scatter_geo(df, lat=columns[0],lon=rows[0],color=df[color],hover_data=detail,size_max=slider_size)
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                return fig
            else:
                fig = px.scatter_geo(df,locations=short_code,color=df[color],hover_data=detail,size_max=slider_size)
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                return fig
        elif size is not None and color is None:
            if key == "":
                    fig = px.scatter_geo(df, lat=columns[0], lon=rows[0], size=df[size],hover_data=detail,size_max=slider_size)
                    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                    return fig
            else:
                fig = px.scatter_geo(df, locations=short_code, size=df[size], hover_data=detail,
                                     size_max=slider_size)
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                return fig
    else:
        return dash.no_update
    #     ### FOLIUM BIBLIOTEKA https://python-visualization.github.io/folium/quickstart.html#Getting-Started ####


# CALLBACK ZA PRIKAZ T1 TABA (za sredjivanje) ili T2 TABA (za vizuelizaciju podataka)

@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value'),
               Input("storage-for-data", "data")])
def render_content(tab, data):
    global measures
    global dimensions
    global date_time
    df = pd.DataFrame.from_dict(data)
    max_appearance = np.zeros(df.columns.size)
    if tab!= '':
        if data is not None:

            # ukoliko je izabran prvi tab, prikazi sadrzaj za sredjivanje podataka
            if tab == 'Data':

                #malo skuplja operacija...
                for i in range(0, df.columns.size):
                    # max_appearance[i] = -1
                    for j in range(0, df[df.columns[i]].nunique() - 1):
                        num_of_occurance = df[df[df.columns[i]].unique()[j] == df[df.columns[i]]].shape[0]
                        if max_appearance[i] < num_of_occurance:
                            max_appearance[i] = num_of_occurance

                sum(max_appearance)

                return html.Div(className="container testimonial-group", children=[
                    html.Div(
                        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom",
                        children=[
                            html.H1("Data preparation", className="h2"),
                            # html.Div(className="btn-toolbar mb-2 mb-md-0", children=[
                            #     html.Div(className="btn-group mr-2", children=[
                            #         html.Button("Share", type="button", className="btn btn-sm btn-outline-secondary"),
                            #         html.Button("Export", type="button", className="btn btn-sm btn-outline-secondary")
                            #     ]),
                            #     html.Button("This week", type="button",
                            #                 className="btn btn-sm btn-outline-secondary dropdown-toggle")
                            # ]),
                        ]),
                    dbc.ButtonGroup(children=[
                        dbc.DropdownMenu([
                            dbc.DropdownMenuItem("NULL values", id="remove-nulls-btn", n_clicks=0),
                            dbc.DropdownMenuItem("Whole column", id="remove-column-btn", n_clicks=0),
                        ], label="Remove", className="m-1", color="primary", direction="right", group=True,
                        ),
                        dbc.Button("Standardize", className="m-1", id="standardize-btn", n_clicks=0),
                        dbc.Button("Rename Column", id="rename-btn", n_clicks=0, className="m-1"),
                        dbc.DropdownMenu([
                            dbc.DropdownMenuItem("to String", id="change-to-string"),
                            dbc.DropdownMenuItem("to Int", id="change-to-int"),
                            dbc.DropdownMenuItem("to Date", id="change-to-date",header=True),
                            dbc.DropdownMenuItem("Geographic role", header=True),
                            dbc.DropdownMenuItem("to Longitude", id="change-to-longitude",header=True),
                            dbc.DropdownMenuItem("to Latitude", id="change-to-latitude",header=True),
                            dbc.DropdownMenuItem("to Country", id="change-to-country",header=True),
                        ],  # dodati textarea po kliku na TEXT za dva parametra,
                            # ostali samo za jedan parametar
                            label="Change type", color="success", className="m-1", group=True),
                        dbc.DropdownMenu([
                            dbc.DropdownMenuItem("Text", id="text-btn"),
                            dbc.DropdownMenuItem("Replace NULL with:", header=True),
                            dbc.DropdownMenuItem("Custom Value", id="custom-value-btn"),
                            dbc.DropdownMenuItem("Average", id="average-btn"),
                            dbc.DropdownMenuItem("Mode", id="mode-btn")
                        ],  # dodati textarea po kliku na TEXT za dva parametra,
                            # ostali samo za jedan parametar
                            label="Find & Replace", color="secondary", className="m-1", group=True),
                        # dbc.Button("Count text matches", id="count-btn", className="m-1"),
                        dbc.Button("Group By",id="groupby-btn", color="info", className="m-1"),
                        # dbc.DropdownMenu([
                        #
                        # ], label="Math Functions", id="math-func", color="warning", className="m-1", group=True),
                    ]),

                    dcc.Dropdown(
                        options=[
                            {'label': df.columns[i], 'value': df.columns[i]} for i in range(0, df.columns.size)
                        ],
                        multi=True,
                        placeholder="First select column(s) and then action from buttons above",
                        id="selected-columns"
                    ),
                    html.Br(),
                    html.Div([
                        dbc.Toast([
                            dbc.Input(id="to-replace", type="text", placeholder="Text to replace"),
                            html.Br(),
                            dbc.Input(id="value", type="text", placeholder="New Text Value"),
                            dbc.Button('Confirm', className="mt-2", color="primary", id='confirm-replacing-btn', n_clicks=0)

                        ],
                            id="find-and-replace-toast",
                            header="Find and Replace Text",
                            icon="primary",
                            dismissable=True,
                            className="toast",
                            is_open=False),
                        dbc.Toast([
                            dbc.Input(
                                id='replace-with-custom-value-input',
                                placeholder="Enter custom value...",
                                value='',
                                type="number",

                            ),

                            dbc.Button('Replace', className="mt-2", color="primary", id='replace-with-value-btn',
                                       n_clicks=0)
                        ],
                            id="replace-with-value-toast",
                            dismissable=True,
                            header="Replace NULL with custom value",
                            icon="primary",
                            className="toast",
                            is_open=False),
                        dbc.Toast([

                            # dbc.DropdownMenuItem("SUM", id="sum-btn"),
                            # dbc.DropdownMenuItem("AVG", id="avg-btn"),
                            # dbc.DropdownMenuItem("MIN", id="min-btn"),
                            # dbc.DropdownMenuItem("MAX", id="max-btn"),
                            # dbc.DropdownMenuItem("Group by and Count", id="group-by-and-count-btn"),
                            dbc.Label("Value:"),
                            app.logger.info("message"),
                            dcc.Dropdown(
                                options=[
                                    {'label': measures[i], 'value': measures[i]} for i in range(0, len(measures))
                                ],
                                id='groupby-value-input',
                                placeholder="Value for selected aggregation function...",

                            ), dbc.Label("Choose the aggregation function"),
                            dbc.RadioItems(options=[
                                {"label": "SUM","value":1},
                                {"label": "AVG","value":2},
                                {"label": "MIN","value":3},
                                {"label": "MAX","value":4},
                                {"label": "Group by and COUNT","value":5},
                                ],
                            value=1,
                            id="agg-radio-btn"),
                            html.Br(),

                            # dbc.Checklist(options=[
                            #     {"label":"Group by as new column","value":1},
                            #    ],
                            #     value=[],
                            #     id="add-col-switch",
                            #     switch=True
                            # ),
                            dbc.Button('Group By', className="mt-2", color="primary", id='confirm-group-by',
                                       n_clicks=0)
                        ],
                            id="groupby-toast",
                            dismissable=True,
                            header="Measure column for Aggregation",
                            icon="primary",
                            className="toast",
                            is_open=False),
                        dbc.Toast([
                            dbc.Input(
                                id='text-to-count-input',
                                placeholder="Enter text to count...",
                                value='',
                                type="text"
                            ),
                            dbc.Button('Count text', className="mt-2", color="warning", id='text-to-count-btn',
                                       n_clicks=0),
                            dbc.Checklist(
                                options=[
                                    {"label": "Add counted column", "value": 1}],
                                id='add-column-counted-btn',
                                value=[]
                            )
                        ],
                            id="text-to-count-toast",
                            dismissable=True,
                            header="Text to count",
                            icon="warning",
                            className="toast",
                            is_open=False),
                        dbc.Toast([
                            dbc.Input(
                                id='rename-column-input',
                                placeholder="Enter column's new name...",
                                value='',
                                type="text"
                            ),

                            dbc.Button('Rename Column', className="mt-2", color="info", id='rename-column-button', n_clicks=0)
                        ],
                            id="add-column-toast",
                            dismissable=True,
                            header="Rename column",
                            icon="info",
                            className="toast",
                            is_open=False
                            ),
                    ], className="grid-figure-container row text-center",
                        style={"display": "grid", "gridTemplateColumns": "auto auto auto auto"}),
                    html.Br(),
                    html.Div(className="row text-center", children=[
                        html.Div(n_clicks=0, children=[
                            # rad sa frejmom i filtriranje podataka
                            # vrsta podataka
                            html.P("Kategorijska kolona" if df.columns[i] in dimensions else "Numerička kolona" if df.columns[i] in measures else "Vremenska(kalendar) kolona", className="category-id"),

                            # ime featurea
                            html.H6([df.columns[i]], className="feature-name"),

                            # broj jedinstvenih vrednosti
                            html.P(df[df.columns[i]].nunique(), className="num-unique-value"),
                            html.Hr(),

                            # jedinstvene vrednosti po broju/procentu. gde je vrednost sa najvise
                            html.Ul(className="list-group mr-3", children=[
                                html.Li(style={'position': 'relative'},
                                        children=[
                                            dbc.Progress(style={"height": "25px"}, className="unique-progress",
                                                         color="info", value=(df[df[df.columns[i]].unique()[j] == df[
                                                    df.columns[i]]].shape[0] / max_appearance[i]) * 100),
                                            html.Div([
                                                html.P(df[df.columns[i]].unique()[j], className="d-inline"),
                                                html.P(" (" + str(
                                                    df[df[df.columns[i]].unique()[j] == df[df.columns[i]]].shape[0]) + ")",
                                                       className="d-inline")
                                            ],
                                                className="unique-div d-inline",
                                                style={'position': 'absolute', 'left': '0', 'top': 0, 'color': 'black',
                                                       'overflow': 'hidden', 'width': '100%'})
                                        ], className="mb-1") for j in range(0, df[df.columns[i]].nunique())

                                # html.Li(df[df.columns[i]].unique()[j], className="list-group-item p-3 mb-2 bg-info text-white",
                                #         style={"width": str((df[df[df.columns[i]].unique()[j]==df[df.columns[i]]].shape[0]/max_appearance[i])*100)+"%"})
                            ])

                            # df[df[df.columns[0]].unique()[1]==df[df.columns[0]]].shape[0]
                        ], className="col-3 mr-2 bg-light shadow-sm border rounded")
                        for i in range(0, df.columns.size)
                    ]),
                    # table,
                ]),
        # prikaz sadrzaja za drugi tab kada se ucitaju podaci
            elif tab == 'Visualisation':
                return html.Div([
                    html.Div(className="container", children=[
                        html.Div(className="row ui-for-eda", children=[
                            # srednji deo - trenutni graf/plot/figura
                            html.Div(className="col-10", children=[
                                html.Div(className="row", style={"height": "100%"}, children=[
                                    html.Div(className="col-2 p-0", children=[
                                        html.Label("After changing any of paramaters below, click again on CHART IMAGE at right for rendering the new graph"),
                                        html.Br(),
                                        html.Label("Color"),
                                        # daq.ColorPicker(
                                        #     id='colorpicker',
                                        #     label="Choose color",
                                        #     size=150
                                        # ),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': df.columns[i], 'value': df.columns[i]} for i in
                                                range(0, df.columns.size)
                                            ],
                                            id="dropdown-color"
                                        ),
                                        html.Br(),
                                        html.H6("Detail"),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': df.columns[i], 'value': df.columns[i]} for i in
                                                range(0, df.columns.size)
                                            ],
                                            id="dropdown-detail",
                                            multi=True
                                        ),
                                        html.Hr(),
                                        html.H6("Size"),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': df.columns[i], 'value': df.columns[i]} for i in
                                                range(0, df.columns.size)
                                            ],
                                            id="dropdown-size"
                                        ),
                                        html.Br(),
                                        html.H6("Adjust size"),
                                        dcc.Slider(
                                            id='size-slider',
                                            min=10,
                                            max=80,
                                            step=5,
                                            value=20,
                                        ),

                                        html.Br(),
                                        html.P("Filter data"),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': df.columns[i], 'value': df.columns[i]} for i in
                                                range(0, df.columns.size)
                                            ],
                                            id="dropdown-filter",
                                            multi=True,
                                        ),
                                        html.Div(id="div-for-filtering"),
                                        html.Hr(),
                                        # to do add callback for putting value in storage-for-figure
                                        html.Div([
                                            dbc.RadioItems(
                                                options=[
                                                    {'label': '', 'value': x} for x in colorscales
                                                ],
                                                value='',
                                                id="radioitems-colorscale"
                                            ),
                                            html.Ul([
                                                html.Li([], className="bluered"),
                                                html.Li([], className="cividis"),
                                                html.Li([], className="darkmint"),
                                                html.Li([], className="greys"),
                                                html.Li([], className="inferno"),
                                                html.Li([], className="portland"),
                                                html.Li([], className="viridis")
                                            ], style={"position": "relative"})], className="d-inline",
                                            style={'position': 'relative'}),
                                        html.Hr(),
                                        # html.H6("Faced rows"),
                                        # dcc.Dropdown(
                                        #     options=[
                                        #         {'label': df.columns[i], 'value': df.columns[i]} for i in
                                        #         range(0, df.columns.size)
                                        #     ],
                                        #     id="dropdown-faced-rows",
                                        #     multi=True
                                        # ),
                                        # html.H6("Faced column(s)"),
                                        # dcc.Dropdown(
                                        #     options=[
                                        #         {'label': df.columns[i], 'value': df.columns[i]} for i in
                                        #         range(0, df.columns.size)
                                        #     ],
                                        #     id="dropdown-faced-cols",
                                        #     multi=True
                                        # ),
                                    ]),
                                    html.Div(className="col-10", children=[
                                        html.Br(),
                                        html.Div(className="row ml-1 mr-3 mb-1 bg-primary border rounded", children=[
                                            html.P("Kolone", className="col-sm-3 text-light font-weight-bold"),
                                            html.Div([
                                                dcc.Dropdown(
                                                    options=[
                                                        {'label': df.columns[i], 'value': df.columns[i]} for i in
                                                        range(0, df.columns.size)
                                                    ],
                                                    multi=True,
                                                    id="dropdown-columns"
                                                )
                                            ], className="col-sm p-1")
                                        ]),
                                        html.Div(className="row ml-1 mr-3 mb-1 bg-primary border rounded", children=[
                                            html.P("Vrste", className="col-sm-3 text-light font-weight-bold"),
                                            html.Div([
                                                dcc.Dropdown(
                                                    options=[
                                                        {'label': df.columns[i], 'value': df.columns[i]} for i in
                                                        range(0, df.columns.size)
                                                    ],
                                                    multi=True,
                                                    id="dropdown-rows"
                                                )
                                            ], className="col-sm p-1")
                                        ]),
                                        dbc.Button(["Izaberi grafikon"], id="check-for-chart", n_clicks=0, color="primary",
                                                   className="ml-1"),
                                        html.Div(className="row", children=[
                                            dcc.Graph(
                                                id='current-graph',

                                            )
                                        ]),
                                    ]),
                                ]),
                            ]),

                            # preporuceni grafovi/plotovi/figure
                            html.Div(className="col-2", children=[
                                ### MODALS FOR INFO ABOUT CHARTS ###
                                dbc.Modal([
                                    dbc.ModalHeader("Map chart header"),
                                    dbc.ModalBody("Choose COUNTRY NAME or SHORT CODE from dropmenu"),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-map-btn", className="ml-auto")
                                    )
                                ], id="modal-map-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Scatter map header"),
                                    dbc.ModalBody("unavailable for now"),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-scatter-map-btn", className="ml-auto")
                                    )
                                ], id="modal-scatter-map-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Density map chart header"),
                                    dbc.ModalBody("In column dropmenu choose LATITUDE. In row dropdown choose LONGITUDE. If coords are not in dataset, choose COUNTRY NAME or SHORT CODE from dropmenu"),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-density-map-btn", className="ml-auto")
                                    )
                                ], id="modal-density-map-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Bubble map chart header"),
                                        dbc.ModalBody("In column dropmenu choose LATITUDE. In row dropdown choose LONGITUDE. If coords are not in dataset, choose COUNTRY NAME or SHORT CODE from dropmenu. Separate by SIZE choosing feature from sidebar"),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-bubble-map-btn", className="ml-auto")
                                    )
                                ], id="modal-bubble-map-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for showing bar chart"),
                                    dbc.ModalBody("In column dropmenu choose ONE dimension. In row dropdown choose ONE measure."),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-bar-btn", className="ml-auto")
                                    )
                                ], id="modal-bar-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for showing Pie chart"),
                                    dbc.ModalBody("In column dropmenu choose ONE dimension. In row dropdown choose ONE measure."),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-pie-btn", className="ml-auto")
                                    )
                                ], id="modal-pie-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for showing Scatter chart"),
                                    dbc.ModalBody([html.P("In column dropmenu choose ONE measure."),html.P("In row dropdown choose ONE measure.")]),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-scatter-btn", className="ml-auto")
                                    )
                                ], id="modal-scatter-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for Bubble chart "),
                                    dbc.ModalBody("In column dropmenu choose ONE measure. In row dropdown choose ONE measure. On sidebar, choose ONE measure to separate by SIZE"),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-bubble-btn", className="ml-auto")
                                    )
                                ], id="modal-bubble-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for Line chart"),
                                    dbc.ModalBody("In column dropmenu choose ONE date. In row dropdown choose ONE measure."),
                                    dbc.ModalFooter(
                                        dbc.Button("Zatvori", id="close-info-line-btn", className="ml-auto")
                                    )
                                ], id="modal-line-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for Histogram chart"),
                                    dbc.ModalBody("In rows dropdown choose ONE measure."),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-info-histogram-btn", className="ml-auto")
                                    )
                                ], id="modal-histogram-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for Heatmap chart"),
                                    dbc.ModalBody("In column dropmenu choose ONE measure. In row dropdown choose ONE measure."),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-info-heatmap-btn", className="ml-auto")
                                    )
                                ], id="modal-heat-chart"),
                                dbc.Modal([
                                    dbc.ModalHeader("Paramaters for Box-plot chart"),
                                        dbc.ModalBody("In column dropmenu choose ONE measure. In row dropdown choose ZERO/ONE dimension."),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-info-box-btn", className="ml-auto")
                                    )
                                ], id="modal-box-chart"),
                                #################
                                html.Div([
                                dbc.Label("If coordinates aren't available (1,2 & 4 type of maps):",className="text-light"),
                                dcc.Dropdown(
                                    options=[
                                        {'label': dimensions[i], 'value': dimensions[i]} for i in
                                        range(0, len(dimensions))
                                    ],
                                    id="dropdown-geo-code",
                                    placeholder="choose country/code"
                                )], className="bg-primary"),
                                html.Div(choose_figure),
                                dcc.Store(id="storage-for-figure", storage_type="memory"),
                                html.Div([

                                ], className="row justify-content-start"),
                            ]),
                        ]),
                    ]),
                ]),


# Layout aplikacije
app.layout = html.Div(children=[nav_bar,
                                html.Div(className="container-fluid", children=[
                                    html.Div(className="row", children=[
                                        html.Nav(className="col-md-3 col-lg-2 d-md-block bg-primary sidebar collapse",
                                                 id="sidebarMenu", children=[
                                                html.Div(className="sidebar-sticky pt-3", children=[

                                                ], id="sidebar-features")
                                            ]),

                                        html.Main(role="main", className="col-md-9 ml-sm-auto col-lg-10 px-md-4",
                                                  children=[
                                                      upload_component,
                                                  ])
                                    ])
                                ]),
                                html.Script(src="https://code.jquery.com/jquery-3.5.1.slim.min.js",
                                            integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj",
                                            crossOrigin="anonymous"),
                                html.Script(
                                    src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.9.0/feather.min.js"),
                                html.Script(src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js"),
                                html.Script("dashboard.js")
                                ])

if __name__ == '__main__':
    app.run_server(debug=True)
