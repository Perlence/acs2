from time import sleep


class PipelineLocked(Exception):
    pass


class Pipeline(object):
    def __init__(self, name):
        self.name = name
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
        return "Pipeline('%s', locked=%s)" % (self.name, self.current is not None)


class Operation(object):
    lock = []
    length = None

    def __init__(self, lock=[], length=None):
        if length is not None:
            self.length = length
        self.lock = self.lock[:] + lock
        self.pipeline = self.lock[0]

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
            yield self


class Scheduler(object):
    def __init__(self, *pipelines):
        self.pipelines = pipelines
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def start(self):
        ticknumber = 1
        while self.tasks:
            # import pdb; pdb.set_trace()
            # if ticknumber == 4:
            #     import ipdb; ipdb.set_trace()
            results = {}
            for task in self.tasks[:]:
                try:
                    tick = next(task)
                    if tick is not None:
                        results[tick.pipeline.name] = tick
                except StopIteration:
                    self.tasks.remove(task)
            map(Pipeline.release, self.pipelines)
            print ticknumber, results
            ticknumber += 1
            sleep(0.5)
