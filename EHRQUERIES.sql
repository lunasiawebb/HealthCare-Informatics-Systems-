-- Select all patients and their allergies
SELECT *
FROM patients AS p 
JOIN allergies AS al
	ON al.PATIENT=p.Id
;

-- Find all conditions
SELECT CODE, DESCRIPTION
FROM conditions 
GROUP BY CODE, DESCRIPTION
;

-- Find what conditions are common
SELECT CODE,DESCRIPTION, COUNT(*)
FROM conditions
GROUP BY CODE,DESCRIPTION
ORDER BY COUNT(*) DESC;

-- group conditions by person, finding

SELECT DESCRIPTION,

	CASE 
		WHEN DESCRIPTION LIKE "%finding%" THEN 'Finding'
		WHEN DESCRIPTION LIKE "%disorder%" THEN 'Disorder'
		WHEN DESCRIPTION LIKE "%situation%" THEN 'Situation'
    ELSE 'Other'
    
    END AS category
    
FROM conditions
;

-- find the condition of all patients

SELECT FIRST, LAST, description
FROM patients
LEFT JOIN conditions
	ON patients.Id=conditions.PATIENT
;

-- Find all the conditions for a particular patient (Tashia)

SELECT FIRST, LAST, DESCRIPTION
FROM patients 
LEFT JOIN conditions
 ON patients.Id=conditions.PATIENT
WHERE FIRST LIKE "Tashia%"
;

-- Find all condiditions pertaining to  asthma or diabetes

SELECT DESCRIPTION
FROM conditions
WHERE DESCRIPTION LIKE '%asthma%'

UNION

SELECT DESCRIPTION
FROM conditions
WHERE DESCRIPTION LIKE '%diabetes%'
;

-- Find immunizations for patients conditions

SELECT FIRST, LAST, 
c.DESCRIPTION AS Conditions, 
im.DATE AS Immunization_Date, 
im.DESCRIPTION AS Immunization
FROM patients AS p
INNER JOIN conditions AS c
	ON p.Id=c.PATIENT
INNER JOIN immunizations AS im
	ON c.PATIENT=im.PATIENT
;

-- find patients with severe allergies and recent encounters
SELECT DISTINCT 
	allergies.START, 
	ENCOUNTERCLASS, 
	FIRST, 
	LAST, 
	allergies.DESCRIPTION, 
	SEVERITY1
FROM patients
INNER JOIN allergies
	ON patients.Id=allergies.patient
INNER JOIN encounters 
	ON encounters.patient = allergies.patient
WHERE SEVERITY1 LIKE 'Severe'
ORDER BY allergies.START DESC
;

-- UPDATE TABLE Clean Patient Names
UPDATE patients
SET FIRST = REGEXP_REPLACE(FIRST, '[0-9]', '') 
WHERE Id IS NOT NULL 
AND FIRST REGEXP '[0-9]';

UPDATE patients
SET LAST = REGEXP_REPLACE(LAST, '[0-9]', '') 
WHERE Id IS NOT NULL 
AND LAST REGEXP '[0-9]';

SELECT FIRST, LAST
FROM patients;

-- Determine if an encounter is recent

SELECT PATIENT, START,
CASE
	WHEN START > '2025-01-01' THEN 'Recent'
END AS ENCOUNTERTIME
FROM encounters;

-- Identify the severity of allergy1

SELECT DESCRIPTION1,
       CASE
           WHEN SEVERITY1 = 'Severe' THEN 'High Risk'
           ELSE 'Standard Risk'
       END AS Risk_Level
FROM allergies;

SELECT FIRST, LAST, INCOME,
	(SELECT AVG(INCOME)
	FROM patients)
FROM patients;
 
 -- WINDOW FUNC
SELECT FIRST, LAST, GENDER, INCOME, HEALTHCARE_EXPENSES,
AVG(INCOME) OVER(PARTITION BY GENDER), AVG(HEALTHCARE_EXPENSES) OVER(PARTITION BY GENDER)
FROM patients;

SELECT GENDER,
AVG(INCOME), AVG(HEALTHCARE_EXPENSES)
FROM patients
GROUP BY GENDER;

SELECT FIRST, LAST, GENDER, INCOME, HEALTHCARE_EXPENSES,
	CASE 
		WHEN INCOME > HEALTHCARE_EXPENSES THEN 'NO DEBT'
		ELSE 'DEBT'
	END AS PAY_LVL
FROM patients;

-- CTE'S

WITH DEBT AS(

SELECT FIRST, LAST, GENDER, INCOME, HEALTHCARE_EXPENSES, HEALTHCARE_COVERAGE,
	CASE 
		WHEN INCOME < HEALTHCARE_EXPENSES THEN (HEALTHCARE_EXPENSES - INCOME) - HEALTHCARE_COVERAGE 
        ELSE 0
	END AS TOTAL_DEBT

FROM patients
)

SELECT *
FROM DEBT 
ORDER BY TOTAL_DEBT DESC

;

-- TEMP TABLE
DROP TEMPORARY TABLE IF EXISTS DEBT; 
CREATE TEMPORARY TABLE DEBT AS
SELECT FIRST, LAST, GENDER, INCOME, HEALTHCARE_EXPENSES,
       HEALTHCARE_COVERAGE,
       GREATEST(
               (HEALTHCARE_EXPENSES - INCOME) - HEALTHCARE_COVERAGE,
               0
           ) AS TOTAL_DEBT
FROM patients;

SELECT * 
FROM DEBT;

SELECT GENDER, AVG(TOTAL_DEBT)
FROM DEBT
GROUP BY GENDER;

-- THIS YEARS ENCOUNTERS

CREATE PROCEDURE recent_encounter()
SELECT START, PATIENT, REASONDESCRIPTION
FROM encounters 
WHERE START LIKE '2026%';

CALL recent_encounter();

DELIMITER $$
CREATE PROCEDURE Cond_All()
BEGIN
	SELECT DESCRIPTION 
	FROM allergies 
	WHERE CATEGORY = 'food'; 
	SELECT DESCRIPTION 
	FROM conditions
	WHERE DESCRIPTION LIKE '%finding%';
END $$
DELIMITER ;

CALL Cond_All();


-- EHR USERS
DROP TABLE IF EXISTS users;
 CREATE TEMPORARY TABLE users (
 user_id INT AUTO_INCREMENT PRIMARY KEY, 
 username VARCHAR(50),
 p_hash VARCHAR(50),
 role VARCHAR(20)
 );
 
 INSERT INTO users (username, p_hash, role)
 VALUES ('kellym21' , 'EFF23H82' , 'Nurse'),
 ('rossl5', 'GSO65H88', 'Administrator')
 ;
 
 SELECT * FROM users;

DROP PROCEDURE IF EXISTS CondFIND;
DELIMITER $$
CREATE PROCEDURE CondFIND(type VARCHAR(20))
BEGIN
	SELECT DISTINCT DESCRIPTION 
	FROM conditions
	WHERE DESCRIPTION LIKE CONCAT('%', type, '%');
END $$
DELIMITER ;

CALL CondFIND('ache');

SELECT * FROM 
encounters
INNER JOIN patients
	ON encounters.id=patients.id
WHERE patients.FIRST = 'Loren';

SELECT
	*
FROM conditions 
INNER JOIN patients 
    ON patients.Id = conditions.PATIENT
WHERE patients.FIRST = 'Loren';

SELECT * FROM patients WHERE FIRST LIKE 'Kiany';
    
    
SHOW CREATE TABLE patients;

DESCRIBE patients;

SELECT FIRST, LAST, DESCRIPTION, TYPE, CATEGORY
FROM patients AS p
JOIN allergies AS a
	ON p.Id=a.PATIENT;
