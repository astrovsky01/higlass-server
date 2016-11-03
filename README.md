# higlass-server
TO INSTALL & RUN:
1) clone repo
2) cd /higlass-server/api
3) sudo pip install --upgrade -r requirements.txt
4) resolve personal dependency issues that pip can't
5) ensure access to port 8000
6) python run_tornado.py 

To access the API interactively, please visit http://54.70.83.188:8000/


To upload a new cooler file, format a POST request according to the interactive specification at http://54.70.83.188:8000/coolers/


To generate multires cooler files in the db for a dataset for which metadata has been uploaded to the database via a POST request visit http://54.70.83.188:8000/coolers/x/generate_tiles replacing x with cooler object id from coolers table


To view info about a specific cooler visit http://54.70.83.188:8000/coolers/x replacing x with cooler object id from coolers table


To view tileset info in a specific multires cooler view http://54.70.83.188:8000/coolers/x/tileset_info replacing x with cooler object id from coolers table


To retrieve a tile visit http://54.70.83.188:8000/coolers/t/tiles/?data=/x.y.z replacing t with cooler object id from coolers table, x&y with coordinates, and z with zoom level. 


To view users table (if admin auth provided) visit http://54.70.83.188:8000/users/


To view more detailed schema visit http://54.70.83.188:8000/schema


To administer visit http://54.70.83.188:8000/admin 
 

Test Accounts:
u Root: p higlassdbmi
u test: p higlassdbmi

Root account will show all data in the coolers table while test will only show public tables + tables owned by the user test. The API can be accessed without logging in for datasets that have been uploaded as "public" (boolean included in the POST request).  

