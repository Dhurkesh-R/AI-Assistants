# from future import print_function
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import time
from dateutil import parser as date_parser
import speech_recognition as sr
import pyttsx3
import pytz  
import subprocess

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/calendar.events"]


MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said


def authenticate_google():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    return service

import datetime
from datetime import timezone

def get_events(day, service):
    try:
        date = datetime.datetime.combine(day, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
        utc = pytz.UTC
        date = date.astimezone(utc)
        end_date = end_date.astimezone(utc)

        print("Start Date:", date)  # Add this line to print the start date
        print("End Date:", end_date)  # Add this line to print the end date

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            speak("No upcoming events found.")

        else:
            speak(f"You have {len(events)} events on this day.")
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])
                start_time = str(start.split("T")[1].split('+')[0])
                if int(start_time.split(':')[0]) < 12:
                    start_time = start_time.split(':')[0]
                    start_time=start_time + "am"
                else:
                    start_time = str(int(start_time.split(':')[0])- 12) + start_time.split(':')[1]
                    start_time = start_time + "pm"

                speak(event['summary'] + "at" + start_time)

    except HttpError as error:
        print(f"An error occurred: {error}")

def get_date(text):
    print("Inside get_date() function")  # Check if the function is being called
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if day < today.day and month == -1 and day != -1:
        month = month + 1

    if day == -1 and month == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()  # Corrected to call the method
        diff = day_of_week - current_day_of_week

        if diff < 0:
            diff += 7
            if text.count("next") >= 1:
                diff += 7

        return today + datetime.timedelta(days=diff)  # Corrected to add days=diff instead of diff
    if month == -1 or day == -1:
        return None
    return datetime.date(month=month, day=day, year=year)

def add_event(service):
    speak("What are the event details?")
    event_details = get_audio()

    day, start_time, end_time, event_name = parse_time(event_details)
    if day is None or start_time is None or end_time is None or event_name is None:
        speak("Sorry, I couldn't understand the event details. Please try again.")
        return
    
    print("Parsed Date (before calling get_events):", day)  # Add this line to print the parsed date before calling get_events
    get_events(day, service)  # Call get_events function to check if the correct date is being passed

    event = {
        'summary': event_name,
        'start': {
            'dateTime': day.strftime('%Y-%m-%d') + 'T' + start_time.strftime('%H:%M:%S'),
            'timeZone': 'Asia/Singapore',
        },
        'end': {
            'dateTime': day.strftime('%Y-%m-%d') + 'T' + end_time.strftime('%H:%M:%S'),
            'timeZone': 'Asia/Singapore',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        speak("Event added to your calendar.")
    except Exception as e:
        print("An error occurred:", e)
        speak("Sorry, there was an error adding the event to your calendar.")


def parse_time(text):
    parts = text.strip().split(" at ")

    if len(parts) == 1:
        parts = text.strip().split("at")

    if len(parts) < 2:
        return None, None, None, None

    event_name = parts[0].strip()
    remaining_text = "at".join(parts[1:]).strip()

    parts = remaining_text.split(" on ")
    if len(parts) < 2:
        return None, None, None, None

    time_range = parts[0].strip()
    day_text = parts[1].strip()

    day = get_day_from_text(day_text)
    if day is None:
        return None, None, None, None

    start_time_text, end_time_text = time_range.split("to")
    start_time = parse_hour_minute(start_time_text.strip())
    end_time = parse_hour_minute(end_time_text.strip())

    if start_time is None or end_time is None:
        return None, None, None, None

    return day, start_time, end_time, event_name

def get_day_from_text(day_text):
    print("Inside get_date() function")  # Check if the function is being called
    day_text = day_text.lower()
    today = datetime.date.today()

    if day_text.count("today") > 0:
        return today
    
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in day_text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if day < today.day and month == -1 and day != -1:
        month = month + 1

    if day == -1 and month == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()  # Corrected to call the method
        diff = day_of_week - current_day_of_week

        if diff < 0:
            diff += 7
            if day_text.count("next") >= 1:
                diff += 7

        return today + datetime.timedelta(days=diff)  # Corrected to add days=diff instead of diff
    if month == -1 or day == -1:
        return None
def parse_hour_minute(time_text):
    parts = time_text.strip().split(":")
    hour = int(parts[0].strip())
    minute = int(parts[1].strip().split()[0])  # Remove any trailing text like 'a.m.' or 'p.m.'
    return datetime.datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)


def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(':', '-') + "-note.txt"

    with open(file_name, 'w') as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])

WAKE = "hey tony"
SLEEP = "bye tony"

service = authenticate_google()
print("Start")

while True:
    print("I am Listening...")
    text = get_audio()

    if text.lower() == SLEEP:
        speak("Goodbye!")
        break

    if text.lower() == WAKE:
        speak("Ready to go")
        print("I am Listening...")
        text = get_audio()

        CALENDAR_STRS = ["what do i have", "do i have plans","do i have any plans", "am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_events(date, service)
                else:
                    speak("I don't understand")

        NOTE_STRS = ["make a note", "write this down", "remember this", "type this"]
        for phrase in NOTE_STRS:
            if phrase in text.lower():
                speak("What would you like me to write down? ")
                write_down = get_audio()
                note(write_down)
                speak("I've made a note of that.")

        ADD_EVENT_STRS = ["add an event", "create an event", "schedule an event", "plan an event"]
        for phrase in ADD_EVENT_STRS:
            if phrase in text.lower():
                add_event(service)

