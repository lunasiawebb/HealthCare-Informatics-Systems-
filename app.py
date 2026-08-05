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
            #audit log
            employee_id=None
            action="LOGIN FAILED"
            description="user login attempt failed"
            table_name="users"
            patient_id=None
            ehr.auditlog(employee_id,patient_id,action,table_name,description)


            return render_template("login.html" , error="Invalid user or password")
        truepwd=userinfo["password_hash"]
        truepwd=truepwd.encode("utf-8")
        pwrd = pwrd.encode("utf-8")
        if user and bcrypt.checkpw(pwrd, truepwd):
            print("You have logged in")
            
            session["employee_id"]=userinfo["employee_id"]
            session["user"]= userinfo["username"]
            session["role"]=userinfo["role"]
            
            #audit log
            employee_id=session["employee_id"]
            action="LOGIN SUCCESS"
            description="user login attempt"
            patient_id=None
            table_name="users"
            ehr.auditlog(employee_id,patient_id,action,table_name,description)



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
    
    return render_template("menu.html", role=session["role"])

@app.route("/add", methods=["GET", "POST"])
def add():
    if "employee_id" not in session:
        return redirect("/login")
    if session["role"] != "Doctor":
        return "Access Denied", 403
    if request.method == "POST":
        #audit log
        patient_id = ehr.add_patient(request.form) 
        employee_id=session["employee_id"]
        action="CREATE"
        description="User created a patient record"
        table_name="patients"
        ehr.auditlog(employee_id,patient_id,action,table_name,description)
        success=f"Success! ID: {patient_id}"
        return render_template("add_patient.html", success=success)
    #this is what is rendered when the user goes to the add route "GET" request
    return render_template("add_patient.html", columns=ehr.demographics[1:])  # Exclude the "Id" column since it will be generated automatically

@app.route("/search", methods=["GET", "POST"])
def search():
    if "employee_id" not in session:
        return redirect("/login")
    if request.method == "POST": #if we are sending data back to backend 
        stage = request.form.get("stage")
        if stage == "find patient":
            fname = request.form.get("FIRST") #request submission of FIRST
            lname = request.form.get("LAST") #Requests Submission in LAST
            option = request.form.get("TYPE")

            if not fname or not lname:
                return render_template(
                "search_patient.html",error="Input a valid name.", stage="find patient")
       
            patient_data = ehr.search_patient(fname, lname, option) #runs the search_patient method and saves the return of the method
            patient_id= ehr.find_patient(fname, lname)

            if patient_id is None:
                return render_template(
                "search_patient.html",error="Patient not found.", stage="find patient")
        
            #auditlogging 
            employee_id=session["employee_id"]
            table_name=option
            description="user viewed patient data"
            action="VIEW"
            ehr.auditlog(employee_id, patient_id, action, table_name, description)


            return render_template("search_patient.html", stage="show results", option=option,results=patient_data) #return results from above function

    return render_template("search_patient.html", stage="find patient")

@app.route("/update", methods=["GET", "POST"])
def update_patient():
    if "employee_id" not in session:
        return redirect("/login")
    
    patient_id=None

    if request.method == "POST": #the add.html is a submission form and will perform these actions when the user submits the form
        stage=request.form.get("stage") #since we have multiple pages in the route, stage determines which page we are on find or update
        if stage == "find patient":
            fname= request.form.get("FIRST")
           
            lname= request.form.get("LAST")

            category= request.form.get("category")

            table = ehr.get_tablecolumns(category)
           
            patient_id=ehr.find_patient(fname,lname)


            if patient_id:

                #this is the stage==update page we redirect to after the form of add.html is submitted
                return render_template("updatefind.html", stage="update patient", category=category, patient_id=patient_id, table=table) 

        elif stage == "update patient":
            data = {}

            category=request.form.get("category")

            table=ehr.get_tablecolumns(category)

            for column in table:
                data[column] = request.form.get(column)

            patient_id= request.form.get("patient_id")

            patient_data=ehr.add_info(patient_id, data, category, table)

            #auditlogging
            employee_id=session["employee_id"]
            action="UPDATE"
            table_name=category
            description="user updated patient information"
            ehr.auditlog(employee_id,patient_id,action,table_name,description)

            print("This is the id", patient_id)
            print("this is the data", data)
            print("this is the category", category)
            print("this is the table",table)
            
            patient_data=ehr.add_info(patient_id, data, category, table)

            
            return render_template("updatefind.html", stage="view changes", results=patient_data)
    
    return render_template("updatefind.html", stage="find patient") #the first page that is rendered when the user goes to the update_patient route "GET" request


@app.route("/lab_results" , methods=["GET", "POST"])
def lab_results():
    if "employee_id" not in session:
        return redirect("/login")
    lablist=ehr.lab_results_patient(patient_id=None, doctor_last=None, type=None)
    if request.method =="POST":
        fname = request.form.get("FIRST")
        lname = request.form.get("LAST")
        doctor_last = request.form.get("DOCTOR_LAST")
        type = request.form.get("TYPE")
        if fname and lname:
            patient_id = ehr.find_patient(fname, lname)
        else:
            patient_id = None
        lablist = ehr.lab_results_patient(patient_id=patient_id, doctor_last=doctor_last, type=type)
        return render_template("lab_results.html", results=lablist) 
    return render_template("lab_results.html", results=lablist) 
@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()

    return redirect("/login")
  

if __name__ == "__main__":
    app.run(debug=True)