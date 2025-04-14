import sqlite3

#insertions
location_insert = """INSERT INTO tbl_location_v2(LOCATION, LOCATION_CODE) VALUES (?, ?) ON CONFLICT(LOCATION) DO NOTHING;"""
route_insert = """INSERT INTO tbl_route_v3(ROUTE_START, ROUTE_END) VALUES (?, ?) ON CONFLICT(ROUTE_START, ROUTE_END) DO NOTHING;"""
train_insert = """INSERT INTO tbl_train_v3(TRAIN_NUMBER, ROUTE) VALUES (?, ?) ON CONFLICT(TRAIN_NUMBER, ROUTE) DO NOTHING;"""
stop_insert = """INSERT INTO tbl_stop_v4(TRAIN, ROUTE_STOP, ROUTE_NEXT_STOP) VALUES (?, ?, ?) ON CONFLICT(TRAIN, ROUTE_STOP, ROUTE_NEXT_STOP) DO NOTHING;"""
via_data_insert = """INSERT INTO tbl_via_data_v4(TRAIN_STOP, SCHEDULE_DATETIME, ARRIVAL_DATETIME, MINUTES_LATE, DATE_TRAIN) VALUES (?, ?, ?, ?, ?) ON CONFLICT(TRAIN_STOP, DATE_TRAIN) DO NOTHING;"""

#queries
location_query = """SELECT LOCATION_ID FROM tbl_location_v2 WHERE LOCATION = ?"""
route_query = """SELECT ROUTE_ID FROM tbl_route_v3 WHERE ROUTE_START = ? AND ROUTE_END = ?"""
train_query = """SELECT TRAIN_ID FROM tbl_train_v3 WHERE TRAIN_NUMBER = ? AND ROUTE = ?"""
stop_query = """SELECT STOP_ID FROM tbl_stop_v4 WHERE TRAIN = ? AND ROUTE_STOP = ? AND ROUTE_NEXT_STOP = ?"""

def get_table_index(query, string, cur):
    #get location index
    cur.execute(location_query, (string,))
    row = cur.fetchone()
    to_idx = row[0]
    return(to_idx)

def set_location(location_data, cur, con):
    #location_data expects location and location code
    db_return_value = cur.execute(location_insert, location_data)
    con.commit()
    return db_return_value

def get_location(location_string, cur):
    #get location index
    print(location_string)
    cur.execute(location_query, (location_string,))
    row = cur.fetchone()
    to_idx = row[0]
    return(to_idx)

def set_route(route_data, cur, con):
    #location_data expects route start and route end
    db_return_value = cur.execute(route_insert, route_data)
    con.commit()
    return db_return_value

def get_route(from_idx, to_idx, cur):
    #get route index
    cur.execute(route_query, (from_idx, to_idx))
    row = cur.fetchone()
    route_idx = row[0]
    return(route_idx)

def set_train(train_data, cur, con):
    #location_data expects train number and route
    db_return_value = cur.execute(train_insert, train_data)
    con.commit()
    return db_return_value

def get_train(train_number, route_idx, cur):
    #get train index
    cur.execute(train_query, (train_number, route_idx))
    row = cur.fetchone()
    train_idx = row[0]
    return(train_idx)

def set_stop(stop_data, cur, con):
    #location_data expects train, route stop and route next stop
    db_return_value = cur.execute(stop_insert, stop_data)
    con.commit()
    return db_return_value

def get_stop(train_idx, route_stop, route_next_stop, cur):
    #get stop index
    cur.execute(stop_query, (train_idx, route_stop, route_next_stop))
    row = cur.fetchone()
    stop_idx = row[0]
    return(stop_idx)

def set_via_data(via_data, cur, con):
    #location_data expects train stop, schedule datetime, arrival datetime, minutes late and date train
    db_return_value = cur.execute(via_data_insert, via_data)
    con.commit()
    return db_return_value