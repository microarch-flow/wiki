"""Small deterministic teaching model; times are assumptions, not GPU results."""

from dataclasses import dataclass
import json
import math


@dataclass(frozen=True)
class Request:
    name: str
    arrival_ms: float
    prompt_tokens: int
    output_tokens: int


def simulate(requests, token_budget=5):
    """Decode-first, FCFS prefill; no memory limit, cancellation, or speculation."""
    if type(token_budget) is not int or token_budget <= 0:
        raise ValueError("token_budget must be a positive integer")
    requests = list(requests)
    if len({r.name for r in requests}) != len(requests):
        raise ValueError("request names must be unique")
    for request in requests:
        if not request.name or not math.isfinite(request.arrival_ms) or request.arrival_ms < 0:
            raise ValueError("a request needs a name and nonnegative finite arrival")
        if any(type(n) is not int or n <= 0 for n in (request.prompt_tokens, request.output_tokens)):
            raise ValueError("prompt and output lengths must be positive integers")
    ordered = sorted(enumerate(requests), key=lambda pair: (pair[1].arrival_ms, pair[0]))
    states = {
        r.name: {"request": r, "prefilled": 0, "output_times_ms": []}
        for _, r in ordered
    }
    now = 0.0
    steps = []
    while True:
        pending = [s for s in states.values()
                   if len(s["output_times_ms"]) < s["request"].output_tokens]
        if not pending:
            break
        ready = [s for s in pending if s["request"].arrival_ms <= now]
        if not ready:
            now = min(s["request"].arrival_ms for s in pending)
            continue
        budget = token_budget
        plan = []
        kv_read = 0
        for state in ready:
            request = state["request"]
            if budget and state["prefilled"] == request.prompt_tokens:
                plan.append((state, "decode", 1))
                kv_read += request.prompt_tokens + len(state["output_times_ms"]) - 1
                budget -= 1
        for state in ready:
            missing = state["request"].prompt_tokens - state["prefilled"]
            if budget and missing:
                count = min(budget, missing)
                plan.append((state, "prefill", count))
                budget -= count
        if not plan:
            raise RuntimeError("ready work made no progress")
        prefill = sum(n for _, phase, n in plan if phase == "prefill")
        decode = sum(n for _, phase, n in plan if phase == "decode")
        duration = 1 + .1 * prefill + .2 * decode + .001 * kv_read
        end = round(now + duration, 12)
        emitted = []
        for state, phase, count in plan:
            if phase == "prefill":
                state["prefilled"] += count
            if phase == "decode" or state["prefilled"] == state["request"].prompt_tokens:
                state["output_times_ms"].append(end)
                emitted.append(state["request"].name)
        steps.append({
            "start_ms": now, "end_ms": end,
            "work": [{"request": s["request"].name, "phase": phase, "tokens": n}
                     for s, phase, n in plan],
            "decode_kv_positions": kv_read, "emitted": emitted,
        })
        now = end
    output = {}
    for name, state in states.items():
        times = state["output_times_ms"]
        output[name] = {
            "prefilled": state["prefilled"], "output_times_ms": times,
            "ttft_ms": round(times[0] - state["request"].arrival_ms, 12),
            "e2e_ms": round(times[-1] - state["request"].arrival_ms, 12),
            "tpot_ms": round((times[-1] - times[0]) / (len(times) - 1), 12) if len(times) > 1 else None,
        }
    return {"time_ms": now, "steps": steps, "requests": output}


def example():
    return simulate([Request("A", 0, 8, 4), Request("B", 0, 3, 2), Request("C", 5, 6, 3)])


if __name__ == "__main__":
    print(json.dumps(example(), ensure_ascii=False, indent=2))
