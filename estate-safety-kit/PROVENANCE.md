# estate-safety-kit — canonical source + vendoring contract

Three small, security-relevant helpers that were each written correctly, then written
*again* — independently, with no code sharing — somewhere else in the estate, because
there was no shared home for cross-repo, cross-language "closes a real defect class"
code. This directory is that home. The estate's answer to "how do we share trust-
sensitive code across repos" is **not** a package registry — it is the same disciplined
vendoring pattern already used for the hellgraph engine tarball
(`prophet-platform/tools/revendor_engine.py` +
`tools/assert_vendored_engine_marker.py`) and for vendored schema sets
(`apps/compute-gateway/src/compute_gateway/schemas/PROVENANCE.md`): **one canonical
source, verbatim copies at consumers, a recorded commit pin, and a checker that proves
byte-identity instead of trusting a comment.**

## The three helpers

| file | closes | first written | duplicated / re-derived |
|---|---|---|---|
| `js/urlSafe.ts` | click-XSS via an unsanitised `:href` scheme (`javascript:`, `data:`, `vbscript:`, …) bound from an upstream-controlled URL | `socioprophet-web/app-vue/src/services/url-safe.ts` — [socioprophet#477](https://github.com/SocioProphet/socioprophet/pull/477) | copy-pasted (not imported — app-vue and client-vue don't share a workspace) into `socioprophet-web/client-vue/src/utils/urlSafe.ts` — [socioprophet#550](https://github.com/SocioProphet/socioprophet/pull/550) |
| `js/mintId.ts` | id-collision from minting an identifier as `hash(inputs + Date.now())` — collides same-millisecond, and is offline-recomputable from anything that publishes the inputs | `apps/health-twin/src/ids.ts` (`mintId`) — [prophet-platform#1070](https://github.com/SocioProphet/prophet-platform/pull/1070), fixing the exact same shape independently found in both a grant-id mint and `consult.ts`'s three id sites | the same PATTERN (not the code — nobody shared it) had to be independently re-derived for `bootProofRecord` in socioprophet's server contracts — [socioprophet#484](https://github.com/SocioProphet/socioprophet/pull/484) |
| `py/bounded_int.py` | "must be a non-negative int" treated as a size bound, when Python ints are arbitrary-precision — a digit-encoded blob smuggles arbitrary payload through a field typed only by sign | `apps/compute-gateway/src/compute_gateway/engine.py`'s exhaust guard — introduced [prophet-platform#1067](https://github.com/SocioProphet/prophet-platform/pull/1067), the open door found in [#1071](https://github.com/SocioProphet/prophet-platform/pull/1071), the int64 bound closing it in [#1118](https://github.com/SocioProphet/prophet-platform/pull/1118) | never generalized even to the sibling app `nugget-extractor` in the *same* repo, which independently grew its own, differently-shaped, pending-cap fix for a related-but-distinct DoS class (`apps/nugget-extractor/tests/test_pending_cap.py`) |

Adjacent context, not the same specific defect but the same session's broader
socioprophet-web XSS/security-hardening sweep that this duplication was found inside of:
[socioprophet#478](https://github.com/SocioProphet/socioprophet/pull/478) (v-html
sanitization on notebook cell output), [#483](https://github.com/SocioProphet/socioprophet/pull/483)
(mesh bearer token moved out of localStorage), [#486](https://github.com/SocioProphet/socioprophet/pull/486)
(six low-severity cockpit findings). None of these three duplicate `isSafeHttp` /
`mintId` / bounded-int — they're cited here only because the pattern that produced this
kit ("fixed the same bug shape more than once, in more than one repo, because there was
nowhere to put the fix once") was noticed while working through that same sweep.

## Why vendoring, not an npm package / PyPI package

This estate has explicitly avoided adding new package-registry surfaces for
cross-repo-shared code (`feedback_vendor_dont_reference_external_cdn.md`,
`feedback_sovereign_decoupled_no_bloat.md`): a private registry is a new supply-chain
surface, a new publish pipeline, and a new versioning burden, for three files. The
existing convention for exactly this shape of problem — the hellgraph engine tarball,
the zero-trust kernel schemas above — is **vendor with a provenance record and a
freshness check**, so that's what this is.

## The vendoring contract

A consumer that wants one of these helpers:

1. **Copies the file verbatim** into its own tree (e.g.
   `socioprophet-web/app-vue/src/services/url-safe.ts`). No edits — if the helper needs
   to change for that consumer, that is a signal the canonical source needs to change
   (open a PR here, or generalize the API — see `mintId(prefix, bytes)`'s width
   parameter for how the kit already accommodates one real divergence, health-twin's
   stricter 64-hex ratchet, without forking the file).
2. **Records a `PROVENANCE.txt`** alongside the vendored file:
   ```
   source-repo: SourceOS-Linux/sourceos-spec
   source-path: estate-safety-kit/js/urlSafe.ts
   source-commit: <full 40-hex commit SHA this copy was taken from>
   vendored-path: socioprophet-web/app-vue/src/services/url-safe.ts
   vendored-at: <date>
   ```
3. **Runs `tools/check_vendored_safety_kit.py`** (in CI, and locally before a re-vendor
   PR) against the vendored file. It reads the `PROVENANCE.txt`, fetches the canonical
   file at the pinned commit (from `raw.githubusercontent.com`, or from a local
   `--source-root` checkout for offline/dev use), and fails loudly on any byte
   difference — the same "prove it, don't just claim it" discipline as
   `assert_vendored_engine_marker.py`, applied to a small source file instead of a
   tarball member (byte comparison instead of marker-substring containment, because a
   file this size can be diffed exactly).

## Re-vendoring (canonical source changed)

1. Land the change here, get it merged to `main`.
2. For each consumer: copy the updated file, update `source-commit` in its
   `PROVENANCE.txt` to the new merge commit, re-run
   `tools/check_vendored_safety_kit.py` to confirm the copy is byte-identical again.
3. Consumers are NOT required to re-vendor in lockstep — an out-of-date pin is visible
   (the checker still passes against the *old* pinned commit; it does not silently claim
   currency with `main`) rather than invisible, which is the property that matters. A
   freshness sweep across consumers is a separate, later concern (see
   `feedback_vendored_dist_freshness.md`), not blocking on this PR.

## Status of this PR

New shared-infrastructure pattern — held for human review of the vendoring convention
itself, not just the code inside it (the three defects it closes are already fixed
independently at every site listed above; this PR does not change behavior anywhere
except socioprophet's two consumers being re-pointed to vendored copies of the same
logic they already ran).
