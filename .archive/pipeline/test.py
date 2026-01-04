import sqlite3

#setup database connection
con = sqlite3.connect("via_data.db")
cur = con.cursor()

location_insert = """INSERT INTO tbl_location(LOCATION, LOCATION_CODE) VALUES (?, ?) ON CONFLICT(LOCATION) DO NOTHING;"""

def set_location(location_data, cur, con):
    #location_data expects location and location code
    db_return_value = cur.execute(location_insert, location_data)
    print(db_return_value)
    con.commit()
    return db_return_value

location_i = 'SUDBURY'
location_code_i = 'SUDB'
set_location((location_i, location_code_i), cur, con)