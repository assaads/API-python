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

    if response.status_code == 200:
        data = json.loads(response.text)
        if isinstance(data, dict) and 'partners' in data:
            data = data['partners']

        # Map the data to User objects
        users = [User(item['firstName'], item['lastName'], item['email'], item['country'], item['availableDates']) for item in data]

        return users
    else:
        return None


def group_users_by_coutry(users):
    # Group users by country
    users_by_country = {}
    for user in users:
        if user.country not in users_by_country:
            users_by_country[user.country] = []
        users_by_country[user.country].append(user)
    
    return users_by_country

def get_max_users_on_consecutive_dates(users_by_country):
    final_result = {'countries': []}

    for country, users in users_by_country.items():
        result = process_country(country, users)
        final_result['countries'].append(result)

    return final_result

def process_country(country, users):
    # Counter object to count the number of users available on each date
    date_counts = Counter()

    for user in users:
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in user.availableDates]
        for date in dates:
            date_counts[date] += 1

    sorted_dates = sorted(date_counts.items())

    max_count = 0
    max_date = None

    for i in range(len(sorted_dates) - 1):
        print(max_count)
        if sorted_dates[i][1] + sorted_dates[i+1][1] > (max_count if max_count else 0):
            max_count = sorted_dates[i][1] + sorted_dates[i+1][1]
            max_date = sorted_dates[i][0]

    attendees = [user.email for user in users if max_date.strftime('%Y-%m-%d') in user.availableDates or (max_date + timedelta(days=1)).strftime('%Y-%m-%d') in user.availableDates] if max_date else []

    # Add each country's data to the list
    country_data = {
        'attendeeCount': len(attendees),
        'attendees': attendees,
        'name': country,
        'startDate': max_date.strftime('%Y-%m-%d') if attendees else None
    }

    return country_data

# Main code

url = 'https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=c6beb3943b6481af2f99c62b9691'
users = get_api_data(url)
users_by_coutry = group_users_by_coutry(users)

result = get_max_users_on_consecutive_dates(users_by_coutry)

result_json = json.dumps(result, indent=2)

post_url = 'https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=c6beb3943b6481af2f99c62b9691'

response = requests.post(post_url, data=result_json)

if response.status_code == 200:
    print("Response from POST request:")
    print(response.text)
else:
    print(f"Failed to send POST request. Status code: {response.text}")