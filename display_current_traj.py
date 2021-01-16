import dash
import pandas as pd
import glob
import os

import plotly.graph_objects as go # or plotly.express as px
import plotly

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)


app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig, id = 'live-update-graph'),
    dcc.Interval(
            id='interval-component',
            interval=2*1000, # in milliseconds
            n_intervals=0
        )
])

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    list_of_files = glob.glob('/home/dennis/t265_data_col_system/t265_data/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    time = df.loc[:, 'timestamp'].values/1000
    n_poses = df.shape[0]
    framerate = 1/(time[1:] - time[:-1])
    #fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)

    fig = plotly.subplots.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig.append_trace( go.Scatter(x = df.loc[:, 'posX'].values, y = df.loc[:, 'posZ'].values, mode= 'lines' , name="position"), 1,1)
    fig.append_trace( go.Scatter(x = time[1:], y = framerate, mode='lines', name="framerate"),2,1)
    fig.update_layout(title = "Tracking Conf: {}, Mapping Conf: {}".format(df.loc[:, 'tracking_confidence'].values[-1],
                                                                           df.loc[:, 'mapping_confidence'].values[-1]))
    LAYOUT = {'height': 1000}

    fig['layout'].update(LAYOUT)




    return fig


app.run_server(debug=True, host='0.0.0.0')
