# Optimization Attempts Log

## Date
- 2026-03-02

## Goal
- Improve `phecs` runtime performance without changing the public API/UX.

## Benchmark Method
- Command:
  - `python3 perf_test.py --entities 10000 --repeats 9 --warmup 3`
- Metrics compared by `median_ms`.

## Stable Baseline (current implementation)
- `spawn_mixed`: `13.196 ms`
- `query_physics`: `4.093 ms`
- `component_churn`: `2.745 ms`
- `despawn_all`: `1.772 ms`
- `frame_step`: `11.781 ms`

## Attempt A: Eager Component Index
- Idea:
  - Maintain `component_type -> {entity -> component}` index and use it directly in `find`.
  - Keep index synchronized on every `spawn/add/remove/despawn`.
- Result (median):
  - `spawn_mixed`: `17.640 ms`
  - `query_physics`: `5.276 ms`
  - `component_churn`: `4.264 ms`
  - `despawn_all`: `6.140 ms`
  - `frame_step`: `9.779 ms`
- Why rejected:
  - Significant regressions in write-heavy operations (`spawn`, `remove`, `despawn`), and query also got slower in this workload.

## Attempt B: Lazy-Rebuild Hybrid Index
- Idea:
  - Keep component index, but mark dirty on removals and rebuild lazily before `find`.
- Result (median):
  - `spawn_mixed`: `18.007 ms`
  - `query_physics`: `5.276 ms`
  - `component_churn`: `3.031 ms`
  - `despawn_all`: `2.435 ms`
  - `frame_step`: `11.403 ms`
- Why rejected:
  - Still slower on key workloads; rebuild/synchronization overhead outweighed benefits.

## Attempt C: Sparse-Set Style Internal Storage
- Idea:
  - Store entities by int id and maintain per-component pools (`values` + id sets).
  - Drive `find` from smallest required component pool.
- Result (median):
  - `spawn_mixed`: `20.260 ms` (`+53.5%`)
  - `query_physics`: `5.823 ms` (`+42.3%`)
  - `component_churn`: `4.982 ms` (`+81.5%`)
  - `despawn_all`: `6.825 ms` (`+285.2%`)
  - `frame_step`: `11.593 ms` (`-1.6%`)
- Why rejected:
  - One small gain in `frame_step`, but broad regressions elsewhere. Not a net win.

## Decision
- Reverted all three attempts.
- Kept stable implementation because it performed better overall for this benchmark profile.

## Next Candidate (not implemented yet)
- Archetype/chunk storage behind the same public API, with dedicated migration benchmarking.
