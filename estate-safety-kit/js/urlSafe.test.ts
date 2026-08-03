/**
 * Pins the scheme-allowlist boundary for `isSafeHttp`. A deny case that leaks through
 * here re-opens click-XSS on any `:href` bound from an untrusted-source URL; an allow
 * case that wrongly rejects moves the bug rather than fixing it (real links go dead).
 *
 * Ported from the two independent suites that pinned this behaviour before this file
 * was canonical: socioprophet app-vue's `url-safe.test.ts` (#477) and client-vue's
 * `urlSafe.test.ts` (#550). Written against Node's built-in test runner (`node:test`)
 * so this file has zero dependencies and runs the same way in any consumer, vitest or
 * not — `node --test js/urlSafe.test.ts` from this directory.
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { isSafeHttp } from './urlSafe.ts';

describe('isSafeHttp — scheme allowlist for untrusted-source URLs', () => {
  // ── ALLOW ──────────────────────────────────────────────────────────────────
  for (const [u, why] of [
    ['https://example.com/path', 'canonical https'],
    ['http://example.com/', 'plain http'],
    ['HTTPS://Example.com', 'mixed-case scheme'],
    ['https://example.com/x?y=1#z', 'with query + fragment'],
    ['http://user:pass@example.com/', 'with credentials in URL — still http scheme'],
    ['https://xn--nxasmq6b.example/', 'punycode host'],
    ['https://github.com/SocioProphet/prophet-platform', 'evidence-link host'],
  ] as const) {
    test(`allows ${u} (${why})`, () => {
      assert.equal(isSafeHttp(u), true);
    });
  }

  // ── DENY: dangerous schemes ────────────────────────────────────────────────
  for (const [u, why] of [
    ['javascript:alert(1)', 'javascript: — the classic click-XSS'],
    ['Javascript:alert(1)', 'javascript: mixed-case'],
    ['JAVASCRIPT:alert(1)', 'javascript: uppercase'],
    ['data:text/html,<script>alert(1)</script>', 'data: URLs execute HTML on some UAs'],
    ['vbscript:msgbox(1)', 'legacy IE surface, still handled by some UAs'],
    ['file:///etc/passwd', 'local file exfil surface'],
    ['ftp://example.com/', 'not-http — reject even if benign'],
    ['mailto:alice@example.com', 'not-http — a caller wanting mail must opt in'],
    ['tel:+1234', 'not-http — same rule'],
    ['about:blank', 'browser-internal scheme'],
    ['chrome-extension://abc/', 'extension scheme'],
    ['view-source:https://example.com', 'view-source wrapping'],
    ['blob:https://example.com/uuid', 'blob: — rendered content is caller-controlled'],
  ] as const) {
    test(`rejects ${u} (${why})`, () => {
      assert.equal(isSafeHttp(u), false);
    });
  }

  // ── DENY: browser normalisation traps ──────────────────────────────────────
  for (const [u, why] of [
    ['\tjavascript:alert(1)', 'leading tab historically stripped before scheme parse'],
    ['\njavascript:alert(1)', 'leading newline'],
    ['\rjavascript:alert(1)', 'leading CR'],
    [' javascript:alert(1)', 'leading space'],
  ] as const) {
    test(`rejects control-char-prefixed ${JSON.stringify(u)} (${why})`, () => {
      assert.equal(isSafeHttp(u), false);
    });
  }

  // ── DENY: no scheme / malformed ────────────────────────────────────────────
  for (const [u, why] of [
    ['', 'empty'],
    ['/relative/path', 'relative path — no scheme'],
    ['//example.com/foo', 'protocol-relative — deny (upstream may relative-resolve to javascript:)'],
    ['//evil.example/path', 'protocol-relative, arbitrary host'],
    ['example.com', 'bare host'],
    ['not a url', 'prose'],
    [':no-scheme', 'colon with no scheme'],
    ['1nvalid://x', 'scheme must start with a letter'],
  ] as const) {
    test(`rejects malformed ${JSON.stringify(u)} (${why})`, () => {
      assert.equal(isSafeHttp(u), false);
    });
  }

  // ── DENY: non-string ───────────────────────────────────────────────────────
  for (const [u, why] of [
    [null, 'null'],
    [undefined, 'undefined'],
    [42, 'number'],
    [{}, 'object'],
    [{ url: 'https://example.com' }, 'object with url — do not resolve'],
    [{ href: 'https://example.com' }, 'object with href — do not resolve'],
    [['https://example.com'], 'array'],
    [true, 'boolean'],
  ] as const) {
    test(`rejects non-string ${JSON.stringify(u)} (${why})`, () => {
      assert.equal(isSafeHttp(u as unknown as string), false);
    });
  }

  // ── extra allow-list — intersected with SAFE_EXTRAS ────────────────────────
  test('allows opt-in mailto/tel', () => {
    assert.equal(isSafeHttp('mailto:a@b', ['mailto']), true);
    assert.equal(isSafeHttp('tel:+1', ['tel']), true);
  });

  test('extras do not weaken the leading-control-char guard', () => {
    assert.equal(isSafeHttp('\tmailto:a@b', ['mailto']), false);
  });

  // ── ABSOLUTE deny — a caller cannot re-enable an executable scheme ─────────
  for (const [u, extras] of [
    ['javascript:alert(1)', ['javascript']],
    ['data:text/html,x', ['data']],
    ['vbscript:x', ['vbscript']],
    ['file:///etc/passwd', ['file']],
    ['blob:https://x/y', ['blob']],
    ['about:blank', ['about']],
    ['chrome-extension://x/', ['chrome-extension']],
    // multi-value extras attempting to smuggle a dangerous scheme past a benign one
    ['javascript:alert(1)', ['mailto', 'javascript']],
    // uppercase in extras must not bypass the SAFE_EXTRAS check
    ['javascript:alert(1)', ['JAVASCRIPT']],
  ] as const) {
    test(`a caller CANNOT re-enable ${u} by passing ${JSON.stringify(extras)} — deny-list is absolute`, () => {
      assert.equal(isSafeHttp(u, extras), false);
    });
  }

  test("extras are normalised — 'Mailto', 'MAILTO ', ' mailto' all opt in", () => {
    assert.equal(isSafeHttp('mailto:a@b', ['Mailto']), true);
    assert.equal(isSafeHttp('mailto:a@b', ['MAILTO ']), true);
    assert.equal(isSafeHttp('mailto:a@b', [' mailto']), true);
  });

  test('non-string entries in extras are ignored silently', () => {
    assert.equal(
      isSafeHttp('mailto:a@b', [null as unknown as string, undefined as unknown as string, 'mailto']),
      true,
    );
    assert.equal(isSafeHttp('javascript:x', [null as unknown as string, 'javascript' as unknown as string]), false);
  });
});
