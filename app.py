from flask import Flask, request, render_template, session, redirect, url_for
import ehr

app = Flask(__name__)

@app.route("/login")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":

        patient_id = ehr.add_patient(request.form)
        return f"Success! ID: {patient_id}"
    #this is what is rendered when the user goes to the add route "GET" request
    return render_template("add_patient.html", columns=ehr.d_columns[1:])  # Exclude the "Id" column since it will be generated automatically

@app.route("/search", methods=["GET", "POST"])
def search():
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

    
    patient_id=None

    if request.method == "POST": #the add.html is a submission form and will perform these actions when the user submits the form
        stage=request.form.get("stage") #since we have multiple pages in the route, stage determines which page we are on find or update
        if stage == "find":
            fname= request.form.get("FIRST")
           
            lname= request.form.get("LAST")

            columns=ehr.d_columns
           
            patient_id=ehr.find_patient(fname,lname)


            if patient_id:

                #this is the stage==update page we redirect to after the form of add.html is submitted
                return render_template("add2.html", patient_id=patient_id,category=columns) 

        elif stage == "update":
            data=request.form
           
            patient_id= request.form.get("patient_id")
            
            patient_data=ehr.add_info(patient_id, data ) #this is the tablechoice that was passed from the add.html page to determine which table to add info too

            return render_template("addview.html", results=patient_data)
    
    return render_template("add.html") #the first page that is rendered when the user goes to the addinfo_patient route "GET" request


  

if __name__ == "__main__":
    app.run(debug=True)