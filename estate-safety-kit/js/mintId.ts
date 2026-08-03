/**
 * ONE decision about where an identifier comes from, for every ledger that mints one.
 *
 * ESTATE SAFETY KIT — canonical source. See ../PROVENANCE.md for what this closes,
 * which repos hit the defect independently, and the vendoring contract every consumer
 * must follow. Do not edit a vendored copy directly — edit this file, re-vendor, done.
 *
 * THE DEFECT, found independently at least twice in prophet-platform's health-twin
 * before this file existed: a grant id minted as `grant-<sha256(agent|scope|Date.now())>`
 * and a consult id minted as `consult-<sha256(pseudonym|scope|Date.now()-scope)>`. Both are
 * a HASH OF THEIR OWN INPUTS, and both inherit two properties from that:
 *
 *   1. THEY COLLIDE. The only varying input is a millisecond. Two records minted with the
 *      same logical inputs in the same millisecond get the SAME id — measured at 79% of
 *      200 concurrent issues on a laptop, for the grant case. A collided id is not a
 *      cosmetic duplicate: the ledger holds two rows under one identity, lookup silently
 *      resolves to one of them, the other holder's secret stops authenticating with no
 *      error anyone can point at, revoking the id revokes one row and leaves the other,
 *      and every receipt naming that id is ambiguous about which record it sealed.
 *
 *   2. THEY ARE RECOMPUTABLE OFFLINE. If the inputs and a millisecond-precision timestamp
 *      are ever published beside the id (a natural thing to do — `granted_at` on a grant,
 *      say), anyone holding that listing can recompute every id in it. The id is then an
 *      offline guessing target handed out for free, which matters most when the id is also
 *      the input to revocation or lookup.
 *
 * THE DECISION: an identifier is MINTED, not DERIVED. Bytes straight from the CSPRNG, hex,
 * behind a human-readable typed prefix. Nothing about the record is recoverable from the
 * id, nothing about the id is predictable from the record, and the collision probability
 * over any ledger this helper could serve is not a number worth writing down.
 *
 * WHY NOT sha256(inputs + a random nonce), the other obvious repair: the moment a random
 * nonce is inside the hash, the output IS random — the deterministic inputs contribute
 * nothing an attacker cannot already see, and the hash contributes nothing but the
 * appearance of derivation. It reads like a content address and is not one. Minting the
 * bytes directly says what is actually happening.
 *
 * WHAT AN ID IS NOT. It is not a content address and it is not a receipt — those stay a
 * hash over their own canonical, sealed content, because their entire job IS to be
 * recomputable from the facts they seal. An id and a receipt are two different things that
 * happen to both be hex strings.
 *
 * WIDTH. Default is 16 bytes (128 bits) — ample collision resistance for any per-service
 * ledger, minted with `randomBytes`, not a UUID library (no extra dependency, same CSPRNG
 * underneath). A caller with a stricter estate-wide ratchet — health-twin's is "no id ends
 * in an 8-hex digest, all of them carry a full 64 hex", to keep every emitted id
 * indistinguishable in shape from a sha256 digest — passes `bytes: 32` to mint the same
 * shape it already emits; the floor below refuses anything under 128 bits so a caller
 * cannot accidentally weaken it to something guessable.
 */
import { randomBytes } from 'node:crypto';

/** Minimum width this helper will mint. Below 128 bits is not "smaller ids", it is a
 * different security property — refuse it here rather than let a caller discover the
 * difference empirically. */
export const MIN_ID_BYTES = 16;

/**
 * Mint a fresh, content-independent identifier: `<prefix>-<CSPRNG bytes as hex>`.
 *
 * @param prefix human-readable, lowercase-and-hyphen typed prefix (`grant`, `consult`, `op`).
 * @param bytes  CSPRNG bytes to mint, default 16 (128 bits). Must be >= {@link MIN_ID_BYTES}.
 */
export function mintId(prefix: string, bytes: number = MIN_ID_BYTES): string {
  if (typeof prefix !== 'string' || prefix.length === 0) {
    throw new TypeError(`mintId: prefix must be a non-empty string (got ${JSON.stringify(prefix)})`);
  }
  if (!Number.isInteger(bytes) || bytes < MIN_ID_BYTES) {
    throw new RangeError(`mintId: bytes must be an integer >= ${MIN_ID_BYTES} (got ${bytes})`);
  }
  return `${prefix}-${randomBytes(bytes).toString('hex')}`;
}

/** Build the shape-check pattern `mintId` guarantees for a given prefix and width, so an
 * invariant can check "is this string actually one of ours" without hardcoding hex length
 * in two places. Matches a LOWERCASE prefix followed by `-` and `2*bytes` lowercase hex
 * digits — the same shape `mintId` produces, nothing looser. */
export function idPattern(prefix: string, bytes: number = MIN_ID_BYTES): RegExp {
  const hexLen = bytes * 2;
  const escapedPrefix = prefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`^${escapedPrefix}-[0-9a-f]{${hexLen}}$`);
}
