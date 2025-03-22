import os
import requests
import pandas as pd
from datetime import datetime
import duckdb


def get_query_results(query_str):
    '''
    inputs: query_str = query string to search for
    output: dictionary of api result
    notes:
        hard coded limit to 500 which is max allowed per api docs
        hard coded types=Person to limit to results which are people
    '''

    h_dict = {'Accept': 'application/json'}
    p_dict = {
                'key': api_key,
                'types': 'Person',
                'limit': 500,
                'indent': True,
                'languages': 'en',
                'query': query_str
            }
    
    resp = requests.get(
                url = service_url, 
                headers = h_dict, 
                params = p_dict
            )
    
    if resp.status_code != 200:
        raise(Exception('{} error, {}'.format(resp.status_code, resp.reason)))
    else:
        resp_json = resp.json()
    
    return(resp_json)


def get_query_df(query_str):
    '''
    inputs: query_str = query string to search for
    output: df of name, category, rnk
    '''
    
    df = pd.DataFrame(columns=["name", 'cat', 'cat_rnk']) #initialize empty df
    query_results = get_query_results(query_str=query_str)['itemListElement']
    
    for cat_rnk, result in enumerate(query_results):
        #loop over all query_results to pull out names
        result_dict = result['result']
        result_name = result_dict['name']
        result_name_series = pd.DataFrame([[result_name, query_str, cat_rnk]], columns=df.columns) 
        df = pd.concat([df, result_name_series], ignore_index=True)
        
    return(df)


def get_output_df():
    '''
    output: final df ready for saving to csv
    '''

    df = pd.DataFrame(columns=["name", 'cat', 'cat_rnk']) #init empty df
    query_list = ['Actor', 'NFL', 'NBA', 'Crypto', 'Politician', 'Billionaire', 'Influencer'] #TODO: store list in csv or DB

    for query in query_list:
        #call api and get list of names for each query item
        print('\nGetting Names for: {}'.format(query))
        query_df = get_query_df(query_str=query) #get df of names matching query
        df = pd.concat([df, query_df], ignore_index=True) #add query_df to df


    #add calculated fields
    df.sort_values(by = ['name', 'cat_rnk', 'cat'], inplace = True)
    df.reset_index(drop=True, inplace=True)
    df['cat_rnk'] = df['cat_rnk'].apply(lambda x: int(x)) #needs to be an int for below transforms to work
    df['num_cats'] = df.groupby(['name'])['cat'].transform('count') # count of rows (ie number of serach terms the name came up in)
    df['bst_cat_rnk'] = df.groupby(['name'])['cat_rnk'].transform('min') # lowest rnk will be the best match
    df['bst_cat_rnk_idx'] = df.groupby(['name'])['cat_rnk'].transform('idxmin') #add index of best match so we can do below to get associated cat
    df['bst_cat'] = df.loc[df.bst_cat_rnk_idx, 'cat'].values #add best cat
    df['dt'] = datetime.now().strftime("%Y-%m-%d") #add current date

    # remove un-needed cols and duplicate rows
    df.drop(['cat','cat_rnk', 'bst_cat_rnk_idx'], axis=1, inplace=True)
    df.drop_duplicates(subset='name', keep='first', inplace=True)

    return(df)


def stage_poi_raw_data():

    sql_query = '''
        CREATE OR REPLACE TABLE poi_stage AS
            SELECT *
            FROM read_csv_auto(
                '{csv_path}',
                normalize_names=True
            )
    '''.format(csv_path=output_path)

    with duckdb.connect(duckdb_path) as con:
        con.sql(sql_query)


def merge_into_poi_hist():
    sql_query_ctine = '''
        CREATE TABLE IF NOT EXISTS poi_hist (
            name VARCHAR,
            num_cats BIGINT,
            best_cat_rnk BIGINT,
            bst_cat VARCHAR,
            dt DATE
        )
    '''

    sql_query_del = '''
        DELETE
        FROM poi_hist
        WHERE dt = (select max(dt) from poi_stage)
    '''

    sql_query_insrt = '''
        INSERT INTO poi_hist
        SELECT *
        FROM poi_stage
    '''

    with duckdb.connect(duckdb_path) as con:
        con.sql(sql_query_ctine)
        con.sql(sql_query_del)
        con.sql(sql_query_insrt)


if __name__ == '__main__': 

    #init variables
    api_key = os.environ.get("GOOGLE_API_KEY")
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    output_path = 'data/poi_raw_data.csv'
    duckdb_path = 'data/person_of_influence.db'

    #get output_df and save results to csv
    output_df = get_output_df() 
    output_df.to_csv(output_path, index=False, encoding='utf-8', sep=',')


    #stage poi_raw_data and merge into a hist table
    stage_poi_raw_data()
    merge_into_poi_hist()


    #superbasic log of last run. Mainly to ensure always have a file to commit/push in event csv is identical to prior run
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs/last_run.txt', 'w') as file:
        file.write('Last Run: {ts}'.format(ts=ts))
