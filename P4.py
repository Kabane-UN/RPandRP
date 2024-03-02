from threading import RLock, Thread
from time import sleep, time
import csv


class Fork:
    def __init__(self, num):
        self.num = num
        self.lock = RLock()


class Phill:
    is_alive: bool = True
    data = []

    def __init__(self, name: int, fl: Fork, fr: Fork, st_time):
        self.name: int = name
        self.left: Fork = fl
        self.right: Fork = fr
        self.data = [["Time", "Doing"]]
        if fl.num < fr.num:
            self.less_left = True
        else:
            self.less_left = False
        self.start_time = st_time

    def log(self, current_time, message):
        self.data.append([str(round(current_time - self.start_time, 5)), message])


def life(ph: Phill):
    while ph.is_alive:
        ph.log(time(), f'Философ {ph.name} думает')
        sleep(2)
        if ph.less_left:
            ph.log(time(), f'Философ {ph.name} берет левую вилку')
            ph.left.lock.acquire()
            ph.log(time(), f'Философ {ph.name} берет правую вилку')
            ph.right.lock.acquire()
        else:
            ph.log(time(), f'Философ {ph.name} берет правую вилку')
            ph.right.lock.acquire()
            ph.log(time(), f'Философ {ph.name} берет левую вилку')
            ph.left.lock.acquire()
        ph.log(time(), f'Философ {ph.name} ест')
        sleep(2)
        if ph.less_left:
            ph.log(time(), f'Философ {ph.name} кладет правую вилку')
            ph.right.lock.release()
            ph.log(time(), f'Философ {ph.name} кладет левую вилку')
            ph.left.lock.release()
        else:
            ph.log(time(), f'Философ {ph.name} кладет левую вилку')
            ph.left.lock.release()
            ph.log(time(), f'Философ {ph.name} кладет правую вилку')
            ph.right.lock.release()


def save(ph: Phill):
    with open(rf'ph{ph.name}.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(ph.data)


N = 5
forks = []
for i in range(1, N+1):
    forks.append(Fork(i))

start_time = time()

phills = []
for i in range(1, N+1):
    if i != 1:
        phills.append(Phill(i, forks[i-2], forks[i-1], start_time))
    else:
        phills.append(Phill(i, forks[len(forks)-1], forks[i-1], start_time))

threads = []
for i in range(N):
    threads.append(Thread(target=life, args=(phills[i],)))


for i in range(N):
    threads[i].start()

sleep(20)

for i in range(N):
    phills[i].is_alive = False
for i in range(N):
    threads[i].join()

for i in range(N):
    save(phills[i])
