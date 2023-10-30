#!/usr/bin/env python
# coding: utf-8

# In[105]:


import dash
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import warnings
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
warnings.filterwarnings("ignore", category=FutureWarning)


# In[106]:


df = pd.read_csv('purine data new.csv')
df


# In[107]:


user = pd.read_excel('gout_patient_data.xlsx')
user


# In[108]:


user['Date'] = pd.to_datetime(user['Date'])
user.info()


# In[109]:


user['Month'] = pd.to_datetime(user['Date']).dt.month


# In[110]:


new_user = pd.melt(user, id_vars=['Date','Month','User'], var_name='Categories', value_name='Value')
new_user.head()


# In[181]:


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

food_quantities = {food: 0 for food in df['Foods']}

food_intake = []

app.layout = html.Div(children=[
    # 左侧部分
    html.Div(children=[
        html.Nav(className="navbar navbar-expand-lg bg-primary",style={'background-color': '#73B3D9'}, **{"data-bs-theme": "dark"}, children=[
            html.Div(className="container-fluid", children=[
                html.A("Personal Health Index", className="navbar-brand",style={'font-size': '50px'})
            ])
        ]),
        
        html.Br(),
        
        html.Div([
        dbc.Row([
            dbc.Col([
                #html.H2('Personal Health Index'),
                dcc.DatePickerSingle(
                    id='date-picker',
                    date=user['Date'].max()
                ),
                html.Div(id='selected-data')
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2('Health Tips', style={'font-size': '30px','color': '#0E367C'}),
                        html.Blockquote([
                            html.P('A regular life is the secret of health and longevity.', className='mb-0'),
                            html.Br(),
                            html.Figcaption([
                                'Balzac'
                            ], className='blockquote-footer')
                        ]),
                    ],
                    ),
                ])
        ], align="end"),
    ]),


        html.Br(),
        html.Br(),

        # 中间部分
        html.Div([
            # 折线图
            html.Div([
                html.H2('Change in Personal Health Index', style={'font-size': '30px','color': '#0E367C'}),
                dcc.Dropdown(
                    new_user['Categories'].unique(),
                    value = 'Total Daily Purine(mg)',
                    id = 'category'
                ),
                
                dcc.Graph(id = 'graph'),
                
                dcc.Slider(
                    new_user['Month'].min(),
                    new_user['Month'].max(),
                    step=None,
                    id='month_slider',
                    value=new_user['Month'].min(),
                    marks={str(month):str(month) for month in new_user['Month'].unique()},
                )
            ], style={'width': '75%', 'display': 'inline-block'}),
            
            html.Br(),
            html.Br(),
            html.Br(),
            
            html.Div([
                html.H2('What did you eat today?', style={'font-size': '30px','color': '#0E367C'}),
                html.Div([
                    'Food',
                    dcc.Dropdown(
                        id='food',
                        options=[{'label': food, 'value': food} for food in df['Foods']],
                        multi=True
                    ),
                    html.Br(),
                    'Total Intake(g)',
                    dcc.Input(id='food_weight', value=350, type='number')
                ]),
                html.Br(),
                html.Div(id='user_intake'),
                dcc.Graph(id='purines-bar-chart'),
                html.Button('Add', id='add_button', n_clicks=0)
            ], style={'width': '75%', 'display': 'inline-block'}),

        ]),
    
            
    html.Br(),
        
    # 显示新闻标题
    html.Div([
        dbc.Card(
            dbc.CardBody([
                 html.H4("Health News - About Hyperuricemia", className="card-title", style={'font-size': '30px'}),
                html.H6("Hyperuricemia: Symptoms, Treatment, and More", className="card-subtitle mb-2 text-muted"),
                html.P("Hyperuricemia occurs when there’s too much uric acid in your blood. Only about a third of people experience symptoms. If uric acid levels remain high, over time they can lead to several diseases, such as gout or kidney stones.", className="card-text"),
                dbc.CardLink("News link", href="https://www.healthline.com/health/hyperuricemia#symptoms"),
            ])
        ),
        
        html.Br(),
        
    html.Div([
        dbc.Card(
            dbc.CardBody([
                 html.H4("Health Artical - About Hyperuricemia", className="card-title", style={'font-size': '30px'}),
                html.H6("The treatment of hyperuricemia", className="card-subtitle mb-2 text-muted"),
                html.P("The present review article will try to summarize the most recent evidences on the efficacy of XO inhibitors and uricosuric compounds in lowering uric acid levels in both the bloodstream and peripheral tissues.", className="card-text"),
                dbc.CardLink("Artical link", href="https://www.sciencedirect.com/science/article/pii/S016752731530317X"),
            ]),
        ),
    ]),
]),
]),
]),
])

        

@app.callback(
    Output('selected-data', 'children'),
    Input('date-picker', 'date')
)
def update_selected_data(selected_date):
    filtered_df = user[user['Date'] == selected_date]

    if not filtered_df.empty:
        user_name = filtered_df.iloc[0]['User']
        water = filtered_df.iloc[0]['Water(L)']
        exercise = filtered_df.iloc[0]['Exercise(min)']
        uric_acid = filtered_df.iloc[0]['Uric Acid (μmol/L)']
        weight = filtered_df.iloc[0]['Weight(kg)']

        return html.Div([
            html.Div(f'{user_name}', style={'font-size': '50px',
                                            'font-weight': 'bold',
                                            'color': '#0E367C'}),
            html.Br(),
            dbc.Stack([
                html.Div(f'Water(L): {water}', style={'font-size': '19px'}),
                html.Div(f'Exercise(min): {exercise}', style={'font-size': '19px'}),
                html.Div(f'Uric Acid (μmol/L): {uric_acid}', style={'font-size': '19px'}),
                html.Div(f'Weight(kg): {weight}', style={'font-size': '19px'}),
            ],
            direction = 'horizontal',
            gap=3,
            ),
        ])
    else:
        return f'No data available for {selected_date}'

@app.callback(
    Output('graph', 'figure'),
    Input('category', 'value'),
    Input('month_slider', 'value')
    )
def update_graph(categories, month_value):
    query = (new_user['Month'] == month_value) & (new_user['Categories'] == categories)
    filtered_df = new_user[query]
    
    fig = px.line(
        data_frame = filtered_df,
        x = 'Date',
        y = 'Value',
        title = f'{categories} over Time')

    return fig

def calculate_total_purines_intake(df, food_quantities, intake_list):
    total_intake = 0 

    for food, quantity in food_quantities.items():
        if quantity is not None: 
            row = df[df['Foods'] == food]
            if not row.empty:
                purines_value = row.iloc[0]['Average Purines in mg uric acid/100 g (Average)']
                if not pd.isna(purines_value):
                    purines_intake = (purines_value / 100) * quantity
                    total_intake += purines_intake

                   
                    intake_list.append({'Food': food, 'Purines Intake': purines_intake})

    return total_intake, intake_list

@app.callback(
    Output('food', 'options'),
    Input('add_button', 'n_clicks')
)
def update_food_options(n_clicks):
    return [{'label': food, 'value': food} for food in food_quantities]

@app.callback(
    Output('user_intake', 'children'),
    Output('purines-bar-chart', 'figure'),
    Input('add_button', 'n_clicks'),
    Input('food', 'value'),
    Input('food_weight', 'value')
)
def update_user_intake(n_clicks, selected_food, weight):
    global food_intake
    food_intake = []  

    
    if not selected_food:
        return "No food selected", {"data": [], "layout": {"title": "Purines Intake by Food"}}

    if not isinstance(selected_food, list):
        selected_food = [selected_food]

    for food in food_quantities:
        if food in selected_food:
            food_quantities[food] = weight
        else:
            food_quantities[food] = 0

    total_purines_intake, food_intake_updated = calculate_total_purines_intake(df, food_quantities, food_intake)

    intake_df = pd.DataFrame(food_intake_updated)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=intake_df['Food'], y=intake_df['Purines Intake'], name='Purines Intake'))
    fig.update_layout(
        title='Purines Intake by Food',
        xaxis_title='Food',
        yaxis_title='Purines Intake (mg)'
    )
    
    total_purines_intake_formatted = f'Total Purines Intake: {total_purines_intake:.2f} mg'
    
    return total_purines_intake_formatted, fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8061)


# In[ ]:





# In[ ]:




