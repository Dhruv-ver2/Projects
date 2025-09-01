def get_date(event):
    return event.date

def current_users(eventss):
    eventss.sort(key=get_date)
    machines=dict()

    for event in eventss:
        if event.machine not in machines:
            machines[event.machine]=set()
        if event.type=="login":
            machines[event.machine].add(event.user)
        elif event.type=="logout":
            machines[event.machine].remove(event.user)
    return machines


def report(machines):
    for machine,user in machines.items():
        if user:
            userlist="' ".join(user)
            print(f"{machine} ==> {userlist}")

class Event:
  def __init__(self, edate, etype, m, u):
    self.date = edate
    self.type = etype
    self.machine = m
    self.user = u

events = [
  Event('2020-01-21 12:45:46', 'login', 'myworkstation.local', 'jordan'),
  Event('2020-01-22 15:53:42', 'logout', 'webserver.local', 'jordan'),
  Event('2020-01-21 18:53:21', 'login', 'webserver.local', 'lane'),
  Event('2020-01-22 10:25:34', 'logout', 'myworkstation.local', 'jordan'),
  Event('2020-01-21 08:20:01', 'login', 'webserver.local', 'jordan'),
  Event('2020-01-23 11:24:35', 'login', 'mailserver.local', 'chris'),
]

users=current_users(events)
report(users)
