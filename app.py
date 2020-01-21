from flask import Flask,render_template,request,url_for,redirect
import pyrebase
import json
from time import gmtime, strftime

#flask setup
app = Flask(__name__)

#firebase setup
with open("config.json",'r') as configuration_file:
    config = json.loads(configuration_file.read())

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

@app.route('/login',methods=['POST','GET'])
def login():
    if(request.method == "POST"):
        email = request.form['email']
        password = request.form['password']
        try:
            if(email and password):
                user = auth.sign_in_with_email_and_password(email,password)
            return redirect(url_for('home'))
        except Exception as e:
            print(f"error {e}")
            return "Wrong email or password"
    else:
        return render_template('login.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if(request.method == "POST"):
        email = request.form['email']
        password = request.form['password']
        try:
            if(email and password):
                user = auth.create_user_with_email_and_password(email,password)
            return redirect(url_for('login'))
        except Exception as e:
            print(f"error : {e}")
            return "Unable to signup"
    else:
        return render_template('signup.html')

@app.route('/home')
@app.route('/',methods=['GET','POST'])
def home():
    if(auth.current_user):
        if(request.method=='POST'):
            add_appointment()
            return redirect(url_for("home"))

        name = auth.current_user['email'].split('@')[0]

        patients = db.child("Appointments").child(name).get().val()

        def gen(patients):
            if(not patients):
                return

            for i,v in patients.items():
                yield v

        patients = gen(patients)

        return render_template("home.html",patients=patients if patients else [],doctor={"name":"Dr. "+name})
    else:
        return redirect(url_for('login'))

@app.route('/bot')
def bot():
    return "bot"

@app.route('/logout')
def logout():
    auth.current_user = None
    return redirect(url_for('login'))

def add_appointment():
    doc_name = auth.current_user['email'].split('@')[0]
    name = request.form['patient_name']
    time = request.form['patient_time']
    patient = {
    "name": name,
    "time": time
    }
    if(patient["name"] and patient["time"]):
        db.child("Appointments").child(doc_name).push(patient,auth.current_user['idToken'])

if __name__ == '__main__':
    app.run(debug=True)
