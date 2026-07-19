from flask import Flask, request, render_template, session, redirect, url_for
import ehr
import bcrypt

app = Flask(__name__)
app.secret_key = "your_super_secret_key"

@app.route("/")
def nohome():
    return redirect("/login")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" :
        user=request.form.get("USER")
        pwrd=request.form.get("PASSWORD")
        userinfo=ehr.login(user)
        if not userinfo:
            return render_template("login.html" , error="Invalid user or password")
        truepwd=userinfo["password_hash"]
        truepwd=truepwd.encode("utf-8")
        pwrd = pwrd.encode("utf-8")
        if user and bcrypt.checkpw(pwrd, truepwd):
            print("You have logged in")
            
            session["employee_id"]=userinfo["employee_id"]
            session["user"]= userinfo["username"]
            session["password"]=userinfo["password_hash"]
            session["role"]=userinfo["role"]

            return redirect("/menu")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first=request.form.get("FIRST")
        last=request.form.get("LAST")
        user=request.form.get("USER")
        password=request.form.get("PASSWORD")
        created=ehr.sign_up(first,last,user,password)

        return redirect("/login")
        
    return render_template("signup.html")

@app.route("/menu")
def menu():
    if "employee_id" not in session:
        return redirect("/login")
    
    return render_template("menu.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if "employee_id" not in session:
        return redirect("/login")
    if session["role"] != "Doctor":
        return "Access Denied", 403
    if request.method == "POST":

        patient_id = ehr.add_patient(request.form)
        return f"Success! ID: {patient_id}"
    #this is what is rendered when the user goes to the add route "GET" request
    return render_template("add_patient.html", columns=ehr.demographics[1:])  # Exclude the "Id" column since it will be generated automatically

@app.route("/search", methods=["GET", "POST"])
def search():
    if "employee_id" not in session:
        return redirect("/login")
    if request.method == "POST": #if we are sending data back to backend 
        # we have a form that exists in search_patients.html to grad the first and last name of patient 
        fname = request.form.get("FIRST") #request submission of FIRST
        lname = request.form.get("LAST") #Requests Submission in LAST
        option = request.form.get("option")
        patient_data = ehr.search_patient(fname, lname, option) #runs the search_patient method and saves the return of the method
        return render_template("search_results.html", option=option,results=patient_data) #return results from above function

    return render_template("search_patient.html")

@app.route("/addmenu", methods=["GET", "POST"])
def addinfo_patient():
    if "employee_id" not in session:
        return redirect("/login")
    
    patient_id=None

    if request.method == "POST": #the add.html is a submission form and will perform these actions when the user submits the form
        stage=request.form.get("stage") #since we have multiple pages in the route, stage determines which page we are on find or update
        if stage == "find":
            fname= request.form.get("FIRST")
           
            lname= request.form.get("LAST")

            category= request.form.get("category")

            table = ehr.get_tablecolumns(category)
           
            patient_id=ehr.find_patient(fname,lname)


            if patient_id:

                #this is the stage==update page we redirect to after the form of add.html is submitted
                return render_template("add2.html", category=category, patient_id=patient_id, table=table) 

        elif stage == "update":
            data = {}

            category=request.form.get("category")

            table=ehr.get_tablecolumns(category)

            for column in table:
                data[column] = request.form.get(column)

            patient_id= request.form.get("patient_id")

            patient_data=ehr.add_info(patient_id, data, category, table)

            print("This is the id", patient_id)
            print("this is the data", data)
            print("this is the category", category)
            print("this is the table",table)
            
            #patient_data=ehr.add_info(patient_id, data, category, table)
             #this is the tablechoice that was passed from the add.html page to determine which table to add info too

            
            #return render_template("addview.html", results=patient_data)
    
    return render_template("add.html") #the first page that is rendered when the user goes to the addinfo_patient route "GET" request

@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()

    return redirect("/login")
  

if __name__ == "__main__":
    app.run(debug=True)