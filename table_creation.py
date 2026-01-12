import sqlite3

db_name  = "ocr_master.db"
con = None


try:
    # establishing connenction
    con = sqlite3.connect(db_name)
    cur = con.cursor()


    #creating table:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocr_line_items ( 
            Invoice_No TEXT NOT NULL,
            line_item_id INTEGER NOT NULL,
            Issue_Date TEXT,
            billed_to TEXT,
            billed_by TEXT,
            Description TEXT,
            Category TEXT,
            Amount REAL,
            Grand_Total REAL,
            source_file TEXT, -- column name case for consistency
            PRIMARY KEY (Invoice_No, line_item_id)
        )
    """)

     #closing the connection
    con.commit()
    print(f"table succeffully created")

except sqlite3.Error as e:
    print(f"error is {e}")


finally:
    if con:
        con.close()




