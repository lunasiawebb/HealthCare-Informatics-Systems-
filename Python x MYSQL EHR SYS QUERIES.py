#Python x MYSQL 
from dotenv import load_dotenv
import os 
import uuid
import mysql.connector

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


def menu():
    while True:
        option=input("""Choose an option:
        1. View a patient 
        2. Add a patient
        3. Add information to a patient
        4. Exit
        """)
        if option == "1":
            view_patient()

        if option == "2":
            add_patient()
            
        if option == "3":
            add_info()
        
        if option == "4":
            print("Exiting the program.")
            break
        
        


def view_patient():
    option2=input("""Would you like to view this patient's 
    1. Demographics 
    2. Allergies 
    3. Conditions
    4. Encounters
    """)

    name=input("Enter the patient's name: ")

    cursor.execute("SELECT Id FROM patients WHERE FIRST LIKE %s", (f"%{name}%",))
    patient_id = cursor.fetchone()[0]

    if option2 == "1":
        cursor.execute("SELECT * FROM patients WHERE Id=%s", (patient_id,))
        print(cursor.fetchall())
    elif option2 == "2":
        cursor.execute("SELECT DESCRIPTION, TYPE, CATEGORY FROM allergies WHERE PATIENT=%s", (patient_id,))
        print(cursor.fetchall())
    elif option2 == "3":
        cursor.execute("SELECT DISTINCT DESCRIPTION FROM conditions WHERE PATIENT=%s", (patient_id,))
        print(cursor.fetchall())
    elif option2 == "4":
        cursor.execute("SELECT START, STOP, ENCOUNTERCLASS, DESCRIPTION FROM encounters WHERE PATIENT=%s", (patient_id,))
        print(cursor.fetchall())
    else:
        print("Invalid option. Please try again.")


def add_patient():
    columns = ["BIRTHDATE", "FIRST", "MIDDLE", "LAST", "GENDER", 
               "RACE", "BIRTHPLACE", "ADDRESS", "CITY", "STATE", "COUNTY"]
    patient_id = str(uuid.uuid4())
    values = []

    for column in columns:
        value= input(f"Enter {column}: ")
        values.append(value)

    cursor.execute(f"INSERT INTO patients (Id, {', '.join(columns)}) VALUES ({', '.join(['%s'] * (len(columns) + 1))})", (patient_id,) + tuple(values))
    print("Patient added successfully.")
    print(f"Patient ID: {patient_id}")

    connection.commit() 

def add_info():
    option=input("Provide the name of your patient: ")
    
    cursor.execute("SELECT Id FROM patients WHERE FIRST LIKE %s", (f"%{option}%",))
    result = cursor.fetchone()

    if result is None:
        print("Patient not found.")
    
    patient_id = result[0]

    table=input("Provide the directory where you would like to add information)" \
    "1. Demographics::" \
    "2. Allergies:" \
    "3. Conditions:" \
    "4. Encounters:")
    if table not in ["1", "2", "3", "4"]:
        print("Invalid option.")
        

    if table == "1":
        columns=["DEATHDATE", "SSN", "DRIVERS", "PASSPORT", "PREFIX", "SUFFIX", "MAIDEN", 
                 "MARITAL", "ETHNICITY", "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE", "INCOME"]
        values=[]  
        for column in columns:
            value=input(f"Enter {column} or leave blank: ")
            values.append(value) 
   
        set_clause = ", ".join(f"{column} = %s" for column in columns)
        
        cursor.execute(f"UPDATE patients SET {set_clause} WHERE Id = %s", tuple(values) + (patient_id,))
        
        connection.commit()
        print("Patient updated successfully.")
        

menu()


# cursor.execute runs queries 
# cursor.fetchall fetches results from queries 
#connection.commit() saves changes to the database
#.join() is used to join strings together
#tuples are needed when combining multiple values to be inserted into the database ex: patient_id and list of values
