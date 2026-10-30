                                                                          
                                                                        

from e06_temperatures import to_fahrenheit, warmest

readings = {"Brest": 14.5, "Lille": 11.0, "Nice": 22.0}

for city, celsius in readings.items():
    print(f"{city}: {celsius} °C = {to_fahrenheit(celsius):.1f} °F")
print(f"Warmest: {warmest(readings)}")
