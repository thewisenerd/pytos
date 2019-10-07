from statistics import mean, median


class RequestContext:
    def __init__(self, name: str):
        self.name = name
        self.ctr = 0
        self.dup = 0
        self.latency = []

    def add(self, duration: float, count: int = 0, dupes: int = 0):
        self.ctr = self.ctr + count
        self.dup = self.dup + dupes
        self.latency.append(duration)

    def stat(self):
        name = self.name
        ctr = self.ctr
        dup = self.dup
        latency = self.latency
        tpl = '[{}] total: {}, dup: {} ({}), latency (avg): {}, (med): {}'
        fmt = tpl.format(name, ctr, dup, ctr - dup, mean(latency), median(latency))
        print(fmt)
