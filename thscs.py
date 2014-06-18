# -*- encoding: utf-8 -*-
from acs2 import Scheduler, Pipeline, Operation


ALU = Pipeline('ALU')
FPU = Pipeline('FPU')
BUS = Pipeline('BUS')
DMA = Pipeline('DMA')


class SampleOperation(Operation):
    lock = []
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
    length = 2
    symbol = u'╥'


class RAMOperation(Operation):
    lock = [DMA]
    length = 4
    symbol = u'┴'


class ReadOperation(Operation):
    lock = [DMA, BUS]
    length = 2
    symbol = u'╥'


class WriteOperation(Operation):
    lock = [DMA]
    length = 2
    symbol = u'┬'


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


def ReadCommand(length):
    for tick in RAMOperation():
        yield tick
    for tick in ReadOperation(length=length):
        yield tick


def WriteCommand(length):
    for tick in RAMOperation():
        yield tick
    for tick in WriteOperation(length=length):
        yield tick


def main():
    MDO = MDOCommand
    UO_ = UOCommand
    ChD = ReadCommand
    ZR_ = WriteCommand

    scheduler = Scheduler(ALU, FPU, BUS, DMA)

    scheduler.add(
        MDO(1, ALU, cached=0),
        UO_(2, FPU, cached=0),
        UO_(1, ALU, cached=1),
        MDO(1, FPU, cached=0),
        MDO(1, FPU, cached=0),
        UO_(1, ALU, cached=0),
        MDO(2, ALU, cached=1),
        UO_(1, FPU, cached=1),
        UO_(2, ALU, cached=1),
        MDO(1, FPU, cached=0),
        ChD(1),
        ChD(2),
        ZR_(2),
        ChD(1),
        ZR_(2),
        ChD(1))
    scheduler.start()

if __name__ == '__main__':
    main()
