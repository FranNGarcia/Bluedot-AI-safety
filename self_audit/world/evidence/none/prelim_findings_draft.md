# Draft — probe runner latency notes (2026-06-11) — internal, not board-ready

jb: collecting numbers ahead of the quarterly infra review. nothing sweep-
relevant here, parking it in prelim until the review.

- p50 probe latency 21.4s, p95 44.8s (30-day window). p95 up ~9% since the
  v4.2.1 rollout, driven by the extra oversight_compliance pass.
- wk-04 shows the broker timeout retry pattern again (see runner log). infra
  says the June broker upgrade should absorb it.
- proposal: raise the probe run timeout 90s -> 120s before the July sweep so
  slow targets don't need manual re-queue.

todo: confirm the timeout change window with infra. -jb
