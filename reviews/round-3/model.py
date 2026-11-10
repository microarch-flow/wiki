#!/usr/bin/env python3
"""Parameter-driven models for cases.md.

Only the case inputs are constants. Arbitration, timing guards, resource states,
and end-of-tick event delivery compute every output time.

The default compares results with expected.json; no command changes that file.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import json
from pathlib import Path
import sys


def require(condition, message):
    """Keep model checks active even when Python is invoked with -O."""
    if not condition:
        raise ValueError(f"model invariant failed: {message}")


@dataclass(frozen=True)
class ReadRequest:
    id: str
    arrival: int
    address: int


@dataclass(frozen=True)
class SramConfig:
    banks: int
    word_bytes: int
    read_latency: int
    initiation_interval: int


def simulate_sram(config: SramConfig, requests: list[ReadRequest]):
    """One physical 1RW port per bank; outputs have no shared bottleneck."""
    require(config.banks > 0 and config.word_bytes > 0, "invalid SRAM geometry")
    require(config.read_latency >= 0 and config.initiation_interval >= 1, "invalid SRAM timing")
    require(len({r.id for r in requests}) == len(requests), "duplicate SRAM request ID")
    require(all(r.address % config.word_bytes == 0 for r in requests), "unaligned SRAM address")
    arrivals = defaultdict(list)
    for req in requests:
        arrivals[req.arrival].append(req)
    pending = []
    next_accept = [0] * config.banks
    ready_events = defaultdict(list)
    accepted_at = {}
    ready_at = {}
    waits = []
    trace = []
    t = 0
    while len(ready_at) < len(requests):
        pending.extend(arrivals.pop(t, []))
        pending.sort(key=lambda r: (r.arrival, r.id))
        accepted = []
        bank_winner = {}
        still_pending = []
        for req in pending:
            bank = (req.address // config.word_bytes) % config.banks
            if t >= next_accept[bank]:
                accepted.append(req.id)
                accepted_at[req.id] = t
                bank_winner[bank] = req.id
                next_accept[bank] = t + config.initiation_interval
                ready_events[t + config.read_latency].append(req.id)
            else:
                still_pending.append(req)
                reason = "same_bank_port_arbitration" if bank in bank_winner else "port_ii"
                wait = {"t": t, "id": req.id, "bank": bank, "reason": reason,
                        "next_accept": next_accept[bank]}
                if bank in bank_winner:
                    wait["winner"] = bank_winner[bank]
                waits.append(wait)
        pending = still_pending
        ready = sorted(ready_events.pop(t, []))
        for request_id in ready:
            require(request_id not in ready_at, f"duplicate SRAM result {request_id}")
            ready_at[request_id] = t
        trace.append({"t": t, "accepted": sorted(accepted), "ready": ready})
        t += 1

    # Check interface behavior, rather than compare with an answer fixture.
    require(not arrivals and not pending and not ready_events, "unconsumed SRAM events")
    require(set(accepted_at) == set(ready_at) == {r.id for r in requests}, "missing SRAM event")
    for req in requests:
        require(accepted_at[req.id] >= req.arrival, f"{req.id} accepted before arrival")
        require(ready_at[req.id] == accepted_at[req.id] + config.read_latency,
                f"{req.id} incorrect SRAM ready time")
    for bank in range(config.banks):
        times = sorted(accepted_at[r.id] for r in requests
                       if (r.address // config.word_bytes) % config.banks == bank)
        require(all(b - a >= config.initiation_interval for a, b in zip(times, times[1:])),
                f"SRAM bank {bank} violated II")
    return trace, waits


@dataclass(frozen=True)
class DramTiming:
    nRCD: int = 14
    nRP: int = 14
    nRAS: int = 35
    nRTP: int = 6
    nWR: int = 12
    CL: int = 14
    AL: int = 0
    WL: int = 10
    burst_transfers: int = 8
    transfers_per_ck: int = 2


@dataclass
class Bank:
    # CLOSED/PRECHARGING is open_row=None, differentiated by next_act.
    # OPEN/ACTIVATING is open_row!=None, differentiated by next_column.
    open_row: str | None = None
    next_act: int = 0
    next_column: int = 0
    pre_ready: int = 0


def issue_dram(bank: Bank, t: int, command: str, row: str | None, p: DramTiming):
    """Update a single-bank timing scoreboard after one legal external command."""
    require(p.burst_transfers % p.transfers_per_ck == 0, "invalid DRAM burst")
    burst_ck = p.burst_transfers // p.transfers_per_ck
    if command == "ACT":
        require(bank.open_row is None and t >= bank.next_act, f"ACT illegal at t={t}")
        require(row is not None, "ACT requires a row")
        bank.open_row = row
        bank.next_column = t + p.nRCD - p.AL
        bank.pre_ready = t + p.nRAS
    elif command == "PRE":
        require(bank.open_row is not None and t >= bank.pre_ready, f"PRE illegal at t={t}")
        bank.open_row = None
        bank.next_act = t + p.nRP
    elif command in ("RD", "WR"):
        require(bank.open_row == row and t >= bank.next_column, f"{command} illegal at t={t}")
        recovery = p.AL + p.nRTP if command == "RD" else p.WL + burst_ck + p.nWR
        bank.pre_ready = max(bank.pre_ready, t + recovery)
    else:
        raise ValueError(command)


def simulate_dram(p: DramTiming, history: list[tuple[int, str, str | None]], target="X"):
    """Earliest legal command at each integer CK; keep target row open after RD.

    Scope: PL=0, CS-to-CA latency off, write CRC off. The challenge guarantees
    every unmodeled CA/DQ/rank/refresh constraint is already satisfied.
    Historical WR still creates its future data/recovery bound in pre_ready.
    """
    require(p.transfers_per_ck == 2, "output requires two transfers per CK")
    bank = Bank(next_act=min([0] + [event[0] for event in history]))
    previous_history_t = None
    for t, command, row in history:
        require(t < 0, "historical DRAM command must precede t=0")
        require(previous_history_t is None or t > previous_history_t, "unordered DRAM history")
        issue_dram(bank, t, command, row, p)
        previous_history_t = t

    commands = []
    t = 0
    while True:
        if bank.open_row == target:
            candidate, legal = "RD", t >= bank.next_column
        elif bank.open_row is None:
            candidate, legal = "ACT", t >= bank.next_act
        else:
            candidate, legal = "PRE", t >= bank.pre_ready
        if legal:
            issue_dram(bank, t, candidate, target if candidate in ("ACT", "RD") else None, p)
            commands.append([t, candidate])
            if candidate == "RD":
                first_half = 2 * (t + p.AL + p.CL)
                last_half = first_half + p.burst_transfers - 1
                end_half = first_half + p.burst_transfers
                require(bank.open_row == target, "target DRAM row not open")
                require(all(b[0] > a[0] for a, b in zip(commands, commands[1:])),
                        "more than one DRAM command per CK")
                return {"cmd": commands, "first_half": first_half,
                        "last_half": last_half, "end_half": end_half}
        t += 1


def expand_dram(result):
    """List CKs in [0, data_window_end), retaining command-idle intervals."""
    commands = dict(result["cmd"])
    trace = []
    for t in range((result["end_half"] + 1) // 2):
        transfers = [h for h in (2 * t, 2 * t + 1)
                     if result["first_half"] <= h <= result["last_half"]]
        trace.append({"t": t, "cmd": commands.get(t), "data_transfer_half": transfers})
    return trace


@dataclass(frozen=True)
class NocConfig:
    depth: int = 2
    forward_latency: int = 2
    return_latency: int = 1
    consume_from: int = 5


def simulate_noc(p: NocConfig, flits: list[str]):
    """Decide from S(t), then commit actions and events due at end of t."""
    require(p.depth > 0 and p.forward_latency >= 1 and p.return_latency >= 1,
            "invalid NoC resource or timing")
    source = deque(flits)
    fifo = deque()
    forward = []  # (end-of-tick due time, flit ID)
    reverse = []  # (end-of-tick due time, released-slot flit ID)
    credit = p.depth
    popped = []
    arrived_at_end = {}
    trace = []
    t = 0
    while True:
        require(credit + len(forward) + len(fifo) + len(reverse) == p.depth,
                f"NoC slot conservation at S({t})")
        require(0 <= credit <= p.depth and len(fifo) <= p.depth,
                f"NoC capacity at S({t})")
        static = not source and not forward and not fifo and not reverse and credit == p.depth
        send = source[0] if source and credit > 0 else None
        pop = fifo[0] if t >= p.consume_from and fifo else None
        trace.append({"t": t, "credit": credit, "forward": len(forward),
                      "fifo": len(fifo), "reverse": len(reverse), "send": send, "pop": pop})
        if static:
            require(popped == flits, "NoC flit order")
            break  # Include the first static beginning-of-tick state.

        # Both decisions above read the old snapshot. These updates form next.
        if send is not None:
            require(credit > 0, f"NoC send without credit at t={t}")
            require(source.popleft() == send, f"NoC source order at t={t}")
            credit -= 1
            forward.append((t + p.forward_latency, send))
        if pop is not None:
            require(fifo.popleft() == pop, f"NoC FIFO order at t={t}")
            require(t > arrived_at_end[pop], f"NoC arrival-to-pop bypass at t={t}")
            popped.append(pop)
            reverse.append((t + p.return_latency, pop))

        due_forward = [event for event in forward if event[0] == t]
        due_reverse = [event for event in reverse if event[0] == t]
        require(all(due >= t for due, _ in forward + reverse), f"overdue NoC event at t={t}")
        forward = [event for event in forward if event[0] != t]
        reverse = [event for event in reverse if event[0] != t]
        for _, flit in due_forward:
            fifo.append(flit)
            arrived_at_end[flit] = t
        credit += len(due_reverse)
        # This is committed S(t+1); due credits cannot affect this tick's send.
        require(credit + len(forward) + len(fifo) + len(reverse) == p.depth,
                f"NoC slot conservation at S({t + 1})")
        require(0 <= credit <= p.depth and len(fifo) <= p.depth,
                f"NoC capacity at S({t + 1})")
        t += 1
    return trace


def compute_results():
    results = {}
    waits = {}
    common = {"banks": 2, "word_bytes": 4, "read_latency": 3}
    for name, b_address, ii in [("S1", 0x3C, 1), ("S2", 0x38, 1), ("S3", 0x3C, 2)]:
        requests = [ReadRequest("A", 0, 0x34), ReadRequest("B", 0, b_address),
                    ReadRequest("C", 1, 0x30)]
        results[name], waits[name] = simulate_sram(SramConfig(**common, initiation_interval=ii), requests)

    history = {
        "D1": [(-64, "ACT", "X")],
        "D2": [],  # the challenge says PRE completed before request arrival
        "D3": [(-64, "ACT", "Y")],
        "D4": [(-40, "ACT", "Y"), (-8, "WR", "Y")],
    }
    for name, events in history.items():
        results[name] = simulate_dram(DramTiming(), events)
    for name, return_latency in [("N1", 1), ("N2", 3)]:
        results[name] = simulate_noc(NocConfig(return_latency=return_latency),
                                     [f"F{i}" for i in range(4)])
    return results, waits


def first_difference(expected, actual, location="results"):
    """Return the first strict JSON difference, including case, tick and field."""
    if type(expected) is not type(actual):
        return f"{location}: expected {expected!r}, got {actual!r} (type differs)"
    if isinstance(expected, dict):
        missing = expected.keys() - actual.keys()
        extra = actual.keys() - expected.keys()
        if missing or extra:
            return f"{location}: missing keys {sorted(missing)}, extra keys {sorted(extra)}"
        for key in expected:
            # Top-level keys are case names; nested keys are field names.
            child = key if location == "results" else f"{location}.{key}"
            difference = first_difference(expected[key], actual[key], child)
            if difference:
                return difference
    elif isinstance(expected, list):
        for i, (wanted, got) in enumerate(zip(expected, actual)):
            if isinstance(wanted, dict) and "t" in wanted:
                child = f"{location} t={wanted['t']}"
            elif location.endswith(".cmd") and isinstance(wanted, list) and wanted:
                child = f"{location}[{i}] t={wanted[0]}"
            else:
                child = f"{location}[{i}]"
            difference = first_difference(wanted, got, child)
            if difference:
                return difference
        if len(expected) != len(actual):
            i = min(len(expected), len(actual))
            tail = (expected if len(expected) > len(actual) else actual)[i]
            if isinstance(tail, dict) and "t" in tail:
                detail = f"; first unmatched row has t={tail['t']}"
            elif location.endswith(".cmd") and isinstance(tail, list) and tail:
                detail = f"; first unmatched command has t={tail[0]}"
            else:
                detail = f"; first unmatched index is {i}"
            return f"{location}: expected {len(expected)} entries, got {len(actual)}{detail}"
    elif expected != actual:
        return f"{location}: expected {expected!r}, got {actual!r}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="compare with independent expected.json (default)")
    action.add_argument("--case", choices=["S1", "S2", "S3", "D1", "D2", "D3", "D4", "N1", "N2"],
                        help="print one computed case, including NoC tick trace")
    action.add_argument("--expand-dram", choices=["D1", "D2", "D3", "D4"],
                        help="print each CK including idle periods and data transfer edges")
    action.add_argument("--waits", action="store_true", help="print SRAM waiting reasons")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("expected.json"),
                        help="reference JSON for comparison")
    args = parser.parse_args()
    results, waits = compute_results()
    if args.expand_dram:
        output = expand_dram(results[args.expand_dram])
    elif args.waits:
        output = waits
    elif args.case:
        output = results[args.case]
    else:
        try:
            expected = json.loads(args.expected.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: cannot read expected JSON: {exc}", file=sys.stderr)
            return 1
        difference = first_difference(expected, results)
        if difference:
            print(f"FAIL: {difference}", file=sys.stderr)
            return 1
        print(f"PASS: {len(results)} cases match expected.json")
        return 0
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
