import requests
import json

# Define the URL of the API endpoint
url = 'https://sqlapiendpoint.onrender.com/run-query'

# Define the SQL query you want to send (change this to your actual SQL query)
sql_query = 'SELECT * FROM Orders LIMIT 10'

# Create the data payload as a dictionary
data = {
    'Returned SQL': sql_query
}

# Convert the dictionary to a JSON string
json_data = json.dumps(data)

# Set the appropriate headers for a JSON POST request
headers = {
    'Content-Type': 'application/json'
}

# Send the POST request
response = requests.post(url, data=json_data, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Print the response data
    print("Response Data:", response.json())
else:
    # Print an error if something went wrong
    print(f"Error {response.status_code}: {response.text}")
