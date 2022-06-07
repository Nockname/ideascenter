import email
import json
import os
import base64 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid 
import hashlib
import glob
from flask import Flask, request, render_template, redirect
app = Flask(__name__)

users = []
with open("courses.txt", encoding='utf-8') as currentFile:
        data = currentFile.read().split("\n")
        
MY_ADDRESS = "princetonideascenter@gmail.com"         # Replace with yours
MY_PASSWORD = "jppsjxxzlhksqvls"      # Replace with yours

HOST_ADDRESS = 'smtp.gmail.com'   # Replace with yours
HOST_PORT = 587                          # Replace with yours

# PROBLEM CREATION/EDITING/SOLUTION GRADING

def admin_check(req):
    for filename in glob.glob(os.path.join("users/", '*.json')): #only process .JSON files in folder.      
        with open(filename, encoding='utf-8') as currentFile:
            data = json.load(currentFile)
            if req.cookies.get("userid") == data[3] and data[4]:
                return data
    return False

def encrypt(raw):
    data_bytes = raw.encode("utf-8")
    return base64.b64encode(data_bytes)

def decrypt(enc):
    data_bytes = enc.decode("utf-8")
    return base64.b64decode(data_bytes)

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "POST":
        tuteeClass = request.form["thisClass"]
        print(encrypt(tuteeClass))
        print(decrypt(encrypt(tuteeClass)))

        if tuteeClass != "" and tuteeClass in data:
            id = encrypt(tuteeClass)
            return redirect(f"/sign_up?={id}")
        
    user_id = request.cookies.get('userid')
    if user_id != "NotIn" and user_id != "" and user_id != None:
        with open(glob.glob(os.path.join("users/", '{}.json'.format(user_id)))[0], encoding='utf-8') as currentFile:
            tutee_data = json.load(currentFile)
            
    else:
        tutee_data = ["", ""]
            
    return render_template(
        "index.html",
        courses = data,
        the_username = tutee_data[1]
    )
    
@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

def email_tutors(tuteeClass, email, username):
    
    count = 0
    
    for filename in glob.glob(os.path.join("tutors/", '*.json')): #only process .JSON files in folder.      
        with open(filename, encoding='utf-8') as currentFile:
            data = json.load(currentFile)
            if tuteeClass in data or "any" in data:
                
                count+=1
    
                RECIPIENT_ADDRESS = data[0]  # Replace with yours
                # Connection with the server
                server = smtplib.SMTP(host=HOST_ADDRESS, port=HOST_PORT)
                server.starttls()
                server.login(MY_ADDRESS, MY_PASSWORD)

                # Creation of the MIMEMultipart Object
                message = MIMEMultipart()

                # Setup of MIMEMultipart Object Header
                message['From'] = MY_ADDRESS
                message['To'] = RECIPIENT_ADDRESS
                message['Subject'] = "Tutoring Match"

                # Creation of a MIMEText Part
                textPart = MIMEText("Dear {},\n\nYou have a been paired with {}, a tutee seeking tutoring in {}. Please email them at {} to begin tutoring (make sure to CC AndreaDinan@princetonk12.org)!\n\nSincerely,\nPrinceton High School's Ideas Center".format(data[1], username, tuteeClass, email), 'plain')

                # Part attachment
                message.attach(textPart)

                # Send Email and close connection
                server.send_message(message)
                server.quit()
                
    if count == 0:
        RECIPIENT_ADDRESS = email  # Replace with yours
        # Connection with the server
        server = smtplib.SMTP(host=HOST_ADDRESS, port=HOST_PORT)
        server.starttls()
        server.login(MY_ADDRESS, MY_PASSWORD)

        # Creation of the MIMEMultipart Object
        message = MIMEMultipart()

        # Setup of MIMEMultipart Object Header
        message['From'] = MY_ADDRESS
        message['To'] = RECIPIENT_ADDRESS
        message['Subject'] = "Tutoring Update"

        # Creation of a MIMEText Part
        textPart = MIMEText("Dear {},\n\nUnfortunately, no tutors are currently avaliable to tutor in {}. Please try again later or request a different course.\n\nSincerely,\nPrinceton High School's Ideas Center".format(username, tuteeClass), 'plain')

        # Part attachment
        message.attach(textPart)

        # Send Email and close connection
        server.send_message(message)
        server.quit()
        
    else:
        RECIPIENT_ADDRESS = email  # Replace with yours
        # Connection with the server
        server = smtplib.SMTP(host=HOST_ADDRESS, port=HOST_PORT)
        server.starttls()
        server.login(MY_ADDRESS, MY_PASSWORD)

        # Creation of the MIMEMultipart Object
        message = MIMEMultipart()

        # Setup of MIMEMultipart Object Header
        message['From'] = MY_ADDRESS
        message['To'] = RECIPIENT_ADDRESS
        message['Subject'] = "Tutoring Request Conformation"

        # Creation of a MIMEText Part
        textPart = MIMEText("Dear {},\n\nThere are {} tutors who are available to tutor {}. They have been notified of your tutoring request, and if they are avaliable, they will email you soon.\n\nSincerely,\nPrinceton High School's Ideas Center".format(username, count, tuteeClass), 'plain')

        # Part attachment
        message.attach(textPart)

        # Send Email and close connection
        server.send_message(message)
        
    server.quit()

@app.route("/availability", methods=["GET", "POST"])
def availability():
    
    if request.method == "POST":
        user_class = base64.b64decode(request.url.split("?=")[-1][2:-1]).decode("utf-8")
        user_id = request.cookies.get('userid')
        print(user_class, user_id)
        
        with open(glob.glob(os.path.join("users/", '{}.json'.format(user_id)))[0], encoding='utf-8') as currentFile:
            tutee_data = json.load(currentFile)
            email_tutors(user_class, tutee_data[0], tutee_data[1])
        
        return redirect(f"/thank_you")
    
    return render_template("availability.html", courses = data)

@app.route("/resources", methods=["GET"])
def resources():
    return render_template("resources.html")

@app.route("/thank_you", methods=["GET"])
def thank_you():
    return render_template("thank_you.html")
    
# LOGIN / SECURITY

def hash_password(password):
    salt = uuid.uuid4().hex 
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password): 
    password, salt = hashed_password.split(':') 
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def is_admin(email, username, hashedPass):
    if email == "jierueic@gmail.com" and username == "knosmos" and check_password("c8cd035724dd2cc48f87c17f21c4cb7f9bdf9cf767bc88e5fcefefbf8f73dd0f:533a7722507f4d1da1bdfca16bf70675", hashedPass):
        return True
    if email == "nicholas.d.hagedorn@gmail.com" and username == "Nickname" and check_password("6d6438706baee7793b76597a15628859cf9b47c0097f814d06187247d120ceb7:6316c3b35173482db353c2a2baa8301e", hashedPass):
        return True
    
    return False

def is_account(cred, email_or_username, password):
    return check_password( cred[2], password) and (email_or_username == cred[0] or email_or_username == cred[1])
    
class User:
    def __init__(self, email, username, password):
        self.user_ID = str(id(str(email)+str(username)+str(hash_password(password))))
        self.isAdmin = is_admin(email, username, password)
        self.credentials = [email, username, hash_password(password), self.user_ID, self.isAdmin] 
    
    def is_repeat(self, users):
        for otherUser in users:
            if otherUser.credentials[0] == self.credentials[0] or otherUser.credentials[1] == self.credentials[1]:
                return True
        return False
    
    def store_account(self):
        open("users/" + self.user_ID + ".json", "w", encoding='utf-8').write(json.dumps(self.credentials))

@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        try:
            emailUsername = request.form["emailUsername"].strip()
            password = request.form["password"].strip()
            
            for filename in glob.glob(os.path.join("users/", '*.json')): #only process .JSON files in folder.      
                with open(filename, encoding='utf-8') as currentFile:
                    data = json.load(currentFile)
                    if is_account(data, emailUsername, password):

                        userID = data[3]
                        isAdmin = data[4]
                        
                        return render_template(
                            "log_in.html",
                            admin = isAdmin,
                            userid = userID
                        )
                        # return redirect(f"/?id={userID}") #change to put userID in the URL
        except:
            pass

    return render_template("log_in.html")

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User(email, username, password)
        if "@" in email and len(username) > 4 and len(password) > 4 and not user.is_repeat(users):
            print("works")
            user.store_account()
            userID = user.credentials[3]
            isAdmin = user.credentials[4]
            return render_template("sign_up.html", admin = isAdmin, userid = userID) #change to put userID in the URL
    return render_template("sign_up.html")

if __name__ == "__main__":
    app.run("0.0.0.0")
