# Course: Operating Systems_11010CS 342302

Start Date: 2021/09/13
Used language: Python, C

## Content: Exercise on OS concepts (Python)

1. Counting semaphore and threads: Parking lot example 
2. Deadlock detection by DFS
3. Page replacement policies including OPT, LRU, FIFO, SecondChance
4. File system simulation (FCB, DEntry)

## Final Project: Parking lot simuilation 

### Spec
1. Make 5 cars competing for 2 spots. Make thread for each car.
2. Threads package supports at most 4 threads (including main).
3. Create threads up to the maximum number available by semaphore.
4. Maintain a “log” for the events:<br>
● When a car gets the parking spot (what time, which spot)<br>
● When a car exits the parking lot (what time)<br>

### Prerequisites
To compile this project and run testing and experiments, you need the following tools:<br>
● `make`<br>
● `EdSim51` - The 8051 Simulator<br>

### Sample output

