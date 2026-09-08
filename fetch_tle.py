import requests                             

url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"  # Defining the web address (using ISS as an example here)

response = requests.get(url)                 

with open('data/iss.txt', 'w') as file:      
    file.write(response.text)                