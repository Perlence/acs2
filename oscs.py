# -*- encoding: utf-8 -*-
from acs2 import Scheduler, Pipeline, Operation


CPU = Pipeline('CPU')
BUS = Pipeline('BUS')


class SampleOperation(Operation):
    lock = [CPU]
    length = 1
    symbol = u'┴'


class CacheOperation(Operation):
    lock = [BUS]
    length = 8
    symbol = u'╨'


class MDOOperation(Operation):
    lock = [CPU]
    symbol = u'┬'


class UOOperation(Operation):
    lock = [CPU, BUS]
    symbol = u'╥'


def MDOCommand(length, cached):
    if not cached:
        for tick in CacheOperation():
            yield tick
    for tick in SampleOperation():
        yield tick
    for tick in MDOOperation(length=length):
        yield tick


def UOCommand(length, cached):
    if not cached:
        for tick in CacheOperation():
            yield tick
    for tick in SampleOperation():
        yield tick
    for tick in UOOperation(length=length):
        yield tick


def main():
    MDO = MDOCommand
    UO_ = UOCommand

    scheduler = Scheduler(CPU, BUS)

    scheduler.add(
        MDO(1, cached=True),
        MDO(2, cached=False),
        UO_(1, cached=True),
        UO_(2, cached=True),
        MDO(1, cached=False),
        MDO(2, cached=True))
    scheduler.start()

    scheduler.add(
        UO_(1, cached=False),
        UO_(2, cached=False),
        UO_(1, cached=True),
        MDO(1, cached=True),
        MDO(1, cached=False),
        UO_(1, cached=False),
        MDO(2, cached=True),
        UO_(1, cached=True),
        MDO(2, cached=True),
        MDO(1, cached=False))
    scheduler.start()

    scheduler.add(
        MDO(1, cached=True),
        UO_(2, cached=False),
        UO_(1, cached=True),
        MDO(1, cached=True),
        MDO(1, cached=False),
        UO_(1, cached=False),
        MDO(2, cached=False),
        UO_(1, cached=True),
        MDO(2, cached=False),
        UO_(1, cached=False))
    scheduler.start()


if __name__ == '__main__':
    main()
