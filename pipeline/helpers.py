import sqlite3
import pandas as pd

import database_helpers

def connect_to_database(database_name):
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    return con, cur

def get_clean_data(df):
    #transpose data
    df_t = df.transpose()
    #shift train name into column
    df_t = df_t.reset_index()
    #subset columns
    via_day_data = df_t[['times','index','departed','arrived', 'from', 'to', ]]

    # Initialize an empty list to store DataFrames with IDs
    flattened_dfs = []
    # Iterate over each row in x
    for idx, row in via_day_data.iterrows():

        # Iterate over each DataFrame in the sublist
        for df in row['times']:
            # Add the ID as a column to the DataFrame
            df['ID'] = row['index']
            df['departed'] = row['departed']
            df['arrived'] = row['arrived']
            df['from'] = row['from']
            df['to'] = row['to']
            # Append the DataFrame to the list
            flattened_dfs.append(df)

    test_2 = pd.DataFrame(flattened_dfs)

    #Clean up datetimes
    test_2['estimated'] = pd.to_datetime(test_2['estimated'], errors = 'coerce')
    test_2['scheduled'] = pd.to_datetime(test_2['scheduled'], errors = 'coerce')

    #subset columns for clean data
    via_day_data_clean = test_2[['station','code', 'ID','scheduled','estimated','departed','diffMin', 'arrived','from','to']].copy()

    via_day_data_clean['prev_station'] = via_day_data_clean.groupby('ID')['station'].shift(1)
    #last row of each train has NA - try to impute
    #via_day_data_clean.loc[(via_day_data_clean.station.upper() == via_day_data_clean.to), "next_stop"] = via_day_data_clean.to

    #create depature time column
    via_day_data_clean['train_departure_schedule'] = via_day_data_clean.groupby('ID')['scheduled'].transform('min')

    return via_day_data_clean


def json_data_to_database(json_data, con, cur):
    
    clean_data = get_clean_data(json_data)

    #add locations first because we need to add 'from' and 'to' locations (but these require the location code)
    for idex, row in clean_data.iterrows():
        #change to upper case to align with to/from variables
        location_i = row['station'].upper()
        location_code_i = row['code']
        database_helpers.set_location((location_i, location_code_i), cur, con)


    #process data
    for idx, row in clean_data.iterrows():

        #change to upper case to align with to/from variables
        from_i = row['from'].upper()
        to_i = row['to'].upper()
        location_i = row['station'].upper()
        previous_location_i = row['prev_station']
        if pd.isna(previous_location_i):
            previous_location_i = location_i
        else:
            previous_location_i = previous_location_i.upper()

        train_num = row['ID']

        departed_boolean = row['departed']
        arrived_boolean = row['arrived']

        scheduled_time = row['scheduled']
        estimated_time = row['estimated']
        time_diff = row['diffMin']
        train_departure_schedule = row['train_departure_schedule']

        #get location index
        location_idx = database_helpers.get_location(location_i, cur)
        #get previous location index
        previous_location_idx = database_helpers.get_location(previous_location_i, cur)
        #get to index
        to_idx = database_helpers.get_location(to_i, cur)
        #get from index
        from_idx = database_helpers.get_location(from_i, cur)

        #add to route table
        database_helpers.set_route((from_idx, to_idx), cur, con)

        #get route
        route_idx = database_helpers.get_route(from_idx, to_idx, cur)

        #add to train table
        print(train_num)
        print(route_idx)
        database_helpers.set_train((train_num, route_idx), cur, con)

        #get train
        train_idx = database_helpers.get_train(train_num, route_idx, cur)

        database_helpers.set_stop((train_idx, location_idx, previous_location_idx), cur, con)
        stop_idx = database_helpers.get_stop(train_idx, location_idx, previous_location_idx, cur)

        #If train has arrived and departed then save data
        if departed_boolean and arrived_boolean:
            if (not pd.isnull(scheduled_time)) and (not pd.isnull(estimated_time) and (not pd.isnull(time_diff)) and (not pd.isnull(train_departure_schedule))):
                data_tuple = (stop_idx, scheduled_time.strftime("%Y-%m-%d %H:%M:%S"), estimated_time.strftime("%Y-%m-%d %H:%M:%S"), time_diff, train_departure_schedule.strftime("%Y-%m-%d"))
                database_helpers.set_via_data(data_tuple, cur, con)


