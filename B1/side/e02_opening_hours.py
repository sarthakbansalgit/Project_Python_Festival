                                                                   
                                                                       

opening = [
    {"day": "monday", "from": "14:00", "to": "18:00"},
    {"day": "wednesday", "from": "10:00", "to": "12:30"},
    {"day": "wednesday", "from": "14:00", "to": "19:00"},
    {"day": "saturday", "from": "10:00", "to": "17:00"},
]

                                                            
days = []
for slot in opening:
    if slot["day"] not in days:
        days.append(slot["day"])

                                                        
day = input("Which day? ").strip().lower()
while day not in days:
    print(f"Closed on {day!r}. Open on: {', '.join(days)}")
    day = input("Which day? ").strip().lower()

print(f"Open on {day}:")
for slot in opening:
    if slot["day"] == day:
        print(f"{slot['from']} - {slot['to']}")

                                                                   
                                                            
print("09:30" < "10:00", "9:30" < "10:00")
