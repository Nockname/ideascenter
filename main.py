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
pairing = {}
id_to_class = {}

with open("courses.txt", encoding='utf-8') as currentFile:
        data = currentFile.read().split("\n")
        
MY_ADDRESS = "princetonideascenter@gmail.com"         # Replace with yours
MY_PASSWORD = "jppsjxxzlhksqvls"      # Replace with yours

HOST_ADDRESS = 'smtp.gmail.com'   # Replace with yours
HOST_PORT = 587                          # Replace with yours

# PROBLEM CREATION/EDITING/SOLUTION GRADING

def get_log_in_info(user_id):
    with open(glob.glob(os.path.join("users/", '{}.json'.format(user_id)))[0], encoding='utf-8') as currentFile:
        return json.load(currentFile)

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
            return redirect(f"/sign_up?course={id}")
        
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

@app.route("/thank_you_tutor", methods=["GET"])
def thank_you_tutor():
    return render_template("thank_you_tutor.html")

def email_tutors(tuteeClass, email, username, tuteeID):
    
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

                # OLD, WITH EMAIL
                # textPart = MIMEText("Dear {},\n\nYou have a been paired with {}, a tutee seeking tutoring in {}. Please email them at {} to begin tutoring (make sure to CC AndreaDinan@princetonk12.org)!\n\nSincerely,\nPrinceton High School's Ideas Center".format(data[1], username, tuteeClass, email), 'plain')

                # NEW, WITH LINK
                textPart = MIMEText("Dear {},\n\nYou have a been paired with {}, a tutee seeking tutoring in {}. If you avaliable, please visit http://127.0.0.1:5000/sign_up_match?tutee={} to confirm your avaliability!\n\nSincerely,\nPrinceton High School's Ideas Center".format(data[1], username, tuteeClass, tuteeID), 'plain')

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
def email_update(tuteeClass, tuteeEmail, tuteeUsername, tutorEmail, tutorUsername, tutorID):
    
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
    message['Subject'] = "Potential Tutor"

    # Creation of a MIMEText Part
    textPart = MIMEText("Dear {},\n\n{} is a tutor ready to tutor you in {}. Check out their About Me page at http://127.0.0.1:5000/about?tutor={}. Please email them at {} and CC andredinan@princetonk12.org if you would like {} to be your tutor.\n\nSincerely,\nPrinceton High School's Ideas Center".format(
        tuteeUsername, tutorUsername, tuteeClass, tutorID, tutorEmail, tutorUsername), 'plain')

    # Part attachment
    message.attach(textPart)

    # Send Email and close connection
    server.send_message(message)
    server.quit()



@app.route("/availability", methods=["GET", "POST"])
def availability():
    
    if request.method == "POST":
        user_class = base64.b64decode(request.args.get("course")[2:-1]).decode("utf-8")
        user_id = request.cookies.get('userid')
        print(user_class, user_id)

        pairing[user_id] = []
        id_to_class[user_id] = user_class

        print(pairing)
        print(id_to_class)
        
        with open(glob.glob(os.path.join("users/", '{}.json'.format(user_id)))[0], encoding='utf-8') as currentFile:
            tutee_data = json.load(currentFile)
            email_tutors(user_class, tutee_data[0], tutee_data[1], tutee_data[3])
        
        return redirect(f"/thank_you")
    
    return render_template("availability.html", courses = data)

@app.route("/match", methods=["GET", "POST"])
def match():

    if request.url.split("?tutee=")[-1] in pairing and request.cookies.get('userid') not in pairing[request.url.split("?tutee=")[-1]]:
        tutor_id = request.cookies.get('userid')
        tutor_info = get_log_in_info(tutor_id)

        tutee_id = request.url.split("?tutee=")[-1]
        tutee_info = get_log_in_info(tutee_id)
        tutee_class = id_to_class[tutee_id]

        if request.method == "POST":
            pairing[tutee_id].append(tutor_info)
            if len(pairing[tutee_id]) == 1:
                email_update(tutee_class, tutee_info[0], tutee_info[1], tutor_info[0], tutor_info[1], tutor_info[3])
            return redirect(f"/thank_you_tutor")

        return render_template("match.html", tutor_info = tutor_info, tutee_info=tutee_info, tutee_class=tutee_class)

    return redirect(f"/")


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
        return "True"
    if email == "nicholas.d.hagedorn@gmail.com" and username == "Nickname" and check_password("6d6438706baee7793b76597a15628859cf9b47c0097f814d06187247d120ceb7:6316c3b35173482db353c2a2baa8301e", hashedPass):
        return "True"
    
    return "False"

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
        if "@" in email and len(username) > 2 and len(password) > 4 and not user.is_repeat(users):
            print("works")
            user.store_account()
            userID = user.credentials[3]
            isAdmin = user.credentials[4]
            return render_template("sign_up.html", admin = isAdmin, userid = userID) #change to put userID in the URL
    return render_template("sign_up.html")

@app.route("/sign_up_match", methods=["GET", "POST"])
def sign_up_match():
    if request.url.split("?tutee=")[-1] not in pairing:
        return redirect(f"/")
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User(email, username, password)
        if "@" in email and len(username) > 2 and len(password) > 4 and not user.is_repeat(users):
            print("works")
            user.store_account()
            userID = user.credentials[3]
            isAdmin = user.credentials[4]
            return render_template("sign_up_match.html", admin = isAdmin, userid = userID) #change to put userID in the URL
    return render_template("sign_up_match.html")

if __name__ == "__main__":
    app.run("0.0.0.0")
