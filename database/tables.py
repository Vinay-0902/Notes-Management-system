from database.connection import database_config,cursor

def create_tables():
    users_table_query ="""
                        CREATE TABLE IF NOT EXISTS USERS(
                        USERID INT AUTO_INCREMENT,
                        USERNAME VARCHAR(35) NOT NULL,
                        EMAIL VARCHAR(50) NOT NULL UNIQUE,
                        PASSWORD VARCHAR(25),
                        PRIMARY KEY(USERID)
                        );"""
    notes_table_query = """
                        CREATE TABLE IF NOT EXISTS NOTES(
                        NOTEID INT AUTO_INCREMENT,
                        USERID INT NOT NULL,
                        EMAIL VARCHAR(50) NOT NULL,
                        TITLE VARCHAR(100) NOT NULL,
                        CONTENT MEDIUMTEXT,
                        LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (NOTEID),
                        FOREIGN KEY (USERID) REFERENCES USERS(USERID)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
                        );
                        """
    
    cursor.execute(users_table_query)
    cursor.execute(notes_table_query)
   
    print("Table created Successfully")