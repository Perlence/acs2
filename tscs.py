# -*- encoding: utf-8 -*-
from acs2 import Scheduler, Pipeline, Operation


ALU = Pipeline('ALU')
FPU = Pipeline('FPU')
BUS = Pipeline('BUS')


class SampleOperation(Operation):
    lock = []
    symbol = u'┴'


class CacheOperation(Operation):
    lock = [BUS]
    length = 6
    symbol = u'╨'


class MDOOperation(Operation):
    lock = []
    symbol = u'┬'


class UOOperation(Operation):
    lock = []
    length = 2
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

    scheduler.add(
        MDO(2, FPU, cached=True),
        UO_(1, ALU, cached=False),
        MDO(1, ALU, cached=True),
        MDO(2, FPU, cached=False),
        MDO(2, FPU, cached=True),
        UO_(1, ALU, cached=True),
        MDO(1, ALU, cached=True))
    scheduler.start()

    scheduler.add(
        MDO(1, ALU, cached=False),
        UO_(2, FPU, cached=False),
        UO_(1, ALU, cached=True),
        MDO(1, FPU, cached=False),
        MDO(1, FPU, cached=False),
        UO_(1, ALU, cached=False),
        MDO(2, ALU, cached=True),
        UO_(1, FPU, cached=True),
        UO_(2, ALU, cached=True),
        MDO(1, FPU, cached=False))
    scheduler.start()

    scheduler.add(
        MDO(1, FPU, cached=True),
        UO_(2, ALU, cached=False),
        UO_(1, ALU, cached=True),
        MDO(1, FPU, cached=True),
        MDO(1, ALU, cached=False),
        UO_(1, FPU, cached=False),
        MDO(2, ALU, cached=False),
        UO_(1, FPU, cached=True),
        MDO(2, ALU, cached=False),
        UO_(1, FPU, cached=False),
        UO_(2, ALU, cached=False),
        MDO(1, FPU, cached=True))
    scheduler.start()

if __name__ == '__main__':
    main()
