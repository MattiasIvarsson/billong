
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_table as dt
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import matplotlib.pyplot as plt
import pyodbc
import urllib.request
from sqlalchemy import create_engine
import chart_studio as cs
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate



#CONFIG
# -----------------------------------------------
config = {
        'server': 'localhost\BILLONG',
        'db': 'FOOTBALL-DBT',
        'user': 'admin', 
        'pwd': 'T14he5971!'
}

params = urllib.parse.quote_plus('Driver={SQL Server};'
                                 'Server=' + config['server'] + ';'
                                 'Database=' + config['db'] + ';'
                                 'UID=' + config['user'] + ';'
                                 'PWD=' + config['pwd'] + ';')

engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
engine.fast_executemany = True


# OTHER DATA INPUT
# -----------------------------------------------
football_data = pd.read_csv('data/bigfive.csv',sep=';')
football_data = football_data[["MatchDay", "Country", "Team", "Points", "Goals"]].drop_duplicates()


# SQL FUNCTIONS
# -----------------------------------------------

def get_table():
    query = """
    SELECT 
        RANK() OVER (order by sum(Points)desc,	Sum(Goals-GoalsAgainst) desc) AS 'Pos'        
        ,r.Team
        ,COUNT(distinct r.match_key)										AS 'Games'
        ,SUM(CASE	WHEN r.Result ='Home' AND Location = 'Home'	THEN 1 
                    WHEN r.Result ='Away' AND Location = 'Away'	THEN 1 END)	AS 'Won'							
        ,SUM(CASE	WHEN r.Result ='Draw'						THEN 1 END)	AS 'Draw'
        ,SUM(CASE	WHEN r.Result ='Home' AND Location = 'Away'	THEN 1 
        WHEN r.Result ='Away' AND Location = 'Lost'	THEN 1 END)	AS 'Lost'
        ,SUM(Goals)															AS 'GF'
        ,SUM(GoalsAgainst)													AS 'GA'
        ,SUM(Goals - GoalsAgainst)											AS 'GD'
        ,SUM(Points)														AS 'Points'
    
    FROM	
        [FOOTBALL-DBT].[football].[results_team]  as r
        LEFT JOIN(	SELECT
            opponent as team
            ,CAST(goals AS INT) AS 'GoalsAgainst'
            ,match_key
        FROM
            [FOOTBALL-DBT].[football].[results_team] 
        ) AS o  on o.team =r.Team AND o.match_key = r.match_key
        
     WHERE 
        r.bigfive = 1
        AND r.Country = 'England'
        AND r.Season = '2018/2019'
        
    GROUP BY
        r.Team	
        ORDER BY
        9 desc"""
    return pd.read_sql_query(query, con=engine)


def get_table_2(id):
    query = """
            SELECT 
                RANK() OVER (order by sum(Points)desc)				AS 'Prio'
                ,r.Team												AS 'Team'
                ,r.Country											AS 'Country'
                ,SUM(CASE WHEN Location = 'Home' THEN Points END)	AS 'HomePoints'
                ,SUM(CASE WHEN Location = 'Away' THEN Points END)	AS 'AwayPoints'
                ,SUM(Points)										AS 'Points'
                ,SUM(Goals)											AS 'Goals'
                ,SUM(CASE WHEN Location = 'Home' THEN Goals END)	AS 'HomeGoals'
                ,SUM(CASE WHEN Location = 'Away' THEN Goals END)	AS 'AwayGoals'
                ,SUM(Shots)											AS 'Goals'
                ,SUM(CASE WHEN Location = 'Home' THEN Shots END)	AS 'HomeShots'
                ,SUM(CASE WHEN Location = 'Away' THEN Shots END)	AS 'AwayShots'
            FROM	
                [FOOTBALL-DBT].[football].[results_team]  as r	
            WHERE 
                bigfive=1
                AND Country = 'England'
                AND Season = like '""" + id + """%'
            GROUP BY
                r.Team
                ,r.Country
            ORDER BY
                SUM(Points)"""  
    return pd.read_sql_query(query, con=engine)


def sql_team_values():
    query = """
    SELECT 
        RANK() OVER (PARTITION BY Country,Season order by sum(Points)desc)	AS 'Prio'
        ,r.Team												AS 'Team'
        ,Season												AS 'Season'
        ,r.Country											AS 'Country'
        ,SUM(CASE WHEN Location = 'Home' THEN Points END)	AS 'HomePoints'
        ,SUM(CASE WHEN Location = 'Away' THEN Points END)	AS 'AwayPoints'
        ,SUM(Points)										AS 'Points'
        ,SUM(Goals)											AS 'Goals'
        ,SUM(CASE WHEN Location = 'Home' THEN Goals END)	AS 'HomeGoals'
        ,SUM(CASE WHEN Location = 'Away' THEN Goals END)	AS 'AwayGoals'
        ,SUM(Shots)											AS 'Goals'
        ,SUM(CASE WHEN Location = 'Home' THEN Shots END)	AS 'HomeShots'
        ,SUM(CASE WHEN Location = 'Away' THEN Shots END)	AS 'AwayShots'
    FROM	
        [FOOTBALL-DBT].[football].[results_team]  as r	
    WHERE 
        r.bigfive=1
        AND r.Country = 'England'
        AND r.Season in ('2019/2020')
    GROUP BY
        r.Team
        ,r.Country
        ,r.Season
    ORDER BY
        RANK() OVER (PARTITION BY Country,Season order by sum(Points))"""

    return pd.read_sql_query(query, con=engine)


def sql_team_location_values():
    query = """
        SELECT 
            RANK() OVER (order by sum(Points)desc)				AS 'Prio'
            ,MatchDay											AS 'MatchDay'
            ,YEAR(MatchDay)										AS 'Year'
            ,GameWeek											AS 'GameWeek'
            ,Team												AS 'Team'
            ,Country											AS 'Country'
            ,Location											AS 'Location'
            ,SUM(CASE WHEN Location = 'Home' THEN Points END)	AS 'HomePoints'
            ,SUM(CASE WHEN Location = 'Away' THEN Points END)	AS 'AwayPoints'
            ,SUM(Points)										AS 'Points'		
            ,SUM(Points_RT)										AS 'PointsRT'
            ,SUM(Goals)											AS 'Goals'
            ,SUM(CASE WHEN Location = 'Home' THEN Goals END)	AS 'HomeGoals'
            ,SUM(CASE WHEN Location = 'Away' THEN Goals END)	AS 'AwayGoals'
            ,SUM(Shots)											AS 'Shots'
            ,SUM(CASE WHEN Location = 'Home' THEN Shots END)	AS 'HomeShots'
            ,SUM(CASE WHEN Location = 'Away' THEN Shots END)	AS 'AwayShots'
        FROM	
            [FOOTBALL-DBT].[football].[results_team]  as r	
        WHERE 
            r.bigfive = 1
            AND Country in( 'England','Italy')
            AND Season = '2019/2020'	
        GROUP BY
            Team
            ,Country
            ,Gameweek
            ,Location
            ,MatchDay
        ORDER BY
            Team
            ,Country
            ,Gameweek"""
    return pd.read_sql_query(query, con=engine)


def sql_team_country_values():
    query = """
        SELECT 
            YEAR(MatchDay)										AS 'Year'
            ,Team												AS 'Team'
            ,Country											AS 'Country'
            ,SUM(CASE WHEN Location = 'Home' THEN Points END)	AS 'HomePoints'
            ,SUM(CASE WHEN Location = 'Away' THEN Points END)	AS 'AwayPoints'
            ,SUM(Points)										AS 'Points'		
            ,SUM(Goals)											AS 'Goals'
            ,SUM(CASE WHEN Location = 'Home' THEN Goals END)	AS 'HomeGoals'
            ,SUM(CASE WHEN Location = 'Away' THEN Goals END)	AS 'AwayGoals'
            ,SUM(Shots)											AS 'Shots'
            ,SUM(CASE WHEN Location = 'Home' THEN Shots END)	AS 'HomeShots'
            ,SUM(CASE WHEN Location = 'Away' THEN Shots END)	AS 'AwayShots'
        FROM	
            [FOOTBALL-DBT].[football].[results_team]  as r	
        WHERE 
            r.bigfive=1
            AND Country in( 'England','Italy','Spain')
            AND YEAR(MatchDay)	BETWEEN '2016' AND '2020'	
        GROUP BY
            Team
            ,Country
            ,YEAR(MatchDay)	
        ORDER BY
            Team
            ,Country"""
    return pd.read_sql_query(query, con=engine)


# GENERATE FUNCTIONS
# -----------------------------------------------
def generate_table(dataframe, max_rows=100):
    return html.Table(
        # Header
             [html.Tr([html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
        )


def generate_barChart(data, title):
    return dcc.Graph(
            config={'responsive': True},
            style={ 'height': '100%',
                    'width': '115%',
                    'opacity': '0.9' },
            figure={'data': data,
                    'layout':go.Layout( title=title,
                                        titlefont={'size': 14},
                                        barmode='stack',
                                        xaxis=dict( showgrid=False,
                                                    domain=[0, 0.9],
                                                    anchor='y',
                                                    linecolor=barchart['Fontcolor'],
                                                    linewidth=2
                                                       ),
                                        yaxis=dict( showgrid=False,
                                                    type='category'),
                                        paper_bgcolor=barchart['Papercolor'],
                                        plot_bgcolor=barchart['Papercolor'],
                                        font=dict(  color=barchart['Fontcolor'],
                                                    family='Calibri',
                                                    size =10),
                                        margin=go.layout.Margin(l=80, pad=5)
                                        ),
                    }
                )


def generate_lineChart(data,title):
    data.update_layout( autosize=True,
                        title=title,
                        titlefont={'size': 14},
                        paper_bgcolor=linechart['Papercolor'],
                        plot_bgcolor=linechart['Papercolor'],
                        font=dict(  color=linechart['Fontcolor'],
                                    family='Helvetica'),
                        xaxis=dict( showgrid=False,
                                    showline=True,
                                    linecolor=barchart['Fontcolor'],
                                    linewidth=2),
                        yaxis=dict( showgrid=False),
                        showlegend=True,
                        margin=go.layout.Margin(t=45, b=10, l=80, r=10),
                    )
    return dcc.Graph(
                    config={'responsive': True},
                    style={ 'height': '100%',
                             'width': '100%',
                             'opacity': '0.9' },
                    figure=data
                    )


def generate_pieChart(data, title):
    return dcc.Graph(
            config={'responsive': True},
            style={ 'height': '100%', 
                    'width': '100%',
                    'opacity': '0.9'},
            figure={'data': data,                                             
                    'layout':go.Layout( title=title,
                                        titlefont={'size': 12},
                                        paper_bgcolor=piechart['Papercolor'],
                                        plot_bgcolor=piechart['Papercolor'],
                                        font=dict(  color=piechart['Fontcolor'],
                                                    family='Helvetica',
                                                    size=12),
                                        autosize=True,
                                        margin = go.layout.Margin(t=45, b=10, l=10, r=10, pad=1)
                                                                                        
                                        ),
                    }
                ) 


def generate_scatterChart(search_value):
    return dcc.Graph(id='graph-with-slider'),


# OTHER FUNCTIONS
# -----------------------------------------------

def select_team_pointsPie(team_location_values):        
        df = pd.pivot_table(team_location_values, index=['Location'], values=['Points'], aggfunc=sum, fill_value=0)      

        trace1 = go.Pie(
                    labels=df.index, 
                    values=df.Points,
                    hole=0.5,
                    direction='clockwise',
                    sort=True,
                    marker={'colors': [barchart["Barcolor1"], barchart["Barcolor"]]},
                    showlegend=False,
                    )        
        data =[trace1]
        return data


def select_team_goalsPie(team_location_values):        
        df = pd.pivot_table(team_location_values, index=['Location'], values=['Goals'], aggfunc=sum, fill_value=0)

        trace1 = go.Pie(
                    labels=df.index, 
                    values=df.Goals,
                    hole=0.5,
                    direction='clockwise',
                    sort=True,
                    marker={'colors':[barchart["Barcolor1"],barchart["Barcolor"]]},
                    showlegend=False,
                    )        
        data =[trace1]
        return data


def select_team_shotsPie(team_location_values):        
        df = pd.pivot_table(team_location_values, index=['Location'], values=['Shots'], aggfunc=sum, fill_value=0)      
        trace1 = go.Pie(
                    labels=df.index, 
                    values=df.Shots,
                    hole=0.5,
                    direction='clockwise',
                    sort=True,
                    marker={'colors':[barchart["Barcolor1"],barchart["Barcolor"]]},
                    showlegend=False,
                    )        
        data =[trace1]
        return data


def select_team_points(team_values):
        # pv = pd.pivot_table(df, index=['Team'], columns=['Location'], values=['Points'], aggfunc=sum, fill_value=0)
        df=team_values
        trace1 = go.Bar(y=df.Team, 
                        x=df.HomePoints, 
                        name='Home',
                        orientation = 'h',
                        text=df.HomePoints,
                        textposition='auto',
                        showlegend=False,
                        marker=dict(color=(barchart["Barcolor"] ))
                         )        
        trace2 = go.Bar(y=df.Team, 
                        x=df.AwayPoints, 
                        name='Away',
                        orientation = 'h',
                        text=df.AwayPoints,
                        textposition='auto',
                        showlegend=False,
                        marker=dict(color=(barchart["Barcolor1"] )) )                                 
        data = [trace1, trace2]         
        return data


def select_team_goals(team_values):
        df=team_values
        trace1 = go.Bar(y=df.Team, 
                        x=df.HomeGoals, 
                        name='Home',
                        orientation = 'h',
                        text=df.HomeGoals,
                        textposition='auto',
                        showlegend=False,
                        marker=dict(color=(barchart["Barcolor"] )) 
                         )        
        trace2 = go.Bar(y=df.Team, 
                        x=df.AwayGoals, 
                        name='Away',
                        orientation = 'h',
                        text=df.AwayGoals,
                        textposition='auto',
                        showlegend=False,
                        marker=dict(color=(barchart["Barcolor1"] )) )                           
        data = [trace1, trace2]         
        return data


def select_team_shots(team_values):
        df=team_values
        trace1 = go.Bar(y=df.Team, 
                        x=df.HomeShots, 
                        name='Home',
                        orientation = 'h',
                        text=df.HomeShots,
                        textposition='auto',
                        showlegend=False,
                        marker=dict(color=(barchart["Barcolor"] )) 
                         )        
        trace2 = go.Bar(y=df.Team, 
                        x=df.AwayShots, 
                        name='Away',
                        orientation = 'h',
                        text=df.AwayShots,
                        textposition='auto',
                        showlegend=False,
                        marker=dict(color=(barchart["Barcolor1"] )) )                           
        data = [trace1, trace2]         
        return data


def select_team_pointsLine(team_location_values):
        #df = pd.pivot_table(team_location_values, index=['GameWeek'],columns=['Team'], values=['Points'], aggfunc=sum, fill_value=0)      
        df = team_location_values
        z = df.Team
        y = df.PointsRT
        x = df.GameWeek
        data = px.line(dict(Team=z, 
                            Points=y, 
                            GameWeek=x), 
                            x='GameWeek',
                            y='Points',
                            color=z,
                            hover_name=z)
        for trace in data.data:
            trace.name = trace.name.split('=')[1]     
        return data


def select_team_goals_2(team_location_values):
        df = team_location_values
        print(df)
        traces = []      
        for i in df.Team.unique():
            df_by_team = df[df['Team'] == i]
            go.Bar (y=df_by_team.Team,
                    x=df_by_team.Goals,
                    name=i,
                    orientation = 'h',
                    text=df.HomeGoals,
                    textposition='auto',
                    showlegend=False,
                    marker=dict(color=(barchart["Barcolor"] )) 
                                )  
            data = traces                                                             
        return data


# VARIBLES
# -----------------------------------------------
team_values = sql_team_values()
team_location_values = sql_team_location_values()
df = sql_team_country_values()
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

barchart = {    'Barcolor':'#7E8D8D',
                'Barcolor1':'rgb(194, 204, 204)',
                'Fontcolor':'white',
                'Papercolor':'rgba(0,0,0,0)',
                'Plotcolor':'rgba(0,0,0,0)',
                'LineColor':'white'
                }
piechart = {    'Barcolor':'#7E8D8D',
                'Barcolor1':'rgb(194, 204, 204)',
                'Fontcolor':'white',
                'Papercolor':'rgba(0,0,0,0)',
                'Plotcolor':'rgba(0,0,0,0)',
                'LineColor':'white'
                }
linechart = {   'Linecolor':'#7E8D8D',
                'Linecolor1':'rgb(194, 204, 204)',
                'Fontcolor':'white',
                'Papercolor':'rgba(0,0,0,0)',
                'Plotcolor':'rgba(0,0,0,0)',
                'LineColor':'white'              
                }


# APPLICATION
# -----------------------------------------------
app = dash.Dash(__name__) 

app.layout = html.Div(children=[


                # HEADER
                # -----------------------
                html.Div(children=[
                        html.H1(children="FOOTBALL"),
                        html.Img(src="/assets/plan.png")
                            ]),
                 
                # TAB
                # ----------------------- 
                dcc.Tabs(                        
                    children=[
                        
                        # TAB1
                        # -----------------------
                        dcc.Tab(label='FIRST', children=[
                       
                            # GRID
                            # -----------------------
                            html.Div(children=[
                        
                                # TOP GRID1
                                # -----------------------
                                html.Div(children=[   
            
                                  #  generate_pieChart(dataBarchar(team_values,'Points','Goals','Year','Team'),'Points')

                                    ],className='menurow'),
                            
                                # TOP GRID2
                                # -----------------------
                                html.Div(children=[ 
                                    generate_pieChart(select_team_goalsPie(team_location_values), 'Goals')
                                    ], className='menurow'),
                            
                                # TOP GRID3
                                # -----------------------
                                html.Div(children=[   
                                    generate_pieChart(select_team_shotsPie(team_location_values),'Shots')
                                    ], className='menurow'),

                                # TOP GRID4
                                # -----------------------
                                html.Div(children=[
                                            html.H2(children="FILTERS"),
                                            dcc.Input(id='my-id', value='Write something', type='text'),
                                            html.Div(id='my-div') ,  
                                            dcc.Dropdown(
                                                        multi=False,
                                                        id='drop-down-id')

                                        ], className='menurow'),
                                
                                # GRID MAIN
                                # -----------------------
                                html.Div(children=[                                                          

                                        # GRID MAIN 1
                                        # -----------------------
                                        html.Div(children=[
                                                    generate_barChart(select_team_points(team_values), 'Points')
                                                ], className='item11'),
                                        
                                        # GRID MAIN 2
                                        # -----------------------   
                                        html.Div(children=[
                                                    generate_barChart(select_team_goals(team_values), 'Goals')
                                                ], className='item12'),

                                        # GRID MAIN 3
                                        # -----------------------   
                                        html.Div(children=[
                                                    generate_barChart(select_team_shots(team_values), 'Shots')
                                                ], className='item13'),


                                        # GRID MAIN BOTTOM
                                        # -----------------------   
                                        html.Div(children=[
                                                    generate_lineChart(select_team_pointsLine(team_location_values),'Shots')      
                                                ], className='item14'),
                                            
                                    ], className='item1'),

                                # GRID SIDE TOP
                                # -----------------------
                                html.Div(children=[
                                        generate_table(get_table())
                                    ], className="item2"),

                                # GRID 4 SIDE BOTTOM
                                # -----------------------
                                html.Div(children=[
                                                html.H3("Forth"),
                                                dt.DataTable(
                                                        id='datatable',
                                                        data =football_data.to_dict('records'),
                                                        columns=[{'name': c,'id':c} for c in football_data.columns],
                                                        style_as_list_view=True,
                                                        style_cell={'textAlign':   'left',
                                                                    'backgroundColor': '#464848',
                                                                    'color':   'white'},
                                                        style_header={  'backgroundColor':  '#7E8D8D',
                                                                        'fontWeight':   'bold',
                                                                        'color':   '#161717'},
                                                        style_table={   'maxHeight':    '500px',
                                                                        'overflowY':    'scroll'}                                                                                               
                                                        )                                     
                                            ], className='item3'),

                                # GRID FOOTER
                                # -----------------------
                                html.Div(children=[  
                                            dcc.Graph(  id='graph-with-slider',
                                                        style={'height': '100%'}),

                                            dcc.Slider(
                                                id='year-Slider',
                                                min=df['Year'].min(),
                                                max=df['Year'].max(),
                                                value=df['Year'].min(),
                                                marks={str(year): str(year) for year in df['Year'].unique()},
                                                step=0.5
                                                    ),
                                                                                   
                                    ],className='item4'),        
                            ], className='container'),  # GRID CLOSE
                        
                    ],  className='tab',
                            selected_className='tabselected'),  # TAB 1 CLOSE


                        # TAB2
                        # -----------------------
                        dcc.Tab(label='SECOND', children=[
                       
                            # GRID
                            # -----------------------
                            html.Div(children=[                        
                        
                                # TOP GRID1
                                # -----------------------
                                html.Div(children=[   
                                        generate_pieChart(select_team_pointsPie(team_location_values), 'Points')
                                    ], className='menurow'),
                            
                                # TOP GRID2
                                # -----------------------
                                html.Div(children=[ 
                                        generate_pieChart(select_team_goalsPie(team_location_values), 'Goals')
                                    ], className='menurow'),
                            
                                # TOP GRID3
                                # -----------------------
                                html.Div(children=[   
                                    generate_pieChart(select_team_shotsPie(team_location_values), 'Shots')
                                    ], className='menurow'),

                                # TOP GRID4
                                # -----------------------
                                    html.Div(children=[   
                                            html.H2(children="FILTERS"),
         

                                        ], className='menurow'),
                                
                                # GRID MAIN
                                # -----------------------
                                html.Div(children=[                                                          

                                        # GRID MAIN 1
                                        # -----------------------
                                        html.Div(children=[

                                                ], className='item11'),
                                        
                                        # GRID MAIN 2
                                        # -----------------------   
                                        html.Div(children=[
                                                    generate_barChart(select_team_goals(team_values), 'Goals')
                                                ], className='item12'),

                                        # GRID MAIN 3
                                        # -----------------------   
                                        html.Div(children=[
                                                    generate_barChart(select_team_shots(team_values), 'Shots')
                                                ], className='item13'),


                                        # GRID MAIN BOTTOM
                                        # -----------------------   
                                        html.Div(children=[
                                                    generate_lineChart(select_team_pointsLine(team_location_values), 'Shots')
                                                ], className='item14'),
                                            
                                    ],className='item1'),  

                                # GRID SIDE TOP
                                # -----------------------
                                html.Div(children=[
                                        generate_table(get_table())
                                    ], className="item2"),

                                # GRID 4 SIDE BOTTOM
                                # -----------------------
                                html.Div(children=[
                                                html.H3("Forth"),
                                                dt.DataTable(
                                                        data=football_data.to_dict('records'),
                                                        columns=[{'name': c, 'id': c} for c in football_data.columns],
                                                        style_as_list_view=True,
                                                        style_cell={'textAlign':   'left',
                                                                    'backgroundColor': '#464848',
                                                                    'color':   'white'},
                                                        style_header={'backgroundColor':  '#7E8D8D',
                                                                      'fontWeight':   'bold',
                                                                      'color':   '#161717'},
                                                        style_table={'maxHeight':    '500px',
                                                                     'overflowY':    'scroll'}
                                                        )                                     
                                            ], className='item3'),

                                # GRID FOOTER
                                # -----------------------
                                html.Div(children=[  
                                    html.H3("Forth"),                                
                                    ], className='item4'),

                            ], className='container'),  # GRID CLOSE
                        
                    ],  className='tab',
                        selected_className='tabselected'),  # TAB 2 CLOSE
            
            ], className='tabscontainer')   # TAB CLOSE
      
        ])  # LAYOUT CLOSE


    # CALL BACKS
    # -----------------------

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-Slider', 'value')])


def update_figure(selected_year):
    df = sql_team_country_values()
    print(df)
    print(selected_year)
    filtered_df = df[df['Year'] == selected_year]  
    print(filtered_df) 
    print(filtered_df.Country.unique) 
    traces = []
    for i in filtered_df.Country.unique():
        df_by_team = filtered_df[filtered_df['Country'] == i]
        traces.append(dict(
            x=df_by_team['Points'],
            y=df_by_team['Goals'],
            text=df_by_team['Team'],
            mode='markers',
            opacity=0.7,
            marker={'size': 15 },
            name=i
        )) 
    return {
            'data': traces,
            'layout': dict(
                        xaxis=dict( title= 'Points',
                                    range =[1, df['Points'].max()],
                                    showline=True,
                                    showgrid=False,
                                    linecolor=barchart['Fontcolor'],
                                    linewidth=1 ),
                        yaxis=dict( title= 'Goals',
                                    range =[1, df['Goals'].max()],
                                    showline=True,
                                    showgrid=False,
                                    linecolor=barchart['Fontcolor'],
                                    linewidth=1 ),
                        margin = go.layout.Margin(t=45, b=50, l=80, r=40),
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 1000},
                        titlefont={'size': 14},
                        paper_bgcolor=linechart['Papercolor'],
                        plot_bgcolor=linechart['Papercolor'],
                        font=dict(  color=linechart['Fontcolor'],family='Helvetica') , 
                        )

            }
                
          


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)


def update_output_div_test(input_value):
    return 'You\'ve entered "{}"'.format(input_value)


# SEARCH BOX
@app.callback(
    dash.dependencies.Output("drop-down-id", "options"),
    [dash.dependencies.Input("drop-down-id", "search_value")],
)
def update_multi_options(search_value):
    if not search_value or len(search_value) < 5:
        print(search_value)
        raise PreventUpdate
    else:
        return [{'label': i, 'value': i} for i in get_table_2(search_value)['season']]

 

if __name__ == '__main__':
    app.run_server(debug=True)

