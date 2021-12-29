import time
from typing import List, Optional, Protocol


class Profiler(Protocol):
    def cycle(self):
        """Collect profile data. Called once per CPU cycle."""

    def __str__(self):
        """Output profile results."""


class CPUFrequencyProfiler(Profiler):
    """Profile how many cycles are performed per second."""
    def __init__(self):
        self.timings = {}
        self.count = 0
        self.tick = None

    def cycle(self):
        now = int(time.time())
        if self.tick != now:
            self.tick = now
            self.count = 0
        self.timings[now] = self.count
        self.count += 1

    def __str__(self):
        return f"CPU frequency: {self.timings}"


class CPUTimingProfiler(Profiler):
    """Profile long each cycle takes to execute."""
    def __init__(self):
        self.profile = []
        self.tick = 0

    def cycle(self):
        now = time.perf_counter()
        self.profile.append(int((now - self.tick) * 1000))
        self.tick = now

    def __str__(self):
        return f"CPU timings: {self.profile}"


class CPUProfiler:
    """Profile CPU cycles, shares interface with CPU to be passed to intepretor."""

    def __init__(self, cpu, profilers: Optional[List[Profiler]] = None):
        self.cpu = cpu

        if profilers is None:
            profilers = [
                CPUFrequencyProfiler(),
                CPUTimingProfiler(),
            ]
        self.profilers: List[Profiler] = profilers

    def cycle(self):
        """Update profilers and pass through call to CPU."""

        for profiler in self.profilers:
            profiler.cycle()

        self.cpu.cycle()

    @property
    def memory(self):
        """Pass through call to fetch CPU's memory."""
        return self.cpu.memory

    def shutdown(self):
        """Output profiler timings.

        Called when backend emits QUIT event."""
        for profiler in self.profilers:
            print(profiler)

        self.cpu.shutdown()
