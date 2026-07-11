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
cursor = connection.cursor()

#columns for each table
d_columns=["Id", "BIRTHDATE", "DEATHDATE", "SSN", "DRIVERS", "PASSPORT", "PREFIX", "FIRST", "MIDDLE", "LAST",
                 "SUFFIX", "MAIDEN", "MARITAL", "RACE", "ETHNICITY", "BIRTHPLACE", "ADDRESS", "CITY", "STATE", "COUNTY", "HEALTHCARE_EXPENSES",
                 "HEALTHCARE_COVERAGE", "INCOME"
                 ]
a_columns=["DESCRIPTION", "TYPE", "CATEGORY"]
c_columns=["DESCRIPTION"]
e_columns=["START", "STOP", "ENCOUNTERCLASS", "DESCRIPTION"]


def login(user):
    cursor.execute("SELECT password_hash from users WHERE username=%s"), (user,)
    hpassword=cursor.fetchone()

    return hpassword

def sign_up(first,last, user, password):
    password = password.encode("utf-8")
    hpassword = bcrypt.hashpw(password,bcrypt.gensalt())
    hpassword= hpassword.decode("utf-8")

    cursor.execute("INSERT INTO employees (first_name, last_name) VALUES (%s, %s)", (first, last))
    employee_id=cursor.lastrow_id
    cursor.execute("INSERT INTO users (employee_id, username, password_hash) VALUES (%s, %s)", (employee_id, user, hpassword))

    connection.commit()

    return "Your Account Has Been Created!"




def search_patient(fname, lname, option):

    cursor.execute("SELECT Id FROM patients WHERE FIRST LIKE %s AND LAST LIKE %s", (f"%{fname}%", f"%{lname}%"))
    patient_id = cursor.fetchone()
    if patient_id is None:
        return "Patient not found."
    # fetchone() returns a tuple like (Id,)
    patient_id = patient_id[0]

    if option == "Demographics":
        cursor.execute("SELECT * FROM patients WHERE Id=%s", (patient_id,))
        
        result=cursor.fetchone()

        columns=d_columns
        patient_info = dict(zip(columns, result))

        return patient_info

    elif option == "Allergies":
        cursor.execute("SELECT DESCRIPTION, TYPE, CATEGORY FROM allergies WHERE PATIENT=%s", (patient_id,))
        
        rows=cursor.fetchall() #fetch all bc there can be multiple allergies for a patient
        
        columns=a_columns
        
        allergies_info = [dict(zip(columns, row)) for row in rows]
        return allergies_info
    
    elif option == "Conditions":
        
        cursor.execute("SELECT DISTINCT DESCRIPTION FROM conditions WHERE PATIENT=%s", (patient_id,))
        
        rows=cursor.fetchall() #fetch all bc there can be multiple conditions for a patient
        
        columns=c_columns
        
        conditions_info = [dict(zip(columns, row)) for row in rows] #for row in rows bc each row needs to be zipped with columns to create a dictionary for each condition
        
        return conditions_info

    elif option == "Encounters":
        
        cursor.execute("SELECT START, STOP, ENCOUNTERCLASS, DESCRIPTION FROM encounters WHERE PATIENT=%s", (patient_id,))
        
        rows=cursor.fetchall() #fetch all bc there can be multiple encounters for a patient
        
        columns=e_columns
        
        encounters_info = [dict(zip(columns, row)) for row in rows] #for row in rows bc each row needs to be zipped with columns to create a dictionary for each encounter
        
        return encounters_info
    
    elif option == None:
        
        return "Invalid option."

def add_patient(data):

    columns = d_columns[1:]  # Exclude the "Id" column since it will be generated automatically

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

    cursor.execute("INSERT INTO allergies (Id) VALUES (%s)", (patient_id,))
    cursor.execute("INSERT INTO conditions (Id) VALUES (%s)", (patient_id,))
    cursor.execute("INSERT INTO encounters (Id) VALUES (%s)", (patient_id,))

    connection.commit()

    print (f"Patient added successfully with ID: {patient_id}")

    return patient_id

def find_patient(fname, lname):
    
    cursor.execute("SELECT Id FROM patients WHERE FIRST LIKE %s AND LAST LIKE %s", (f"%{fname}%", f"%{lname}%"))
    patient_id = cursor.fetchone()

    if patient_id is None:
        print("Patient not found.")
        return None

    return patient_id[0]  # Return the actual ID value, not the tuple

def add_info(patient_id, data):
    columns = d_columns  # Initialize columns variable




    values=[]  
        
    for column in columns:
        values.append(data.get(column))
   
    set_clause = ", ".join(f"{column} = %s" for column in columns)
        
    cursor.execute(f"UPDATE patients SET {set_clause} WHERE Id = %s", tuple(values) + (patient_id,))

    result=dict(zip(columns, values))
        
    connection.commit()
        
    return result
        


# cursor.execute runs queries 
# cursor.fetchall fetches results from queries 
#connection.commit() saves changes to the database
#.join() is used to join strings together
#tuples are needed when combining multiple values to be inserted into the database ex: patient_id and list of values
