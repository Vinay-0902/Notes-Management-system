from database.connection import database_config,cursor
# create function defination add data to table

def addUser(username:str, email:str, password:str):
    try:
        add_user_query="""
                        INSERT INTO USERS(USERNAME, EMAIL, PASSWORD)
                        VALUES(%s,%s,%s);"""
        cursor.execute(add_user_query,(username,email,password))
        database_config.commit()
        return True
    except Exception as e:
        return f"Somthing wrong in database/utility.py:{e}"

# check weather the user in users table or not
def checkUserStatus(username:str):
    try:
        check_user_query="""SELECT USERID FROM USERS WHERE EMAIL=%s;"""
        cursor.execute(check_user_query,(username,))
        userid = cursor.fetchone()#(user,id)
        if userid:
            return True
        else:
            return False
    except Exception as e:
        return f"Something wrong in database/utility.py:{e}"

def getPasswordFromDB(username:str):
    try:
        check_user_query="""SELECT PASSWORD FROM USERS WHERE EMAIL=%s;"""
        cursor.execute(check_user_query,(username,))
        password = cursor.fetchone()[0]#(user,id)
        return password
    except Exception as e:
        return f"Something wrong in database/utility.py:{e}"

def updatepassword(username:str,newpassword:str):
    try:
        update_password_query="""UPDATE USERS SET PASSWORD = %s WHERE EMAIL = %s"""
        cursor.execute(update_password_query,(newpassword,username))
        row_count =cursor.rowcount
        if row_count ==1:
            database_config.commit()
            return True
        else:
            database_config.rollback()
            return False
        

    except Exception as e:
        return f"Something wrong in database/utility.py:{e}"
    


def addNotesInDB(email:str, title:str, content:str):
    #get userid from user table
    try:
        get_userid_query ="""select userid from users where email =%s;"""
        cursor.execute(get_userid_query,(email,))
        userid=cursor.fetchone()[0]
        add_notes_query =   """insert into notes(userid,email,title,content)
                            values(%s, %s,%s, %s);"""
        cursor.execute(add_notes_query,(userid, email, title, content))
        database_config.commit()
        return True
    except:
        return False
    

# get content from DB using note_id
def getNoteByID(note_id, email):
    query = """
            SELECT noteid, title, content
            FROM notes
            WHERE noteid=%s AND email=%s
            """
    cursor.execute(query,(note_id, email))
    return cursor.fetchone()

def updateNoteInDB(note_id, email, title, content):
    query = """
    UPDATE notes
    SET title=%s, content=%s
    WHERE noteid=%s AND email=%s
    """
    cursor.execute(query, (title, content, note_id, email))
    database_config.commit()
    return cursor.rowcount == 1

def deleteNoteFromDB(note_id, email):
    query = """
    DELETE FROM notes
    WHERE noteid=%s AND email=%s
    """
    cursor.execute(query, (note_id, email))
    database_config.commit()
    return cursor.rowcount == 1


def getNotesFromDB(email):
    query = "SELECT noteid, title, content FROM notes WHERE email=%s"
    cursor.execute(query, (email,))
    return cursor.fetchall()
