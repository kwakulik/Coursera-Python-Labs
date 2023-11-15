# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()] +
                         [{'label': 'All Sites', 'value': 'ALL'}],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
    ),
    html.Br(),

    # Pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: '{} Kg'.format(i) for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),

    # Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback function for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class', title=f'Total Success Launches for {entered_site}')
    return fig

# Callback function for the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    filtered_df = filtered_df[filtered_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()