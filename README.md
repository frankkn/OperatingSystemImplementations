# Course: Operating Systems_11010CS 342302

Start Date: 2021/09/13

Used language: Python


## Content: Exercise on OS concepts (Python)

          1. Counting semaphore and threads: Parking lot example 
          2. Deadlock detection by DFS
          3. Page replacement policies including OPT, LRU, FIFO, SecondChance
          4. File system simulation (FCB, DEntry)
          
## Final Project: Parking lot simuilation 

Make 5 cars competing for 2 spots. 
Make thread for each car. Since our threads package supports at most 4 threads (including main), main() will use a semaphore to create threads up to the maximum number available.
