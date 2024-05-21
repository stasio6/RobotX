from datetime import datetime

start_time = datetime.now()

def time_elapsed(name, printout=True):
    global start_time
    if printout:
        print("Time checkpoint")
        print(name + ":", (datetime.now() - start_time).total_seconds())
        print()
    start_time = datetime.now()

def get_current_datetime():
    now = datetime.now()
    formatted_time = now.strftime("%y%m%d_%H%M%S")
    return formatted_time