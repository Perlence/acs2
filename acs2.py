from time import sleep
from itertools import izip_longest
from collections import namedtuple


class PipelineLocked(Exception):
    pass


class Pipeline(object):
    def __init__(self):
        self.locked = False
        self.pending_release = False
        self.current = None

    def acquire(self):
        if self.locked:
            raise PipelineLocked
        else:
            self.locked = True

    def release(self):
        if self.pending_release:
            self.locked = False

    def release_after(self):
        self.pending_release = True


main_pipeline = Pipeline()
bus_pipeline = Pipeline()


class Operation(object):
    lock = []
    length = None

    def __init__(self, length=None, release=True):
        if length is not None:
            self.length = length
        self.pipeline = self.lock[0]
        self.release = release

    def acquire_pipelines(self):
        for pipeline in self.lock:
            pipeline.acquire()

    def release_pipelines(self):
        for pipeline in self.lock:
            pipeline.release_after()

    def __repr__(self):
        return '{}(length={})'.format(self.__class__.__name__, self.length)

    def __iter__(self):
        while True:
            try:
                self.acquire_pipelines()
                break
            except PipelineLocked:
                yield
        for i in xrange(self.length):
            self.pipeline.current = repr(self)
            if i == self.length - 1 and self.release:
                self.release_pipelines()
            yield repr(self)
            self.pipeline.current = None


class SampleOperation(Operation):
    lock = [main_pipeline]
    length = 1


class CacheOperation(Operation):
    lock = [bus_pipeline]
    length = 8


class MDOOperation(Operation):
    lock = [main_pipeline]


class UOOperation(Operation):
    lock = [main_pipeline, bus_pipeline]


def MDOCommand(length, cached):
    if not cached:
        for tick in CacheOperation():
            yield tick
    for tick in SampleOperation():
        yield tick
    for tick in MDOOperation(length):
        yield tick


def UOCommand(length, cached):
    if not cached:
        for tick in CacheOperation():
            yield tick
    for tick in SampleOperation(release=False):
        yield tick
    for tick in UOOperation(length):
        yield tick


class Scheduler(object):
    def __init__(self):
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def start(self):
        import pdb
        while self.tasks:
            # pdb.set_trace()
            for task in iter(self.tasks):
                try:
                    tick = next(task)
                except StopIteration:
                    self.tasks.remove(task)
            main_pipeline.release()
            bus_pipeline.release()
            print main_pipeline.current, bus_pipeline.current
            sleep(0.5)


def main():
    MDO = MDOCommand
    UO_ = UOCommand

    scheduler = Scheduler()
    scheduler.add(MDO(1, cached=True))
    scheduler.add(MDO(2, cached=False))
    scheduler.add(UO_(1, cached=True))
    scheduler.add(UO_(2, cached=True))
    scheduler.add(MDO(1, cached=False))
    scheduler.add(MDO(2, cached=True))
    scheduler.start()

if __name__ == '__main__':
    main()
