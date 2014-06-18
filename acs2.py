# -*- encoding: utf-8 -*-
from __future__ import print_function

from time import sleep
from collections import OrderedDict


class PipelineLocked(Exception):
    pass


class Pipeline(object):
    def __init__(self, name):
        self.name = name
        self.current = None
        self.pending_release = False

    def __repr__(self):
        return ("Pipeline('%s', locked=%s)" %
                (self.name, self.current is not None))

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


class Operation(object):
    lock = []
    length = None

    def __init__(self, lock=None, length=None):
        if length is not None:
            self.length = length
        if lock is not None:
            self.lock = lock
        self.pipeline = self.lock[0]

    def __repr__(self):
        return '%s(length=%s)' % (self.__class__.__name__, self.length)

    def __iter__(self):
        for __ in self.acquire_pipelines():
            yield
        for i in xrange(self.length):
            if i == self.length - 1:
                self.release_pipelines()
            yield self

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


class Scheduler(object):
    def __init__(self, *pipelines):
        self.pipelines = pipelines
        self.pipeline_names = [pipeline.name for pipeline in pipelines]
        self.tasks = []

    def add(self, *tasks):
        self.tasks.extend(tasks)

    def start(self):
        ticknumber = 1
        graph = []
        started = []
        while started or self.tasks:
            results = OrderedDict.fromkeys(self.pipeline_names)
            # if ticknumber == 19:
            #     self.display(graph)
            #     import ipdb; ipdb.set_trace()
            for task in started + self.tasks[:]:
                try:
                    tick = next(task)
                    if tick is not None:
                        results[tick.pipeline.name] = tick
                        if task not in started:
                            self.tasks.remove(task)
                            started.append(task)
                except StopIteration:
                    started.remove(task)
            map(Pipeline.release, self.pipelines)
            graph.append(results.items())
            print('%3d' % ticknumber, *results.items())
            ticknumber += 1
        self.display(graph)

    def display(self, graph):
        for line in zip(*graph):
            for _, operation in line:
                if operation is not None:
                    print(operation.symbol, end='')
                else:
                    print(u'─', end='')
            print(u'\n')
