import mysql.connector

config = {
    'user': 'cray7',
    'password': 'dgu1234!',
    'host': '43.200.153.107',
    'port': '57223',
    'database': 'cray7db'
}

conn = mysql.connector.connect(**config)

# imgs which will be uploaded
imgs = []

# Start of Cursor
cursor = conn.cursor()

insert_query = "INSERT INTO blue(image) VALUES (%s)" 
for img in imgs :
    data = (img,)
    print(data)
    cursor.execute(insert_query, data)
    conn.commit()

# Termination of Cursor
cursor.close()
