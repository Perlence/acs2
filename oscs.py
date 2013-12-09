from acs2 import Scheduler, Pipeline, Operation


CPU = Pipeline('CPU')
BUS = Pipeline('BUS')


class SampleOperation(Operation):
    lock = [CPU]
    length = 1


class CacheOperation(Operation):
    lock = [BUS]
    length = 8


class MDOOperation(Operation):
    lock = [CPU]


class UOOperation(Operation):
    lock = [CPU, BUS]


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
    scheduler.add(MDO(1, cached=True))
    scheduler.add(MDO(2, cached=False))
    scheduler.add(UO_(1, cached=True))
    scheduler.add(UO_(2, cached=True))
    scheduler.add(MDO(1, cached=False))
    scheduler.add(MDO(2, cached=True))
    scheduler.start()

if __name__ == '__main__':
    main()
