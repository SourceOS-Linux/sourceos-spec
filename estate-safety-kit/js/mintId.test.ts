/**
 * Pins the property `mintId` exists to guarantee — collision-free minting, not
 * derivation from inputs — plus the shape and floor invariants. The regression this
 * guards against (`hash(inputs + Date.now())` colliding same-millisecond) is exactly
 * what "50 calls with identical inputs in a tight loop -> 50 unique ids" below would
 * have caught in health-twin's consult.ts before it was fixed.
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { mintId, idPattern, MIN_ID_BYTES } from './mintId.ts';

describe('mintId — CSPRNG id minting', () => {
  test('default width is 128 bits (32 hex chars) behind the prefix', () => {
    const id = mintId('grant');
    assert.match(id, /^grant-[0-9a-f]{32}$/);
  });

  test('is content-independent — identical prefix, called back-to-back, never repeats', () => {
    // This is the exact regression: the old scheme was a hash of its own inputs, so
    // identical logical inputs in the same millisecond minted the SAME id. mintId takes
    // no content input at all, so "identical inputs" isn't even expressible here — the
    // property under test is that N calls with the SAME prefix in a tight loop are N
    // unique ids, which is what the old scheme failed at 79% of the time under load.
    const n = 2000;
    const ids = new Set<string>();
    for (let i = 0; i < n; i++) ids.add(mintId('consult'));
    assert.equal(ids.size, n, 'every mint in a tight loop must be unique — this is the collision defect');
  });

  test('respects a wider width for callers with a stricter ratchet (health-twin: 32 bytes / 64 hex)', () => {
    const id = mintId('op', 32);
    assert.match(id, /^op-[0-9a-f]{64}$/);
  });

  test('refuses a width below the 128-bit floor', () => {
    assert.throws(() => mintId('x', 4), RangeError);
    assert.throws(() => mintId('x', 15), RangeError);
    assert.doesNotThrow(() => mintId('x', MIN_ID_BYTES));
  });

  test('refuses a non-integer width', () => {
    assert.throws(() => mintId('x', 16.5), RangeError);
    assert.throws(() => mintId('x', NaN), RangeError);
  });

  test('refuses an empty or non-string prefix', () => {
    assert.throws(() => mintId(''), TypeError);
    assert.throws(() => mintId(null as unknown as string), TypeError);
    assert.throws(() => mintId(undefined as unknown as string), TypeError);
  });

  test('id is lowercase hex — no uppercase, no non-hex characters', () => {
    const id = mintId('more');
    const [, hex] = id.split('-');
    assert.equal(hex, hex.toLowerCase());
    assert.match(hex, /^[0-9a-f]+$/);
  });
});

describe('idPattern — shape-check builder', () => {
  test('matches what mintId actually produces, for the default width', () => {
    const pattern = idPattern('grant');
    assert.match(mintId('grant'), pattern);
  });

  test('matches what mintId actually produces, for a non-default width', () => {
    const pattern = idPattern('op', 32);
    assert.match(mintId('op', 32), pattern);
  });

  test('does not match a narrower or wider id than the width it was built for', () => {
    const pattern = idPattern('grant', 32); // expects 64 hex chars
    assert.doesNotMatch(mintId('grant'), pattern); // mintId('grant') defaults to 32 hex chars
  });

  test('does not match a different prefix', () => {
    const pattern = idPattern('grant');
    assert.doesNotMatch(mintId('consult'), pattern);
  });

  test('escapes regex metacharacters in the prefix rather than interpreting them', () => {
    const pattern = idPattern('a.b');
    assert.doesNotMatch('aXb-' + '0'.repeat(32), pattern);
    assert.match('a.b-' + '0'.repeat(32), pattern);
  });
});
