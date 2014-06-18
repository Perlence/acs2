# -*- encoding: utf-8 -*-
from acs2 import Scheduler, Pipeline, Operation


ALU = Pipeline('ALU')
FPU = Pipeline('FPU')
BUS = Pipeline('BUS')


class SampleOperation(Operation):
    lock = []
    length = 1
    symbol = u'┴'


class CacheOperation(Operation):
    lock = [BUS]
    length = 8
    symbol = u'╨'


class MDOOperation(Operation):
    lock = []
    symbol = u'┬'


class UOOperation(Operation):
    lock = []
    symbol = u'╥'


def MDOCommand(length, pipeline, cached):
    if not cached:
        for tick in CacheOperation():
            yield tick
    for tick in SampleOperation([pipeline]):
        yield tick
    for tick in MDOOperation([pipeline], length=length):
        yield tick


def UOCommand(length, pipeline, cached):
    if not cached:
        for tick in CacheOperation():
            yield tick
    for tick in SampleOperation([pipeline]):
        yield tick
    for tick in UOOperation([pipeline, BUS], length=length):
        yield tick


def main():
    MDO = MDOCommand
    UO_ = UOCommand

    scheduler = Scheduler(ALU, FPU, BUS)
    scheduler.add(MDO(2, FPU, cached=True))
    scheduler.add(UO_(1, ALU, cached=False))
    scheduler.add(MDO(1, ALU, cached=True))
    scheduler.add(MDO(2, FPU, cached=False))
    scheduler.add(MDO(2, FPU, cached=True))
    scheduler.add(UO_(1, ALU, cached=True))
    scheduler.add(MDO(1, ALU, cached=True))
    scheduler.start()

if __name__ == '__main__':
    main()
