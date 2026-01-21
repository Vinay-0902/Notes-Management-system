import mysql.connector as SQLC

database_config =  SQLC.connect(
                        host = "localhost",
                        user= "root",
                        password="Vinay@9959793131",
                        database= "notes_management"
)
# 2. create cursor object
cursor = database_config.cursor()
 


# print(database_config)
# print(cursor)


# #creating data base
# create_database_query= "CREATE DATABASE IF NOT EXISTS ANIMALS"

# #3. execute() function is used to excute the sql queries
# cursor.execute(create_database_query)
# print("Database created successfully")
# #use database
# cursor.execute("USE ANIMALS")

# # selecting database
# animal_table_query ="""
#                     CREATE TABLE ANIMAL(
#                     NAME VARCHAR(30),
#                     AGE INT
#                     );"""

# cursor.execute(animal_table_query)
# print(cursor)
# print("Table created successfully")