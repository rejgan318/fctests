''' Пример 3 multiprocessing example
https://www.journaldev.com/15631/python-multiprocessing-example '''

from multiprocessing import Lock, Process, Queue, current_process
import time
import random
import queue    # imported for using queue.Empty exception
import pickle


class Outdata:

    def __init__(self, info: str, data: float):
        self.info: str = info
        self.data: float = [data] * 3


def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
        except queue.Empty:

            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            print(task)
            ts = random.random()*6
            time.sleep(ts)
            d = Outdata(task + ' ' + current_process().name, ts)
            tasks_that_are_done.put(pickle.dumps(d))
    return True


def main():
    number_of_task = 10
    number_of_processes = 4
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    for i in range(number_of_task):
        tasks_to_accomplish.put("№ " + str(i))

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not tasks_that_are_done.empty():
        d = pickle.loads(tasks_that_are_done.get())
        print('Получено: Текст =', d.info, 'Данные =', d.data)

    return True


if __name__ == '__main__':
    main()