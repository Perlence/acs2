from time import sleep


class PipelineLocked(Exception):
    pass


class Pipeline(object):
    def __init__(self):
        self.current = None
        self.pending_release = False

    def acquire(self, operation):
        if self.current is None:
            self.current = operation
        elif self.current != operation:
            raise PipelineLocked

    def release(self):
        if self.pending_release:
            self.pending_release = False
            self.current = None

    def release_after(self):
        self.pending_release = True

    def __repr__(self):
        return 'Pipeline(locked=%s)' % (self.current is not None)

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
        while True:
            try:
                for pipeline in self.lock:
                    pipeline.acquire(self)
                return
            except PipelineLocked:
                yield

    def release_pipelines(self):
        for pipeline in self.lock:
            pipeline.release_after()

    def __repr__(self):
        return '%s(length=%s)' % (self.__class__.__name__, self.length)

    def __iter__(self):
        for __ in self.acquire_pipelines():
            yield
        for i in xrange(self.length):
            if i == self.length - 1:
                self.release_pipelines()
            yield repr(self)


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
    for tick in SampleOperation():
        yield tick
    for tick in UOOperation(length):
        yield tick


class Scheduler(object):
    def __init__(self, *pipelines):
        self.pipelines = pipelines
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def start(self):
        ticknumber = 1
        while self.tasks:
            # if ticknumber == 10:
                # import ipdb; ipdb.set_trace()
            results = []
            for task in self.tasks[:]:
                try:
                    tick = next(task)
                    if tick is not None:
                        results.append(tick)
                except StopIteration:
                    self.tasks.remove(task)
            map(Pipeline.release, self.pipelines)
            print ticknumber, results
            ticknumber += 1
            sleep(0.5)


def main():
    MDO = MDOCommand
    UO_ = UOCommand

    scheduler = Scheduler(main_pipeline, bus_pipeline)
    scheduler.add(MDO(1, cached=True))
    scheduler.add(MDO(2, cached=False))
    scheduler.add(UO_(1, cached=True))
    scheduler.add(UO_(2, cached=True))
    scheduler.add(MDO(1, cached=False))
    scheduler.add(MDO(2, cached=True))
    scheduler.start()

if __name__ == '__main__':
    main()
