import os
from flask import Flask, redirect, url_for, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import string
import math

app = Flask(__name__)
app.secret_key = 'jkahdfiahdfidgfjdak'



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, primary_key=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"
    


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("home.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        if not email:
            return render_template("login.html", alert = "Email must be entered!", alert_type = "error")

        if not password:
            return render_template("login.html", alert = "Password must be entered!", alert_type = "error")
        
      
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return render_template("login.html", alert = "Invalid email or password!", alert_type = "error")
        
        session["user"] = {"name":user.name, "email":user.email}
        
        
        return redirect("/")

    return render_template("login.html")



@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']

        if not name:
            return render_template("signup.html", alert = "Name must be entered!", alert_type = "error")
        
        if len(name)<3 or len(name)>15:
            return render_template("signup.html", alert = "Name must be between 3 and 15 characters!", alert_type = "error") 

        if not email:
            return render_template("signup.html", alert = "Email must be entered!", alert_type = "error")
        
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return render_template("signup.html", alert = "Email contains invalid format or characters!", alert_type = "error")
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template("signup.html", alert = "The email is already used!", alert_type = "error")
        
        if not password:
            return render_template("signup.html", alert = "Password must be entered!", alert_type = "error")
        
        if len(password) < 8:
            return render_template("signup.html", alert = "Password must contain at least 8 characters!", alert_type = "error")

        if not confirm_password:
            return render_template("signup.html", alert = "You must confirm your password!", alert_type = "error")

        if password != confirm_password:
            return render_template("signup.html", alert = "The passwords do not match!", alert_type = "error")
        


        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)




        new_user = User(name=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        

        return redirect("/")


    return render_template("signup.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
    


@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        email = session["user"]["email"]
        user = User.query.filter_by(email=email).first()

        if user:
            db.session.delete(user)
            db.session.commit()
            session.clear()
            

    return render_template("login.html")

        





    
@app.route("/proportions", methods = ["POST", "GET"])
def proportions():
    result = ""
    slot_1 = ""
    slot_2 = ""
    slot_3 = ""
    slot_4 = ""

    if request.method == "POST":
        slot_1 = request.form['slot_1']
        slot_2 = request.form['slot_2']
        slot_3 = request.form['slot_3']
        slot_4 = request.form['slot_4']

        if not slot_1:
            return render_template("proportions.html", alert = "Slot 1 is empty!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
        
        if not slot_2:
            return render_template("proportions.html", alert = "Slot 2 is empty!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
        
        if not slot_3:
            return render_template("proportions.html", alert = "Slot 3 is empty!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
        
        if not slot_4:
            return render_template("proportions.html", alert = "Slot 4 is empty!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
        

        count = 0
        unknown = None

        if any(carattere in string.ascii_letters for carattere in slot_1):
            unknown = slot_1
            count = count + 1

        if any(carattere in string.ascii_letters for carattere in slot_2):
            unknown = slot_2
            count = count + 1

        if any(carattere in string.ascii_letters for carattere in slot_3):
            unknown = slot_3
            count = count + 1

        if any(carattere in string.ascii_letters for carattere in slot_4):
            unknown = slot_4
            count = count + 1

        if count == 0:
            return render_template("proportions.html", alert = "There are no unknowns!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)

        if count > 1:
            return render_template("proportions.html", alert = "There are too many unknowns!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)


        slot_1 = slot_1.replace(",",".")
        slot_2 = slot_2.replace(",",".")
        slot_3 = slot_3.replace(",",".")
        slot_4 = slot_4.replace(",",".")

        if unknown == slot_1:
            try:
              slot_2 = float(slot_2)
              slot_3 = float(slot_3)
              slot_4 = float(slot_4)
            except ValueError:
                return render_template("proportions.html", alert = "Invalid value!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
            
            result = slot_2 * slot_3 / slot_4

        elif unknown == slot_2:
            try:
              slot_1 = float(slot_1)
              slot_3 = float(slot_3)
              slot_4 = float(slot_4)
            except ValueError:
                return render_template("proportions.html", alert = "Invalid value!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
            
            result = slot_1 * slot_4 / slot_3

        elif unknown == slot_3:
            try:
              slot_1 = float(slot_1)
              slot_2 = float(slot_2)
              slot_4 = float(slot_4)
            except ValueError:
                return render_template("proportions.html", alert = "Invalid value!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
            
            result = slot_1 * slot_4 / slot_2

        else:
            try:
              slot_1 = float(slot_1)
              slot_2 = float(slot_2)
              slot_3 = float(slot_3)
            except ValueError:
                return render_template("proportions.html", alert = "Invalid value!", alert_type = "error", slot_1=slot_1, slot_2=slot_2, slot_3=slot_3, slot_4=slot_4)
            
            result = slot_2 * slot_3 / slot_1
           
        result = round(result,2)



    return render_template("proportions.html", slot_1=slot_1,  slot_2=slot_2, slot_3=slot_3, slot_4=slot_4, result=result)



#Check if number input is a number

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    

@app.route("/simplify", methods = ["GET", "POST"])
def simplify():
    simplified = None

    if request.method == "POST":
        num = request.form['num']
        den = request.form['den']

        num = num.replace(",",".")
        den = den.replace(",",".")


        if is_number(num) and is_number(den):
            num = float(num)
            den = float(den)

            if den == 0:
                return render_template("simplify.html", alert = "Denominator cannot be zero!", alert_type = "error", num=num, den=den)
            else:
                if num * den < 0:
                    sign = "-"
                else:
                    sign = "+"

                num = abs(num)
                den = abs(den)

            if num.is_integer() and den.is_integer():
                num = int(num)
                den = int(den)
                gcd = math.gcd(num, den)
                simplified = f"{num // gcd}/{den // gcd}"
            else:
                simplified = f"{sign}{num}/{den}"
                
        else:
            return render_template("simplify.html", alert = "Invalid input. Please enter valid numbers!", alert_type = "error", num=num, den=den)
        

    return render_template("simplify.html", simplified=simplified)









with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
   