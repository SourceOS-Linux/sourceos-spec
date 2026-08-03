# Surface feeds — wiring surfaces to live state

Each Tier-2 surface reads `./data/<name>.json` at load (or `window.SURFACE_FEED_URL`
if the shell injects a live endpoint), falls back to its embedded seed if the fetch
fails, and shows a **LIVE / SAMPLE** badge so it never lies about what it's displaying.

| Surface | feed | required keys |
|---|---|---|
| `b11-life-mirror.html` | `b11.json` | `spaces`, `tripwires`, `transitions` (+ `state`) |
| `e11-consent-receipts.html` | `e11.json` | `surfaces`, `receipts`, `governor` |
| `turn-witness.html` | `turn-witness.json` | `turns` |

## Regenerate from real state
```
python3 tools/build_surface_feed.py --surface e11 --input <runtime-payload>.json   # → provenance=live
python3 tools/build_surface_feed.py --surface b11                                   # re-stamp sample
```
The runtime producer (netwatch snapshot, consent-plane catalog, receipt stream,
App-Intents parser) writes the payload; `build_surface_feed.py` validates the shape,
stamps `provenance` + `generated_at`, and emits the feed. Until a live endpoint is
wired, the committed `*.json` are seeds (`provenance: "sample"`) and the badge says so.
