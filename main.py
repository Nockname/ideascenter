
import json
import os
import random
import time
import markdown
import uuid 
import hashlib
import glob
from flask import Flask, request, render_template, redirect
app = Flask(__name__)

max_testcases = 10
games = []
users = []
adminPass = []

# PROBLEM CREATION/EDITING/SOLUTION GRADING

def admin_check(req):
    for filename in glob.glob(os.path.join("users/", '*.json')): #only process .JSON files in folder.      
        with open(filename, encoding='utf-8') as currentFile:
            data = json.load(currentFile)
            if req.cookies.get("userid") == data[3] and data[4]:
                return data
    return False

@app.route("/", methods=["GET", "POST"])
def index():
    
    with open("courses.txt", encoding='utf-8') as currentFile:
        data = currentFile.readlines()
        for i, line in enumerate(data):
            data[i] = ' '.join(line.split()[:-1])
            
        print(data)
    
    if request.method == "POST":
        try:
            name = request.form["player_name"]
            id = request.form["game_id"]
        except:
            return render_template(
                "index.html",
                courses = data
            )
        id = id.rstrip().upper()
        for game in games:
            if game.id == id and not game.is_duplicate_name(name):
                player = game.add_player(name)
                return redirect(f"/waiting?id={id}&player={player}")
    return render_template(
        "index.html",
        courses = data
    )

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
            user.store_account()
            userID = user.credentials[3]
            return redirect(f"/") #change to put userID in the URL
    return render_template("sign_up.html")

if __name__ == "__main__":
    app.run("0.0.0.0")
