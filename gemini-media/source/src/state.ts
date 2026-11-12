// Local state for the Desktop extension: the spending ledger, the jobs and the per-minute counter,
// in one small JSON file inside the output folder. No prompt text and no image content is stored.
//
// The server is a single process, so an in-process queue makes every read-modify-write atomic:
// two simultaneous requests can never both pass a cap that only has room for one.
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

export interface Job {
  id: string;
  tool: string;
  model: string;
  status: "running" | "succeeded" | "failed";
  created_at: number;
  /** Local month (YYYY-MM) and day (YYYY-MM-DD) the cost counts against. */
  month: string;
  day: string;
  /** Reserved estimate while running, actual cost once settled. USD x 1,000,000. */
  cost_micros: number;
  operation: string | null;
  params: Record<string, unknown>;
  files: string[];
  error: string | null;
}

interface State {
  version: 1;
  jobs: Job[];
  requests: number[];
}

const KEEP_JOBS = 2000;
const nowSeconds = () => Math.floor(Date.now() / 1000);

function localPeriod(date = new Date()): { month: string; day: string } {
  const p = (n: number) => String(n).padStart(2, "0");
  const month = `${date.getFullYear()}-${p(date.getMonth() + 1)}`;
  return { month, day: `${month}-${p(date.getDate())}` };
}

export class StateStore {
  private queue: Promise<unknown> = Promise.resolve();

  constructor(private readonly file: string) {}

  private async load(): Promise<State> {
    try {
      const parsed = JSON.parse(await readFile(this.file, "utf8")) as State;
      if (parsed && parsed.version === 1 && Array.isArray(parsed.jobs) && Array.isArray(parsed.requests)) return parsed;
    } catch (e) {
      if ((e as NodeJS.ErrnoException).code !== "ENOENT") {
        // Unreadable state must not silently reset the spending counter.
        throw new Error("The extension's state file is damaged. Move or delete the .gemini-media folder inside the output folder to start again.");
      }
    }
    return { version: 1, jobs: [], requests: [] };
  }

  private async save(state: State): Promise<void> {
    if (state.jobs.length > KEEP_JOBS) state.jobs = state.jobs.slice(-KEEP_JOBS);
    await mkdir(dirname(this.file), { recursive: true });
    const temp = `${this.file}.${process.pid}.tmp`;
    await writeFile(temp, JSON.stringify(state), { mode: 0o600 });
    await rename(temp, this.file);
  }

  /** Runs `fn` on the state with exclusive access; saves when it returns `true` as second value. */
  private run<T>(fn: (state: State) => { result: T; changed: boolean }): Promise<T> {
    const next = this.queue.then(async () => {
      const state = await this.load();
      const { result, changed } = fn(state);
      if (changed) await this.save(state);
      return result;
    });
    this.queue = next.catch(() => undefined);
    return next;
  }

  month(): string {
    return localPeriod().month;
  }

  /** Per-minute limit for generation requests. Counts the request when it is allowed. */
  allowRequest(limit: number): Promise<boolean> {
    return this.run((state) => {
      const now = nowSeconds();
      state.requests = state.requests.filter((ts) => ts > now - 60);
      if (state.requests.length >= limit) return { result: false, changed: false };
      state.requests.push(now);
      return { result: true, changed: true };
    });
  }

  /** Atomically reserves the estimate against the monthly cap. False when it does not fit. */
  reserve(entry: { id: string; tool: string; model: string; costMicros: number; capMicros: number; params: Record<string, unknown> }): Promise<boolean> {
    return this.run((state) => {
      const { month, day } = localPeriod();
      const spent = state.jobs.filter((j) => j.month === month).reduce((sum, j) => sum + j.cost_micros, 0);
      if (spent + entry.costMicros > entry.capMicros) return { result: false, changed: false };
      state.jobs.push({
        id: entry.id,
        tool: entry.tool,
        model: entry.model,
        status: "running",
        created_at: nowSeconds(),
        month,
        day,
        cost_micros: entry.costMicros,
        operation: null,
        params: entry.params,
        files: [],
        error: null,
      });
      return { result: true, changed: true };
    });
  }

  setOperation(id: string, operation: string): Promise<void> {
    return this.run((state) => {
      const job = state.jobs.find((j) => j.id === id);
      if (job) job.operation = operation;
      return { result: undefined, changed: Boolean(job) };
    });
  }

  /** Replaces the reservation with the final cost and outcome. A settled job is not changed again. */
  settle(id: string, outcome: { status: "succeeded" | "failed"; costMicros: number; files: string[]; error: string | null }): Promise<Job> {
    return this.run((state) => {
      const job = state.jobs.find((j) => j.id === id);
      if (!job) throw new Error("job disappeared");
      if (job.status !== "running") return { result: job, changed: false };
      job.status = outcome.status;
      job.cost_micros = Math.max(0, Math.round(outcome.costMicros));
      job.files = outcome.files;
      job.error = outcome.error;
      return { result: job, changed: true };
    });
  }

  getJob(id: string): Promise<Job | null> {
    return this.run((state) => ({ result: state.jobs.find((j) => j.id === id) ?? null, changed: false }));
  }

  monthSpent(): Promise<number> {
    return this.run((state) => {
      const { month } = localPeriod();
      return { result: state.jobs.filter((j) => j.month === month).reduce((sum, j) => sum + j.cost_micros, 0), changed: false };
    });
  }

  daySpent(): Promise<number> {
    return this.run((state) => {
      const { day } = localPeriod();
      return { result: state.jobs.filter((j) => j.day === day).reduce((sum, j) => sum + j.cost_micros, 0), changed: false };
    });
  }

  byTool(): Promise<{ tool: string; count: number; spent_usd: number }[]> {
    return this.run((state) => {
      const { month } = localPeriod();
      const totals = new Map<string, { count: number; micros: number }>();
      for (const job of state.jobs) {
        if (job.month !== month || job.cost_micros === 0) continue;
        const t = totals.get(job.tool) ?? { count: 0, micros: 0 };
        t.count++;
        t.micros += job.cost_micros;
        totals.set(job.tool, t);
      }
      const result = [...totals].sort(([a], [b]) => a.localeCompare(b)).map(([tool, t]) => ({ tool, count: t.count, spent_usd: Math.round(t.micros / 100) / 10_000 }));
      return { result, changed: false };
    });
  }
}
