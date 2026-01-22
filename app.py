from flask import Flask,request,redirect,url_for,session,render_template
import random
from database.tables import create_tables
from database.utility import addUser,checkUserStatus,getPasswordFromDB,updatepassword,addNotesInDB,getNoteByID,updateNoteInDB,deleteNoteFromDB,getNotesFromDB
from emailsend import emailSend

from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired, BadSignature

app=Flask(__name__)
app.secret_key="Vinay@123"

# Secure time based url serializer
serializer=URLSafeTimedSerializer(app.secret_key)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        if username=='' or password=="":
            return render_template("login.html",msg="Enter the details")
        if username=="" and password=="":
            return render_template("login.html",msg="Enter the details")
        if checkUserStatus(username=username): 
            if getPasswordFromDB(username=username)==password:
                session['user_email'] = username
                token = serializer.dumps(
                    username,
                    salt="login-auth"
                ) 
                return redirect(url_for("dashboard",token=token))
            return render_template("login.html",msg="Incorrect credentails")
        return render_template("login.html",msg="Account not found")
    msg = request.args.get("msg")
    if msg==None:
        return render_template("login.html")
    else:
        return render_template("login.html",msg=msg)



# generate otp token
def generate_otp_token(email):
    otp= random.randint(1000,9999)
    token=serializer.dumps(
        {"email":email,"otp":otp},
        salt="register_otp"
    )
    return otp,token


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        session["username"]=request.form["username"]
        session['email']=request.form["email"]
        session['password']=request.form["password"]

        if session["username"]=="":
            return render_template("register.html",msg="Enter The Username")
        
        if session["email"]=="":
            return render_template("register.html",msg="Enter The Email")
        if session["password"]=="":
            return render_template("register.html",msg="Enter The Password")
        if not checkUserStatus(session["email"])==True:

            # generate otp
            otp,token=generate_otp_token(session['email'])
            print("Register_otp token:",token)
            session["register_otp_token"]=token
            # otp share via email
            # print("OTP is",otp)# assume like this is otp
            body= f"""
                    Dear Customer {session["username"]},
                    This mail is to verify your Notes Management App!!!
                    Verifiction OTP is:{otp}.

                    This otp expires within 2 mins.

                    Don't replay to this email.

                    Best Regards
                    Notes Management App.
                    """
            emailSend(to_email=session['email'], subject="Notes Management OTP Verification", body=body)
            return redirect(url_for("verifyOTP"))
        return render_template('register.html',msg="Email is already Exists")
    return render_template("register.html")


@app.route("/register/verifyotp",methods=["GET","POST"])
def verifyOTP():
    if 'register_otp_token' not in session:
        return redirect(url_for("register"))
    if request.method=="POST":
        try:
            entered_otp=int(request.form["otp"])
            if entered_otp=="":
                return render_template("register.html",msg="Enter The OTP")
            data = serializer.loads(
                session["register_otp_token"],
                salt="register_otp",
                max_age=120 #2mins
            )
            #verify otp
            if entered_otp==data["otp"]:
                #add new user to table
                add_user= addUser(username=session["username"],email=session["email"],password=session["password"])
                if add_user:
                    session.pop("username")
                    session.pop("email")
                    session.pop("password")
                    
                    return render_template("login.html",msg="Successfully")
        except SignatureExpired:
            return render_template("verifyotp.html",msg="OTP Expired")
        except BadSignature:
            return render_template("verifyotp.html",msg="Invalid OTP URL")

        return render_template("verifyotp.html",msg="Invaild otp")
    

    return render_template("verifyotp.html")


@app.route("/forgotPassword",methods=["GET","POST"])
def forgot_password():
    if request.method=="POST":
        email=request.form["email"]
        if email=="":
            return render_template("forgotpassword.html",msg="Enter The Email")
        if checkUserStatus(username=email):
            # generating forgot password token
            token=serializer.dumps(
                email,salt="forgot_password"
            )
           
            # generate reset link
            reset_link=url_for('reset_password',token=token, _external=True)

            #send reset password link via email
            body=f"""
                    Dear Customer,
                    This mail is to update your Notes Management App Password!!!
                    Password reset link:{reset_link}.

                    This link expires within 10 mins.

                    Don't replay to this email.

                    Best Regards
                    Notes Management App.
                    """
            emailSend(
                to_email=email,
                subject="Notes APP Password Reset Request!!",
                body=body
            )
            return redirect(url_for("login",msg="Check your emaill! Password reset successfully"))
        
        return redirect(url_for("login",msg="User Email not found"))



    return render_template("forgotpassword.html")


@app.route("/resetpassword/<token>",methods=["GET","POST"])
def reset_password(token):
    try:
        email=serializer.loads(token,
                            salt="forgot_password",
                            max_age=600)
    except SignatureExpired:
        return redirect(url_for("forgot_password",msg="Link Expired"))
    except BadSignature:
        return redirect(url_for("forgot_password",msg="Invalid Url"))
    # get data from form
    if request.method=="POST":
        new_password=request.form['password']
        # update new password in database
        if updatepassword(username=email,newpassword=new_password):

        #redirect to login page
            return redirect(url_for("login",msg="Password reset successfully"))
        return redirect(url_for("login",msg="Password Not updated"))


    return render_template("resetpassword.html",token=token)


#get email from login - auth token
def verify_login_token(token):
    try:
        email=serializer.loads(
            token,
            salt="login-auth",
            max_age=7200
        )
        return email
    except:
        return None



@app.route("/dashboard/<token>", methods=["GET","POST"])
def dashboard(token):
    email=verify_login_token(token)
    if 'user_email' not in session or not email:
        return redirect(url_for('login', msg="Please login"))
    email = session['user_email']
    #get notes from DB
    notes=getNotesFromDB(email=email)
   
   
    return render_template("dashboard.html",token=token,username=email,notes=notes)
    
    
# add new notes
@app.route("/dashboard/addnotes/<token>", methods=["GET","POST"])
def add_notes(token):
    email=verify_login_token(token)
    if 'user_email' not in session or not email:
        return redirect(url_for('login', msg="Login Expired"))
    email = session['user_email']
    if request.method == "POST":
        title=request.form["title"]
        content=request.form["content"]


        #add notes in database
        if addNotesInDB(email=email,title=title,content=content):
            return redirect(url_for("dashboard",token=token, msg="Notes Added succesfully"))
        else:
            return redirect(url_for("add_notes",token=token, msg="Notes Not updated"))
    

    return render_template("add_notes.html",token=token)


# update content route
@app.route("/dashboard/update/note_id=<int:note_id>/<token>",methods = ["GET", "POST"])
def edit_note(token, note_id):
    email=verify_login_token(token)
    if 'user_email' not in session or not email:
        return redirect(url_for('login', msg="Login Expired"))
    email = session['user_email']
    
    
    #get new content from app
    if request.method=="POST":
        title=request.form["title"]
        content=request.form["content"]
        #update new content in DB
        updateNoteInDB(note_id=note_id,email=email,title=title,content=content)
        return redirect(url_for('dashboard',token=token,msg="Note updated"))

    #get old content from DB using note_id
    note= getNoteByID(note_id=note_id, email=email)




    return render_template("edit_notes.html",note=note, token=token)


@app.route("/dashboard/delete/note_id=<int:note_id>/<token>",methods = ["GET", "POST"])
def delete_note(token, note_id):
    email=verify_login_token(token)
    if 'user_email' not in session or not email:
        return redirect(url_for('login', msg="Login Expired"))
    email = session['user_email']
        #delete notes in DB
    deleteNoteFromDB(note_id=note_id,email=email)   




    return redirect(url_for("dashboard",token=token))

#logout route

@app.route("/logout/<token>")
def logout(token):
    # Clear any session data
    session.clear()
    # You can also expire the token (just ignore it)
    return redirect(url_for("login", msg="Logged out successfully"))









if __name__=="__main__":
    create_tables()
    app.run(debug=True)