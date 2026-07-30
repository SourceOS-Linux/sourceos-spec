# ResourceContract negative control — the throttle must be observed to fire

A `ResourceContract` whose `enforcement` is anything but `observe` must point at a procedure
that drives a consumer past the limit and asserts the enforcement **observably happened**. This
file is that procedure for `scope: tenant`, `resource: disk-writes` on cgroup v2.

It exists because two macOS resource reports on 2026-07-30 declared limits, measured
exceedances, and recorded `Action taken: none` — and because the most common Linux version of
the same failure is subtler: `io.max` written on a slice that contains no tasks, which looks
configured and throttles nothing.

## Why a count is not proof

`firedCount: 0` is the normal state of a healthy contract. It is also the normal state of a
contract wired to the wrong cgroup. The two are indistinguishable from the count alone, which
is why this procedure exists rather than a threshold on `firedCount`.

## Procedure

Both directions are required. A run that only demonstrates the positive is a control that has
never been observed refusing.

### 1. Confirm the tenant's tasks are actually in the slice

The step that catches the common misconfiguration. A limit on a slice with no tasks in it is
decoration.

```bash
SLICE=/sys/fs/cgroup/tenant-42.slice
test -s "$SLICE/cgroup.procs" || { echo "FAIL: no tasks in the slice the limit is written on"; exit 1; }
wc -l < "$SLICE/cgroup.procs"
```

For a VM, assert the **vCPU threads** are there, not just the launcher: a VMM spawned via
libvirt or podman commonly lands under the daemon's hierarchy while the tenant slice stays
empty.

### 2. Record the baseline

```bash
grep -E 'wbytes' "$SLICE/io.stat"
```

### 3. Drive the consumer past the limit

Write past `limit.value` within `window` from inside the slice. Direct I/O so the page cache
does not absorb it:

```bash
systemd-run --slice=tenant-42.slice --pipe -- \
  dd if=/dev/zero of=/var/lib/tenant-42/fill bs=1M count=3072 oflag=direct
```

### 4. Assert the enforcement was observed

```bash
grep -E 'wbytes' "$SLICE/io.stat"          # must show the write pressure
cat "$SLICE/io.pressure"                    # some/full avg10 must rise above baseline
```

For `resource: cpu` the equivalent assertion is `cpu.stat`'s `nr_throttled` and
`throttled_usec` incrementing; for `memory`, `memory.events`' `max` or `oom_kill`. **A
saturated consumer with a flat counter means the limit is not enforcing.** That is the whole
assertion — everything above is setup for it.

### 5. The negative half — remove the limit, confirm the counter stays flat

Without this, step 4 passes for any reason the counter might move, including unrelated load.

```bash
echo max > "$SLICE/io.max"     # or restore the prior value afterwards
# repeat step 3, then confirm the throttle counter does NOT advance
```

Restore the limit and re-run step 4 to confirm it advances again.

## Recording the result

A passing run updates the contract's `observedPeak` with a gate-eligible `Measurement` naming
the instrument (`cgroup v2 io.stat wbytes`, not `io.stat`), and leaves `firedCount` alone —
this procedure exercises the control, it is not production traffic.

## Status

**Procedure only; not yet executed against a runner.** The contract that points here therefore
carries a demonstrable *intent* to throttle and no execution record. Stating that plainly is
the point: an unrun procedure is honest, whereas an `observedPeak` fabricated to look
calibrated would be the paper control this whole schema exists to refuse. Executing it needs
the macfox KVM host, where the open question is whether its existing cgroup limits have ever
throttled anything.
