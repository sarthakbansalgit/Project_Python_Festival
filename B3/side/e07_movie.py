                                                                          
                                                               

from dataclasses import dataclass
from datetime import datetime, timedelta


                                                                         
                                                                        
                                                                      
class Screening:
    def __init__(self, title: str, start: datetime, minutes: int) -> None:
        if minutes < 1:
            raise ValueError(f"{title}: a film lasts at least one minute.")
        self.title = title                                       
        self.start = start
        self.minutes = minutes

    @property
    def end(self) -> datetime:
        """Read like an attribute (screening.end), computed each time."""
        return self.start + timedelta(minutes=self.minutes)

    def is_running(self, at: datetime) -> bool:
        return self.start <= at < self.end

    def to_view(self) -> dict:
        """What an API would send: plain values, computed ones included."""
        return {
            "title": self.title,
            "start": self.start.isoformat(timespec="minutes"),
            "end": self.end.isoformat(timespec="minutes"),
        }


late = Screening("Night of the Living Dad", datetime(2027, 3, 5, 23, 10), 95)
print(late.end)                       
print(late.is_running(datetime(2027, 3, 6, 0, 30)))        
print(late.to_view())

                                                        
row = {"title": "Brunch Club", "start": "2027-03-06T11:00", "minutes": 80}
brunch = Screening(row["title"], datetime.fromisoformat(row["start"]), row["minutes"])
print(brunch.end.strftime("%H:%M"))


                                                                  
@dataclass
class Cinema:
    name: str
    seats: int

    def __post_init__(self) -> None:                                     
        self.name = self.name.strip()
        if self.seats < 1:
            raise ValueError(f"{self.name} needs at least one seat.")


print(Cinema("  Le Rex ", 300))                                    
print(Cinema("Le Rex", 300) == Cinema("Le Rex", 300))        
