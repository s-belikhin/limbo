import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow.decorators import dag, task

vgsales = '/var/lib/airflow/airflow.git/dags/a.batalov/vgsales.csv'


default_args = {
    'owner': 's.belihin',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 7, 11),
    'schedule_interval': '0 13 * * *'
}


year = 1994 + hash(f's-belihin-38') % 23

@dag(default_args=default_args, catchup=False)
def z_lo_lesson_s_belihin_38():
    @task()
    def get_data():
        df = pd.read_csv(vgsales)
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype(int)
        df_year = df.query('Year == @year')
        return df_year


    @task()
    def best_game(df_year):
        best_g = df_year.loc[df_year['Global_Sales'].idxmax()]
        return best_g.to_csv(index=False)


    @task()
    def popular_game(df_year):
        top_sale_game = df_year.groupby('Genre', as_index=False).agg({'EU_Sales':'sum'}).sort_values('EU_Sales', ascending = False)
        max_value = top_sale_game['EU_Sales'].max()
        top_sale_game = top_sale_game[top_sale_game['EU_Sales'] == max_value]
        return top_sale_game.to_csv(index=False)


    @task()
    def popular_platform(df_year):
        top_platform = df_year.query('NA_Sales >= 1').groupby('Platform', as_index=False).agg(count_of_game=('Name','count')).sort_values('count_of_game', ascending = False)
        max_value = top_platform['count_of_game'].max()
        the_most_popular_platform = top_platform[top_platform['count_of_game'] == max_value]
        return the_most_popular_platform.to_csv(index=False)


    @task()
    def popular_publisher(df_year):
        avg_sale_game_JP = df_year.groupby('Publisher', as_index=False).agg({'JP_Sales':'mean'}).sort_values('JP_Sales', ascending = False)
        max_value = df_year['JP_Sales'].max()
        top_avg_sale_game_JP = df_year[df_year['JP_Sales'] == max_value]
        return top_avg_sale_game_JP.to_csv(index=False)


    @task()
    def EU_vs_JP(df_year):
        return (df_year.query("Year == @year").EU_Sales > df_year.query("Year == @year").JP_Sales).sum()


    @task()
    def print_data(best_g, top_sale_game, the_most_popular_platform, top_avg_sale_game_JP, count_EU_vs_JP):
        print(f'Best game for {year}')
        print(best_g)
        
        print(f'Most popular game genre in Europe for {year}')
        print(top_sale_game)

        print(f'Platform with the most games that sold more than one million copies in North America for {year}')
        print(the_most_popular_platform)
        
        print(f'Publisher with the highest average sales in Japan for {year}')
        print(top_avg_sale_game_JP)
       
        print(f'Number of games that sold better in Europe than in Japan for {year}')
        print(count_EU_vs_JP)

    df_year = get_data()
    
    
    best_g = best_game(df_year)
    top_sale_game = popular_game(df_year)
    the_most_popular_platform = popular_platform(df_year)
    top_avg_sale_game_JP = popular_publisher(df_year)
    count_EU_vs_JP = EU_vs_JP(df_year)
    print_data(best_g, top_sale_game, the_most_popular_platform, top_avg_sale_game_JP, count_EU_vs_JP)
    
    
z_lo_lesson_s_belihin_38 = z_lo_lesson_s_belihin_38()