# AGENTS.md

## Scope
These rules apply to the whole repository unless a deeper `AGENTS.md` overrides them.

## Architecture
- Keep core library code separate from demo/app code.
- Keep modules focused on one concern (simulation, spawning, rendering, benchmarking, etc.).
- Do not introduce "mega files."

## File Size Limits
- Target file size: `300-500` lines.
- Soft warning at `>300` lines: consider splitting by concern.
- Hard limit at `>500` lines: split into smaller modules before merging.
- Exceptions: generated code, lockfiles, and vendored third-party files.

## Coding Style (`C+-`)
- Prefer simple, explicit, data-oriented code.
- Prefer straightforward control flow over deep abstraction stacks.
- Keep ownership and mutation obvious at call sites.
- Avoid unnecessary macro/metaprogramming or type-level complexity.
- Minimize hidden allocations and hidden runtime work in hot paths.
- Keep APIs ergonomic for users while implementation remains performance-focused.

## Performance Expectations
- Performance-sensitive changes require measurement, not intuition.
- Add or update benchmarks when modifying spawn/update/render hot paths.
- Track baseline and post-change metrics for key workloads.
- Do not accept perf claims without numbers.

## Testing Expectations
- Keep correctness tests for behavior changes.
- Keep dedicated performance tests/benchmarks for throughput and frame-time stability.

