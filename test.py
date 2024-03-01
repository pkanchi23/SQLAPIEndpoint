import requests
import json

# Define the URL of the API endpoint
url = 'https://sqlapiendpoint.onrender.com/run-query'

# Define the SQL query you want to send (change this to your actual SQL query)
sql_query = 'SELECT * FROM Orders LIMIT 10'

# Adjust the data payload to match the expected structure
payload = {
    "data": {
        "Natural Language Question": "", 
        "Returned SQL": sql_query,
        "Feedback": "",
        "Program Ran": "",
        "Columns": "", 
        "database_name": "", 
        "other": "" 
    }
}

# Convert the payload dictionary to a JSON string
json_payload = json.dumps(payload)

# Set the appropriate headers for a JSON POST request
headers = {
    'Content-Type': 'application/json'
}

# Send the POST request with the updated payload structure
response = requests.post(url, data=json_payload, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Print the response data
    print("Response Data:", response.json())
else:
    # Print an error if something went wrong
    print(f"Error {response.status_code}: {response.text}")
