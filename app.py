import json

import dash
import dash_auth
import numpy as np
import pandas as pd
from dash import dcc, html, dash_table, Output, Input, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

from data_preparation import schools_meta, best_schools, merged, haversine
from zoopla_api import simple_request, get_floor_area, prepare_link, prepare_image_link

px.set_mapbox_access_token(open(".mapbox_token").read())
import gmaps

with open('pass.txt', 'r') as f:
    VALID_USERNAME_PASSWORD_PAIRS = json.load(f)


fig = px.scatter_mapbox(merged, lat="lat", lon="lng", color="Type", text='School', size = np.ones(len(merged))*15,
                        color_continuous_scale=px.colors.cyclical.IceFire, zoom=10)
fig.update_layout(mapbox_style="streets")

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
    # meta_tags=[
    #     {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    # ],
)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.title = "Schools_houses"
server = app.server

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("School Type"),
                dcc.Dropdown(
                    id="school_type",
                    options=['Independent', 'State', 'All'],
                    value="All",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("School age"),
                dcc.Dropdown(
                    id="school_age",
                    options=['Primary', 'Secondary', 'Both'],
                    value="Both",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Gender"),
                dcc.Dropdown(
                    id="gender",
                    options=['Boys', 'Girls', 'Both'],
                    value="Both",
                ),
            ]
        ),
    ],
    body=True,
)

school_data = dbc.Card(
    [
        html.Div(dbc.Label("School info")),
        html.Div(html.Button('Search houses', id='get_zoopla', n_clicks=0)),
        html.Div(id='school_info',
            children = []
        ),
    ],
    body=True,
)

houses = dbc.Card(
    [
        dbc.Label("Houses data"),
        html.Div(id='houses',
            children = []
        ),
    ],
    body=True,
)


app.layout = dbc.Container(
    [
        html.H1("Schools and houses map"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(html.Div(id='map_container', children = [dcc.Graph(id="map", figure=fig)]), md=8),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(school_data, md=4),
                dbc.Col(houses, md=8),
            ],
            align="start",
        ),
    ],
    fluid=True,
)

@app.callback(
    Output('school_info', 'children'),
    [Input('map', 'clickData')])
def display_click_data(custom_data):
    if custom_data is None:
        return []
    name = custom_data['points'][-1]['text']
    info = merged.loc[merged['School'] == name].iloc[0]
    df = info.dropna().to_frame().reset_index()
    df.columns = ['School', info['School']]
    df = df.loc[df['School'] != 'School']
    return [dash_table.DataTable(
        df.to_dict('records'),
        [{"name": i, "id": i} for i in df.columns]
    )]


@app.callback(
    Output('houses', 'children'),
    # Output('map_container', 'children'),
    Input('get_zoopla', 'n_clicks'),
    State('school_info', 'children'), State('map_container', 'children')
)
def update_output(n_clicks, value, map):
    if n_clicks == 0:
        return (
            [],
            # [dcc.Graph(id="map", figure=fig)]
        )
    data = pd.DataFrame(value[0]['props']['data'])
    data_series = data.set_index('School').iloc[:, 0]
    postcode = data.query('School == "POSTCODE"').iloc[0, 1]
    json = simple_request(postcode)

    dfout = pd.DataFrame([
        {'zoopla': prepare_image_link(listing),
         'title': listing['title'],
         'price': pd.to_numeric(listing['price']),
         'distance_to_school': np.round(haversine(data_series['lng'], data_series['lat'], listing['longitude'], listing['latitude']), 2),
         'floor_area': get_floor_area(listing),
         'floor_plan': prepare_link(listing['floor_plan'][0]) if 'floor_plan' in listing else None,
         'num_bedrooms': listing['num_bedrooms'],
         'num_bathrooms': listing['num_bathrooms'],
         'features': ', '.join(listing['bullet']),
         } for listing in json['listing']])

    mapdf = pd.DataFrame([
        {'longitude': listing['longitude'],
         'latitude': listing['latitude'],
         'description': f"{listing['title'].replace(' for sale', '')}, {pd.to_numeric(listing['price'])}",
         'type': 'House'
         } for listing in json['listing']])

    mapdf = pd.concat([mapdf, pd.DataFrame({'longitude': [data_series['lng']],
                                   'latitude': [data_series['lat']],
                                   'description': [data_series.name.rstrip()],
                                    'type': ['School']})])

    new_fig = px.scatter_mapbox(mapdf, lat="latitude", lon="longitude", color="type", text='description', size=np.ones(len(mapdf)) * 15,
                            color_continuous_scale=px.colors.cyclical.IceFire, zoom=10)
    new_fig.update_layout(mapbox_style="streets")

    return (
        dash_table.DataTable(
            dfout.to_dict('records'),
            [{"name": i, "id": i, "presentation": "markdown"} for i in dfout.columns],
            markdown_options={'html': True},
            sort_action='native',
            page_action="native",
            page_current=0,
            page_size=10,
        ),
        # [dcc.Graph(id="map", figure=new_fig)]
    )



if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=False,
                   use_reloader=False,
                   dev_tools_hot_reload_watch_interval=600.0,
                   dev_tools_hot_reload_interval=600.0)
