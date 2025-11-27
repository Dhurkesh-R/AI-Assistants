import datetime
def get_day_from_text(day_text):
    today = datetime.date.today()
    current_day_of_week = today.weekday()
    
    print("Day Text:", day_text)  # Print day_text to verify the input
    
    diff = 0  # Initialize diff to 0

    if "mon" in day_text:
        diff = 0 - current_day_of_week
    elif "tue" in day_text:
        diff = 1 - current_day_of_week
    elif "wed" in day_text:
        diff = 2 - current_day_of_week
    elif "thu" in day_text:
        diff = 3 - current_day_of_week
    elif "fri" in day_text:
        diff = 4 - current_day_of_week
    elif "sat" in day_text:
        diff = 5 - current_day_of_week
    elif "sun" in day_text:
        diff = 6 - current_day_of_week

    if diff < 0:
        diff += 7

    print("Diff:", diff)  # Print diff to verify the calculation

    return today + datetime.timedelta(days=diff)

# Test the function with sample inputs
print(get_day_from_text("Monday"))
print(get_day_from_text("Tuesday"))
print(get_day_from_text("Wednesday"))
print(get_day_from_text("Thursday"))
print(get_day_from_text("Friday"))
print(get_day_from_text("Saturday"))
print(get_day_from_text("Sunday"))
