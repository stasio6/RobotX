from datetime import datetime

start_time = datetime.now()

def time_elapsed(name, printout=True):
    global start_time
    if printout:
        print("Time checkpoint")
        print(name + ":", (datetime.now() - start_time).total_seconds())
        print()
    start_time = datetime.now()

def get_timestamp(millis=False):
    if not millis:
        return datetime.now().strftime("%y%m%d_%H%M%S")
    else:
        return datetime.now().strftime("%y%m%d_%H%M%S_%f")[:-3]