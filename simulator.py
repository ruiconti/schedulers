from dataclasses import dataclass
from time import sleep, time
from typing import List, Optional, List
from types import GeneratorType

from random import randint


class Job:
    pass


class Scheduler:
    pass


class DummyJob(Job):
    def __init__(
        self,
        name: Optional[str] = "dummy",
        start_at: float = 0.0,
        job_quantum_ratio: Optional[float] = None,
    ):
        # Defines for how many ms a job runs, its workload in ms :: T
        # Where 0 <= T <= QUANTUM
        if job_quantum_ratio is None:
            job_quantum_ratio = randint(0, 1000) / 1000
        self.job_quantum_ratio = job_quantum_ratio
        self.start_at = start_at
        self.name = name

        self.run_count = 0
        self.time_ran = 0.0

    def __repr__(self):
        return "<DummyJob ran {:.2f} totalling {:.2f}s>".format(
            self.run_count, self.time_ran
        )

    def run(self, simulator: "Simulator"):
        # State registers
        self.run_count += 1
        job_workload = (simulator.quantum * self.job_quantum_ratio) / 1000
        self.time_ran += job_workload

        # Simulate a busy processor
        sleep(job_workload)
        print(
            "Job {} (quantum ratio {:.2f}%)".format(
                self.name, self.job_quantum_ratio * 100
            )
        )


class RoundRobinScheduler(Scheduler):
    jobs: List[Job]

    def __init__(self, jobs: List[Job]):
        from copy import copy

        self.jobs = copy(jobs)
        self._iter_jobs = iter(jobs)

    def round_robin(self):
        "Round-robin scheduler"
        try:
            job = next(self._iter_jobs)
        except StopIteration:
            self._iter_jobs = iter(self.jobs)
            job = next(self._iter_jobs)
        finally:
            return job

    def fetch_next_job(self, now: float = 0.0) -> Job:
        # We should sort self.jobs by job.start_at and use scheduling
        # given top-most job. If and only if job.start_at > now.
        return self.round_robin()


MAX_DURATION_SECONDS = 5
QUANTUM_MILLI = 100
JOBS_COUNT = 40


@dataclass
class Simulator:
    scheduler: Scheduler
    quantum: float = QUANTUM_MILLI
    running: bool = True
    t_start: float = time()
    max_duration: float = MAX_DURATION_SECONDS
    _last_tick: float = 0.0

    @property
    def now(self):
        return time() - self.t_start

    def execute(self):
        self.run()

    def tick(self):
        if self.now - self._last_tick >= 1:
            print("T={:.3f}s".format(self.now))
            self._last_tick = self.now
        return time() - self.t_start

    def run(self):
        while self.running:
            self.tick()
            try:
                if self.now >= MAX_DURATION_SECONDS:
                    self.running = False

                # This means that each job stays IDLE.
                job = self.scheduler.fetch_next_job()
                job.run(simulator=self)
                # self.run_next_job()
            except KeyboardInterrupt:
                self.running = False

        print("End of simulation")


if __name__ == "__main__":
    # Tear things up
    jobs = [DummyJob(name=i) for i in range(JOBS_COUNT)]
    scheduler = RoundRobinScheduler(jobs=jobs)
    simulator = Simulator(scheduler=scheduler)

    # Run it.
    simulator.execute()
