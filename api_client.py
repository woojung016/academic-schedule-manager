import requests
from datetime import datetime

def fetch_public_holidays(year):
    url = f"https://nagerholidays.com/api/v4/Holidays/KR/{year}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    holidays = []
    for holiday in data:
        if "Public" in holiday.get("holidayTypes", []):
            holidays.append({
                "date": holiday["date"],
                "name": holiday["name"]
            })

    return holidays


if __name__ == "__main__":
    year = datetime.now().year
    holidays = fetch_public_holidays(year)

    for holiday in holidays:
        print(holiday["date"], holiday["name"])
