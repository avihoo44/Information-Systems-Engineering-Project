SELECT Person.p_name as Dog_Owner_Name, COUNT(DISTINCT Day_of_Work) AS Number_Of_Days, SUM(day_price) AS Total_Payment
FROM Has_Dogs AS hd LEFT JOIN Person on Person.email=hd.email
					LEFT JOIN Taking_Dogs AS td ON hd.Dog_ID = td.Dog_ID
					LEFT JOIN Dog_Walker ON Dog_Walker.email=td.email
WHERE Person.city = "Tel Aviv" OR Person.city = "Haifa"
GROUP BY Dog_Owner_Name, Person.email;