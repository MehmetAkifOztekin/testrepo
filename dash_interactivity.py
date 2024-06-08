import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Veri setini indirip yükleyelim
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(url)

# Fırlatma alanlarını alın
launch_sites = spacex_df['Launch Site'].unique()

# Dropdown bileşeni için seçenekler
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Dash uygulaması oluşturma
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='SpaceX Launch Dashboard'),

    html.Div([
        html.Label("Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=dropdown_options,
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
        )
    ]),

    dcc.Graph(id='success-pie-chart'),

    html.Div([
        html.Label("Payload Range (Kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={0: '0', 10000: '10000'},
            value=[0, 10000]
        )
    ]),

    dcc.Graph(id='success-payload-scatter-chart')
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_pie_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        # Başarılı fırlatmaları filtrele (class=1)
        success_df = spacex_df[spacex_df['class'] == 1]
        title = 'Total Success Launches By Site'
        
        # Fırlatma alanlarına göre başarı sayılarını hesapla
        success_counts = success_df['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'count']
        
        # Pasta grafiği oluştur
        fig = px.pie(success_counts, values='count', names='Launch Site', title=title)
    else:
        # Belirli bir fırlatma alanı için veri filtrelenir
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title = f'Total Success and Failure Counts for {selected_site}'
        
        # Başarı ve başarısızlık oranlarını hesapla
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts['class'] = success_counts['class'].apply(lambda x: 'Success' if x == 1 else 'Failure')
        
        # Pasta grafiği oluştur
        fig = px.pie(success_counts, values='count', names='class', title=title)
    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        # Tüm fırlatma alanları için veri filtresi uygulanmadan kullanılır
        filtered_df = spacex_df
        title = 'Payload and Success Scatter Plot for All Sites'
    else:
        # Belirli bir fırlatma alanı için veri filtrelenir
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title = f'Payload and Success Scatter Plot for {selected_site}'
    
    # Seçilen payload aralığına göre veriyi filtrele
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Scatter plot oluştur
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=title)
    fig.update_layout(xaxis_title='Payload Mass (kg)', yaxis_title='Class')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)