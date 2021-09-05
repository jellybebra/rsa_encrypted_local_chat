import time


def timer(func):
    def wrapper(*args, **kwargs):
        before = time.time()
        func()
        print('Function took:', time.time() - before, 'seconds')

    return wrapper


@timer
def run():
    time.sleep(2)


run()


def star(func):
    def inner(*args, **kwargs):
        print("*" * 30)
        func(*args, **kwargs)
        print("*" * 30)
    return inner


def percent(func):
    def inner(*args, **kwargs):
        print("%" * 30)
        func(*args, **kwargs)
        print("%" * 30)
    return inner


@star
@percent
def printer(msg):
    print(msg)


printer("Hello")

class Test:
    @classmethod
    def bruh(cls):
        return ...