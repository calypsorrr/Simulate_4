import mysql.connector
from mysql.connector import errorcode

# Obtain connection string information from the portal

config = {
  'host':'goalgetter.mysql.database.azure.com',
  'user':'goal',
  'password':'KdGaBhg4?7643',
  'database':'access_key',
  'client_flags': [mysql.connector.ClientFlag.SSL],
  'ssl_ca': 'cert/DigiCertGlobalRootG2.crt.pem'
}

# Construct connection string

try:
   conn = mysql.connector.connect(**config)
   print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cursor = conn.cursor()

  cursor.execute("SELECT notion_access_key FROM key_access WHERE email = 'boclaes102@gmail.com'")
  result = cursor.fetchall()
  x = result[0]
  access_key_notion = ''.join(x)
  rows = cursor.fetchall()
  print("Read",cursor.rowcount,"row(s) of data.")
  print(access_key_notion)
  conn.commit()
  cursor.close()
  conn.close()
  print("Done")

