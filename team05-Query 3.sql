SELECT dog_name FROM (SELECT Dogs.dog_name ,count(*) as max_trip 
					  FROM Taking_Dogs as tk JOIN Dogs on tk.dog_id=Dogs.dog_id 
					  GROUP BY Dogs.dog_name
					  HAVING max_trip<=0.5*(SELECT max(max_trip) FROM 
												(SELECT tk.dog_id, count(*) as max_trip 
												 FROM Taking_Dogs as tk JOIN Dogs on tk.dog_id=Dogs.dog_id
												 GROUP BY dog_id) as d)) as d;