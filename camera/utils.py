import datetime

start_time = datetime.datetime.now()

def time_elapsed(name, printout=True):
    global start_time
    if printout:
        print("Time checkpoint")
        print(name + ":", (datetime.datetime.now() - start_time).total_seconds())
        print()
    start_time = datetime.datetime.now()