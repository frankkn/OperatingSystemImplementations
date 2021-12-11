import threading
def MakeParkingLot(N):
    global sem        # semaphore for the parking lot
    global spots      # list for the spots
    global spotsSync  # for synchronizing access to spots
    spots = [None for i in range(N)]
    #  your code to initialize sem and spotsSync 
    sem = threading.Semaphore(N) # 同時最多N台車進來找車位
    spotsSync = [threading.Lock() for _ in range(N)] # 幫每個停車格建Lock

def MakeCars(C):
     # your code here to spawn threads
     # don’t forget to return the list
    return [threading.Thread(target = Park, args = (i,)) for i in range(C)]

def Park(car):
    global sem, spots, spotsSync
    # 2.3.1  ############################
    # if spot available, grab it; otherwise wait until available.
    #  Hint: don’t use if/else statement!  this is just one line.
    sem.acquire()
    # 2.3.2 ###########################################
    # after confirming one parking spot, modify the spots 
    # (Python list or your choice of list-like data structure to
    # put this car into the spot.  The following is an example
    # of what it can do, but you may have a different way of
    # grabbing parking spots.
    # Do you need to protect access to the following block of
    # code? If so, add code to protect it; if not, why not?
    for i in range(len(spots)):
        spotsSync[i].acquire()
        if spots[i] is None:
            spots[i] = car
            spotsSync[i].release()
            break
        spotsSync[i].release()
    snapshot = spots[:]  # make a copy for printing
    # now let us print out the current occupancy
    print("Car %d got spot: %s" % (car, snapshot))
    # leave the car on the lot for some (real) time!
    import time
    import random
    st = random.randrange(1, 3)
    time.sleep(st)
    # now ready to exit the parking lot.  What do we need to 
    # 2.3.3 ################################
    # update the spots data structure by replacing the spot 
    #    that current car occupies with the value None; 
    #    protect code if needed
    for i, car_id in enumerate(spots): # 可以取spots的index跟value
        if (car_id == car):
            spotsSync[i].acquire()
            spots[i] = None
            spotsSync[i].release()
    # (2) print out the status of the spots
    myCopySpots = spots[:]
    print("Car %d left after %d sec, %s" % (car, st, myCopySpots))
    # 2.3.4 #################################
    # (3) give the spot back to the pool 
    # (hint: semaphore operation)
    sem.release()

# Finally, have the main program run it:
if __name__ == '__main__':
    number_of_parking_spots = 5
    number_of_cars = 15
    sem, spots, spotsSync = None, None, None
    MakeParkingLot(number_of_parking_spots)
    cars = MakeCars(number_of_cars)
    for car in cars: 
        car.start()    
