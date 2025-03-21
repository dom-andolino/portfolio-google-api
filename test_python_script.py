import os
import requests
import pandas as pd
from datetime import datetime


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


def get_result_names(query_str):
    '''
    inputs: query_str = query string to search for
    output: df of name, category, rnk
    '''
    
    result_df = pd.DataFrame(columns=["name", 'cat', 'cat_rnk']) #initialize empty df
    results = get_query_results(query_str=query_str)['itemListElement']
    
    for cat_rnk, result in enumerate(results):
        #loop over all results to pull out names
        result_dict = result['result']
        result_name = result_dict['name']
        result_name_series = pd.DataFrame([[result_name, query_str, cat_rnk]], columns=result_df.columns) 
        result_df = pd.concat([result_df, result_name_series], ignore_index=True)
        
    return(result_df)



if __name__ == '__main__': 

    #init variables
    api_key = os.environ.get("GOOGLE_API_KEY")
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    output_path = 'data/test_python_script_output.csv'
    output_df = pd.DataFrame(columns=["name", 'cat', 'cat_rnk']) #init empty df
    query_list = ['Actor', 'Netflix', 'NFL', 'YouTube', 'Bitcoin', 'Politician', 'Billionaire'] #TODO: store list in csv or DB

    for query in query_list:
        #call api and get list of names for each query item
        print('\nGetting Names for: {}'.format(query))
        query_df = get_result_names(query_str=query) #get df of names matching query
        output_df = pd.concat([output_df, query_df], ignore_index=True) #add query_df to output_df


    #add calculated fields
    output_df.sort_values(by = ['name', 'cat_rnk', 'cat'], inplace = True)
    output_df.reset_index(drop=True, inplace=True)
    output_df['cat_rnk'] = output_df['cat_rnk'].apply(lambda x: int(x)) #needs to be an int for below transforms to work
    output_df['num_cats'] = output_df.groupby(['name'])['cat'].transform('count') # count of rows (ie number of serach terms the name came up in)
    output_df['bst_cat_rnk'] = output_df.groupby(['name'])['cat_rnk'].transform('min') # lowest rnk will be the best match
    output_df['bst_cat_rnk_idx'] = output_df.groupby(['name'])['cat_rnk'].transform('idxmin') #add index of best match so we can do below to get associated cat
    output_df['bst_cat'] = output_df.loc[output_df.bst_cat_rnk_idx, 'cat'].values #add best cat


    # remove un-needed cols and duplicate rows
    output_df.drop(['cat','cat_rnk', 'bst_cat_rnk_idx'], axis=1, inplace=True)
    output_df.drop_duplicates(subset='name', keep='first', inplace=True)

    #save results to csv
    output_df.to_csv(output_path, index=False, encoding='utf-8', sep=',')

    #superbasic log of last run. Mainly to ensure always have a file to commit/push in event csv is identical to prior run
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs/last_run.txt', 'w') as file:
        file.write('Last Run: {ts}'.format(ts=ts))
