import pandas as pd
import plotly as plt
import cufflinks as cf
import numpy as np
import plotly.graph_objs as go
import math

from plotly.offline import init_notebook_mode, iplot
from plotly import tools

init_notebook_mode(connected=True)


class GetHappinessData:
    def get_all_data(self):
        df_all = pd.read_excel('./WHR.xls')
        return df_all

    def get_2017_data(self):
        df_2017 = pd.read_excel('./WHR.xls', sheet_name='Figure2.2')
        return df_2017

    def get_us_data(self):
        all = self.get_all_data()
        US = all[all['country'] == 'United States']
        return US


class CreateUS2017Plot:
    def create_trace(self, y_variable_name, name, line=None):
        data = GetHappinessData()
        US = data.get_us_data()
        trace = go.Scatter(x=US['year'], y=US[y_variable_name],
                           mode="markers+lines", name=name, line=line)
        return trace

    def create_US_happy_trace(self):
        data = [self.create_trace('Life Ladder', 'Happiness')]
        layout = go.Layout(
            title='US Happiness 2006-2017',
            hovermode='closest',
            xaxis=dict(
                title='Year',
                ticklen=5,
                zeroline=False,
                gridwidth=2,
            ),
            yaxis=dict(
                title='Happiness Score (Ladder)',
                ticklen=5,
                gridwidth=2,
            ),
            showlegend=False
        )
        fig = dict(data=data, layout=layout)
        iplot(fig)

    def create__comparative_iplot(self):
        figure = tools.make_subplots(rows=3, cols=1)
        figure.append_trace(self.create_trace('Life Ladder', 'Happiness'), 1, 1)
        figure.append_trace(self.create_trace('Social support', 'Social Support'), 1, 1)
        figure.append_trace(self.create_trace('Life Ladder', 'Happiness'), 2, 1)
        figure.append_trace(self.create_trace('Log GDP per capita', 'GDP'), 2, 1)
        figure.append_trace(self.create_trace('Life Ladder', 'Happiness'), 3, 1)
        figure.append_trace(self.create_trace('Generosity', 'Generosity'), 3, 1)
        figure['data'][1].update(yaxis='y4')
        figure['data'][3].update(yaxis='y5')
        figure['data'][5].update(yaxis='y6')

        figure['layout'].update(autosize=False,
                                width=1000,
                                height=1500,
                                showlegend=False,
                                hovermode='x',
                                title='US Happiness compared to other measures of well being')

        figure['layout']['yaxis4'] = dict(
            overlaying='y1',
            anchor='x1',
            side='right',
            showgrid=False,
            title='Social Support'

        )

        figure['layout']['yaxis5'] = dict(
            overlaying='y2',
            anchor='x2',
            side='right',
            showgrid=False,
            title='Log of GDP per Capita'
        )
        figure['layout']['yaxis6'] = dict(
            overlaying='y3',
            anchor='x3',
            side='right',
            showgrid=False,
            title='Generosity'
        )

        iplot(figure)

#create graphs for world happiness scores
class WorldHappiness:
    def __init__(self):
        data = GetHappinessData()
        self.df = data.get_all_data()

    #function to generate list of keys available for comparing
    def listofkeys(self):
        return self.df.columns
    #function to generate a random color for each country in list
    def random_color(self, country):
        x = np.random.choice(range(256))
        y = np.random.choice(range(256))
        z = np.random.choice(range(256))
        return f'rgb({x},{y},{z})'
    # generate scatter plot object for happiness score vs given measure in a given year
    def generateWorldTrace(self, year, measure):
        year_data = self.df[self.df['year'] == year]
        colors = [self.random_color(country) for country in year_data['country']]
        trace = go.Scatter(
                    x=year_data[measure],
                    y=year_data['Life Ladder'],
                    text=year_data['country'],
                    mode='markers',
                    marker = {'size': self.df['Life Ladder']*5, 'color': colors}
                )

        data = [trace]
        iplot(data)

    def changeInMeasureBetweenTwoYears(self, measure, year1, year2):
        #get dataframes of countries relevant measures for matching year
        year_data_1 = self.df[self.df['year']==year1][['country', 'Life Ladder', 'Social support', 'Generosity', 'Log GDP per capita']]
        year_data_2 = self.df[self.df['year']==year2][['country', 'Life Ladder', 'Social support', 'Generosity', 'Log GDP per capita']]
        #join above dataframes on country
        merged = pd.merge(year_data_1, year_data_2, on='country', how='outer')

        #take difference in each countries measure and add new column to dataframe
        for country in merged:
            try:
                merged["delta_" + f"{measure}"] = merged[f"{measure}" + "_y"] - merged[f"{measure}" + '_x']
            except:
                merged["delta_" + f"{measure}"] = None

        #clean all countries with Null values in delta and sort least to most
        cleaned_merged = merged[~merged['delta_' + f"{measure}"].isnull()].sort_values(by=['delta_' + f"{measure}"])

        delta_bar = go.Bar(
            x= cleaned_merged['delta_' + f"{measure}"],
            y= cleaned_merged['country'],
            orientation = 'h',
            name = measure
            )

        delta_chart = tools.make_subplots(rows=1, cols=1, shared_yaxes=True)

        delta_chart.append_trace(delta_bar, 1 ,1)

        delta_chart['layout'].update(autosize= False,
              width= 1000,
              height= 2000,
              showlegend=False,
            title = f'Change in {measure} from {year1} to {year2}')

        iplot(delta_chart)

    def createWorldMap(self):
        #get dataframe with country codes needed for cloropeth map
        country_codes = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
        #rename column name for easy merge
        country_codes = country_codes.rename(index=str, columns={'COUNTRY': 'country'})
        #merge country codes with country happiness dataframe
        merge_codes = pd.merge(self.df[self.df['year']==2017], country_codes, on='country', how='outer')

        data = [ dict(
                type = 'choropleth',
                locations = merge_codes['CODE'],
                z = merge_codes['Life Ladder'],
                text = merge_codes['country'],
                colorscale = [[0,"rgb(5, 10, 172)"],[2,"rgb(40, 60, 190)"],[3,"rgb(70, 100, 245)"],\
                    [4,"rgb(90, 120, 245)"],[5,"rgb(106, 137, 247)"],[7,"rgb(220, 220, 220)"]],
                autocolorscale = False,
                reversescale = True,
                marker = dict(
                    line = dict (
                        color = 'rgb(180,180,180)',
                        width = 0.5
                    ) ),
                colorbar = dict(
                    autotick = False,
                    title = 'Happiness'),
              ) ]

        layout = dict(
            title = 'World Happiness',
            geo = dict(
                showframe = False,
                showcoastlines = False,
                projection = dict(
                type = 'Mercator'
                )
            )
        )

        fig = dict( data=data, layout=layout )
        iplot( fig, validate=False)

    #return mean of all countries happiness for given year
    def average_for_year(self, year):
        year_data = self.df[self.df['year'] == year]
        return (np.mean(year_data['Life Ladder']))

    def changeinAverageOvertime(self):
        #list of years for which country happiness data is available omitting (first two years for insufficient data)
        list_of_years = sorted(list(set(self.df['year'])))[2:]
        averages = [self.average_for_year(year) for year in list_of_years]

        globalHappyTrace = go.Scatter(x=list_of_years, y=averages,
                    mode="markers+lines", name='Happiness', line={'color' : 'rgb(22, 96, 167)'})

        layout = go.Layout(
                    title= 'World Happiness Overtime',
                    xaxis= dict(
                        title= 'Years'
                    ),
                    yaxis=dict(
                        title= 'Happiness'
                    )
                )
        data = [globalHappyTrace]
        fig = dict(data = data, layout = layout)
        iplot(fig)






cf.set_config_file(offline=False, world_readable=True, theme='pearl')
