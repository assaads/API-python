import json
import requests
from collections import Counter
from datetime import datetime, timedelta

class User:
    def __init__(self, firstName, lastName, email, country, availableDates):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.country = country
        self.availableDates = availableDates

def get_api_data(url):
    # Send a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Deserialize the JSON array
        data = json.loads(response.text)
        
        # Check if data is a dictionary and contains a key for the array
        if isinstance(data, dict) and 'partners' in data:
            data = data['partners']
        
        # Map the data to User objects
        users = [User(item['firstName'], item['lastName'], item['email'], item['country'], item['availableDates']) for item in data]

         # Group users by country
        users_by_country = {}
        for user in users:
            if user.country not in users_by_country:
                users_by_country[user.country] = []
            users_by_country[user.country].append(user)
        
        return users_by_country
    else:
        return None

def get_max_users_on_consecutive_dates(users_by_country):
    countries = []

    for country, users in users_by_country.items():
        # Create a Counter object to count the number of users available on each date
        date_counts = Counter()

        for user in users:
            # Convert the available dates from strings to datetime objects
            dates = [datetime.strptime(date, '%Y-%m-%d') for date in user.availableDates]

            # Increment the count for each date and the next day
            for date in dates:
                date_counts[date] += 1
                date_counts[date + timedelta(days=1)] += 1

        # Sort the dates
        sorted_dates = sorted(date_counts.items())

        # Initialize the max count and max date
        max_count = max_date = None

        # Iterate over the sorted dates
        for i in range(len(sorted_dates) - 1):
            # Check if the current date and the next date have the same count
            if sorted_dates[i][1] == sorted_dates[i+1][1]:
                # Check if this is the max count so far
                if max_count is None or sorted_dates[i][1] > max_count:
                    max_count = sorted_dates[i][1]
                    max_date = sorted_dates[i][0]

        # Find the attendees who are available on the max_date and the next day
        attendees = [user.email for user in users if max_date.strftime('%Y-%m-%d') in user.availableDates and (max_date + timedelta(days=1)).strftime('%Y-%m-%d') in user.availableDates] if max_date else []

        # Add the country data to the list
        countries.append({
            'attendeeCount': len(attendees),
            'attendees': attendees,
            'name': country,
            'startDate': max_date.strftime('%Y-%m-%d') if attendees else None
        })

    return {'countries': countries}




# Replace 'your_api_url' with the actual API URL
url = 'https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=c6beb3943b6481af2f99c62b9691'
users = get_api_data(url)

# if users is not None:
#     for user in users:
#         print(f"Name: {user.firstName} {user.lastName}, Email: {user.email}, Country: {user.country}, Available Dates: {', '.join(user.availableDates)}")
# else:
#     print("Failed to retrieve data.")

result = get_max_users_on_consecutive_dates(users)

# Convert the result to a JSON string
result_json = json.dumps(result, indent=2)

print(result_json)

# Replace 'your_post_api_url' with the actual POST API URL
post_url = 'https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=c6beb3943b6481af2f99c62b9691'

# Send a POST request
response = requests.post(post_url, data=result_json)

# Check if the request was successful
if response.status_code == 200:
    print("Response from POST request:")
    print(response.text)
else:
    print(f"Failed to send POST request. Status code: {response.text}")
