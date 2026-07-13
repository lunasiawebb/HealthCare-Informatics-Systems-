#Python x MYSQL 
from click import option
from dotenv import load_dotenv
import os 
import uuid
import mysql.connector
import bcrypt
load_dotenv()

connection = mysql.connector.connect (
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
if connection.is_connected():
    print("Connected to MySQL database")
cursor = connection.cursor(dictionary=True)

#columns for each table
demographics=["Id", "BIRTHDATE", "DEATHDATE", "SSN", "DRIVERS", "PASSPORT", "PREFIX", "FIRST", "MIDDLE", "LAST",
                 "SUFFIX", "MAIDEN", "MARITAL", "RACE", "ETHNICITY", "BIRTHPLACE", "ADDRESS", "CITY", "STATE", "COUNTY", "HEALTHCARE_EXPENSES",
                 "HEALTHCARE_COVERAGE", "INCOME"
                 ]
allergies=["DESCRIPTION", "TYPE", "CATEGORY"]
conditions=["DESCRIPTION"]
encounters=["START", "STOP", "ENCOUNTERCLASS", "DESCRIPTION"]

def get_tablecolumns(category):
    if category=="patients":
        return demographics
    elif category=="allergies":
        return allergies
    elif category=="conditions":
        return conditions
    elif category=="encounters":
        return encounters
    else:
        return "this table does not exist"

def login(user):
    cursor.execute("SELECT employee_id, username, password_hash, role FROM users WHERE username=%s", (user,) )

    userinfo=cursor.fetchone()

    return userinfo

def sign_up(first,last, user, password):
    cursor.execute ("SELECT username FROM users WHERE username = %s", (user,))
    checkuser= cursor.fetchone()

    if checkuser:
        return "Username already exists"
   
    password = password.encode("utf-8")
    hpassword = bcrypt.hashpw(password,bcrypt.gensalt())
    hpassword= hpassword.decode("utf-8")

    cursor.execute("INSERT INTO employees (first_name, last_name) VALUES (%s, %s)", (first, last))
    employee_id=cursor.lastrowid
    cursor.execute("INSERT INTO users (employee_id, username, password_hash) VALUES (%s, %s, %s)", (employee_id, user, hpassword))

    connection.commit()

    return "Your Account Has Been Created!"

def search_patient(fname, lname, option):

    cursor.execute("SELECT Id FROM patients WHERE FIRST LIKE %s AND LAST LIKE %s", (f"%{fname}%", f"%{lname}%"))
    patient_id = cursor.fetchone()
    if patient_id is None:
        return "Patient not found."
    # fetchone() returns a tuple like (Id,)
    patient_id = patient_id["Id"]

    if option == "Demographics":
        cursor.execute("SELECT * FROM patients WHERE Id=%s", (patient_id,))
        
        return cursor.fetchone()


    elif option == "Allergies":
        cursor.execute("SELECT DESCRIPTION, TYPE, CATEGORY FROM allergies WHERE PATIENT=%s", (patient_id,))
        
        return cursor.fetchall()
    
    elif option == "Conditions":
        
        cursor.execute("SELECT DISTINCT DESCRIPTION FROM conditions WHERE PATIENT=%s", (patient_id,))
        
        return cursor.fetchall() #fetch all bc there can be multiple conditions for a patient

    elif option == "Encounters":
        
        cursor.execute("SELECT START, STOP, ENCOUNTERCLASS, DESCRIPTION FROM encounters WHERE PATIENT=%s", (patient_id,))
        
        return cursor.fetchall() #fetch all bc there can be multiple encounters for a patient
    
    elif option == None:
        
        return "Invalid option."

def add_patient(data):

    columns = demographics[1:]  

    patient_id = str(uuid.uuid4())

    values = []

    for column in columns:
        values.append(data.get(column))  # SAFE VERSION

    print("VALUES BEING INSERTED:")
    print(patient_id)
    print(values)

    cursor.execute(
        f"""
        INSERT INTO patients (Id, {', '.join(columns)})
        VALUES ({', '.join(['%s'] * (len(columns) + 1))})
        """,
        (patient_id,) + tuple(values)
    )


    connection.commit()

    print (f"Patient added successfully with ID: {patient_id}")

    return patient_id

def find_patient(fname, lname):
    
    cursor.execute("SELECT Id FROM patients WHERE FIRST LIKE %s AND LAST LIKE %s", (f"%{fname}%", f"%{lname}%"))
    patient_id = cursor.fetchone()

    if patient_id is None:
        print("Patient not found.")
        return None

    return patient_id["Id"]  # Return the actual ID value, not the tuple

def add_info(patient_id, data, category, table):
   
    values=[]  
        
    for column in table:
        values.append(data.get(column))
   
    set_clause = ", ".join(f"{column} = %s" for column in table)
    columns = ", ".join(table)
    placeholders = ", ".join(["%s"] * (len(table) + 1))


    if category == "patients":
        cursor.execute(f"UPDATE {category} SET {set_clause} WHERE Id = %s", tuple(values) + (patient_id,))
    else:
        cursor.execute(f"INSERT INTO {category} (PATIENT, {columns}) VALUES ({placeholders})" ,(patient_id,) + tuple(values))
    
    result=dict(zip(table, values))
        
    connection.commit()
        
    return result
        


# cursor.execute runs queries 
# cursor.fetchall fetches results from queries 
#connection.commit() saves changes to the database
#.join() is used to join strings together
#tuples are needed when combining multiple values to be inserted into the database ex: patient_id and list of values
