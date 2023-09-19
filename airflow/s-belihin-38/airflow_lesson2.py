#22
import requests
import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

TOP_1M_DOMAINS = 'https://storage.yandexcloud.net/kc-startda/top-1m.csv'
TOP_1M_DOMAINS_FILE = 'top-1m.csv'


def get_data():
    # Здесь пока оставили запись в файл, как передавать переменую между тасками будет в третьем уроке
    top_doms = pd.read_csv(TOP_1M_DOMAINS)
    top_data = top_doms.to_csv(index=False)

    with open(TOP_1M_DOMAINS_FILE, 'w') as f:
        f.write(top_data)

                
def get_domen(): # Найти топ-10 доменных зон по численности доменов
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    top_data_df['extension'] = top_data_df['domain'].str.split('.').str[-1] # Извлечение расширений доменов
    df_top_domen = top_data_df.groupby('extension', as_index = False).agg(count_of_domen = ('extension', 'count')).sort_values('count_of_domen', ascending = False) # группировка по доменам
    df_top_10_domen = df_top_domen.head(10)
   
    with open('df_top_10_domen.csv', 'w') as f:
        f.write(df_top_10_domen.to_csv(index=False, header=False))


def get_longest_domains(): # Найти домен с самым длинным именем (если их несколько, то взять только первый в алфавитном порядке)
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    
    max_length = top_data_df['domain'].str.len().max() # определяем максимальную длину домена
    longest_domains = top_data_df[top_data_df['domain'].str.len() == max_length] # поиск этого домена 
    selected_domain = longest_domains['domain'].sort_values().iloc[0] # Выбор первого домена в алфавитном порядке
    longest_domains_row = top_data_df.loc[top_data_df['domain'] == selected_domain] # Вывод строки датафрейма с выбранным доменом
    

    with open('longest_domains_row.csv', 'w') as f:
        f.write(longest_domains_row.to_csv(index=False, header=False))
        

def get_rank_airflow(): # На каком месте находится домен airflow.com?
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    
    target_value = 'airflow.com' # Значение, которое необходимо найти
    rank_airflow_row = top_data_df.loc[top_data_df['domain'] == target_value] # Поиск строки с заданным значением

    with open('rank_airflow_row.csv', 'w') as f:
        f.write(rank_airflow_row.to_csv(index=False, header=False))


def print_data(ds):
    with open('df_top_10_domen.csv', 'r') as f:
        df_top_10_domen = f.read()
    with open('longest_domains_row.csv', 'r') as f:
        longest_domains_row = f.read()
    with open('rank_airflow_row.csv', 'r') as f:
        rank_airflow_row = f.read()
    date = ds

    print(f'Топ-10 доменных зон по численности доменов за дату {date}')
    print(df_top_10_domen)

    print(f'Домен с самым длинным именем (если их несколько, то только первый в алфавитном порядке) за дату {date}')
    print(longest_domains_row)
    
    print(f'На каком месте находится домен airflow.com на дату {date}')
    print(rank_airflow_row)


default_args = {
    'owner': 's.belihin',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 7, 11),
}
schedule_interval = '0 13 * * *'

dag = DAG('2_lesson_s-belihin-38_top_10_ru_new_first', default_args=default_args, schedule_interval=schedule_interval)

t1 = PythonOperator(task_id='get_data',
                    python_callable=get_data,
                    dag=dag)

t2_top_count_domen = PythonOperator(task_id='get_domen',
                    python_callable=get_domen,
                    dag=dag)

t2_longest_domains = PythonOperator(task_id='get_longest_domains',
                        python_callable=get_longest_domains,
                        dag=dag)

t2_rank_airflow = PythonOperator(task_id='get_rank_airflow',
                        python_callable=get_rank_airflow,
                        dag=dag)

t3 = PythonOperator(task_id='print_data',
                    python_callable=print_data,
                    dag=dag)

t1 >> [t2_top_count_domen, t2_longest_domains, t2_rank_airflow] >> t3

#ляськи-масяськи