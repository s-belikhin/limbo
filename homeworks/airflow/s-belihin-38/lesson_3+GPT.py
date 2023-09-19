import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow.decorators import dag, task

TOP_1M_DOMAINS = 'https://storage.yandexcloud.net/kc-startda/top-1m.csv'
TOP_1M_DOMAINS_FILE = '/var/lib/airflow/airflow.git/dags/s-belihin-38/top-1m.csv'


default_args = {
    'owner': 's.belihin',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 7, 11),
    'schedule_interval': '0 13 * * *'
}


@dag(default_args=default_args, catchup=False)
def lesson_3_s_belihin_38():
    @task()
    def get_data():
        top_doms = pd.read_csv(TOP_1M_DOMAINS)
        top_doms.to_csv(TOP_1M_DOMAINS_FILE, index=False)

    @task()
    def get_domains():
        top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
        top_data_df['extension'] = top_data_df['domain'].str.split('.').str[-1]
        df_top_domains = top_data_df.groupby('extension', as_index=False).agg(count_of_domains=('extension', 'count')).sort_values('count_of_domains', ascending=False)
        df_top_10_domains = df_top_domains.head(10)
        df_top_10_domains.to_csv('/var/lib/airflow/airflow.git/dags/s-belihin-38/df_top_10_domains.csv', index=False)

    @task()
    def get_longest_domains():
        top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
        max_length = top_data_df['domain'].str.len().max()
        longest_domains = top_data_df[top_data_df['domain'].str.len() == max_length]
        selected_domain = longest_domains['domain'].sort_values().iloc[0]
        longest_domains_row = top_data_df.loc[top_data_df['domain'] == selected_domain]
        longest_domains_row.to_csv('/var/lib/airflow/airflow.git/dags/s-belihin-38/longest_domains_row.csv', index=False)

    @task()
    def get_rank_airflow():
        top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
        rank_airflow_row = top_data_df.loc[top_data_df['domain'] == 'airflow.com']
        rank_airflow_row.to_csv('/var/lib/airflow/airflow.git/dags/s-belihin-38/rank_airflow_row.csv', index=False)

    @task()
    def print_data():
        df_top_10_domains = pd.read_csv('/var/lib/airflow/airflow.git/dags/s-belihin-38/df_top_10_domains.csv')
        longest_domains_row = pd.read_csv('/var/lib/airflow/airflow.git/dags/s-belihin-38/longest_domains_row.csv')
        rank_airflow_row = pd.read_csv('/var/lib/airflow/airflow.git/dags/s-belihin-38/rank_airflow_row.csv')

        print(f'Top 10 domains by number of domains')
        print(df_top_10_domains)

        print(f'Domain with the longest name (if multiple, take the first one in alphabetical order)')
        print(longest_domains_row)

        print(f'Rank of the domain airflow.com')
        print(rank_airflow_row)

    get_data_task = get_data()
    get_domains_task = get_domains()
    get_longest_domains_task = get_longest_domains()
    get_rank_airflow_task = get_rank_airflow()
    print_data_task = print_data()

    get_data_task >> get_domains_task >> get_longest_domains_task >> get_rank_airflow_task >> print_data_task


lesson_3_s_belihin_38_dag = lesson_3_s_belihin_38()
