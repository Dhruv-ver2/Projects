def greet(hour,minute):
    if 0 <= hour <= 4:
        return "Very Good Morning"
    elif 5 <= hour <= 11:
        return "Good Morning"
    elif hour == 12:
        if minute <= 2:
            return "Good Noon"
        else:
            return "Good afternoon"
    elif 13 <= hour <= 16:
       return "Good afternoon"
    elif 17 <= hour <= 22:
        return "Good Evening"
    else:
        return "Good night"


import pyttsx3
import random
from datetime import datetime as dt

suffix=["Boss","Sir","Master"]

#____________Timing
now = dt.now()
hour = now.hour
minute = now.minute

#____________Speaker engine
engine = pyttsx3.init()
engine.setProperty('rate', 165)
engine.setProperty('volume', 0.9)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)
engine.say(f"{greet(hour,minute)} {random.choice(suffix)}")

engine.runAndWait()
