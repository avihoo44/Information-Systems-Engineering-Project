SELECT Dog_Type, AVG(Day_Price) as Average_Day_Price, COUNT(email) as Num_Of_Active_Dogwalkers
FROM (SELECT DISTINCT DW.email, S.Dog_Type, DW.Day_Price
      FROM Taking_Dogs as TD LEFT JOIN Dogs ON TD.Dog_ID = Dogs.Dog_ID
                       LEFT JOIN Species as S ON Dogs.Type_ID = S.Type_ID
                       LEFT JOIN Dog_Walker as DW ON TD.email = DW.email) as Data_Table
GROUP BY Dog_Type;