# SourceOS Browser Write Accountability v0.1

## Purpose

This contract specializes SourceOS Mutation and Evidence Accountability for browser write-pressure incidents.

The Firefox evidence from the macOS investigation showed repeated SQLite-backed profile/storage writes, but a later Add-ons Manager screenshot showed no visible installed extensions. That correction matters: extension-driven write amplification must be downgraded unless an extension inventory actually supports it.

## Decision

Browser write-pressure receipts must distinguish user-installed extension storage from browser-core profile state, per-origin storage, service-worker/cache state, session restore, browser sync, downloads/cache, diagnostics, and profile repair or migration.

A browser write-pressure incident must not blame extensions merely because the browser wrote heavily.

## Required actor classes

- `browser_profile_core`
- `browser_history_places`
- `browser_favicons`
- `browser_cookies_permissions`
- `browser_session_restore`
- `browser_origin_storage`
- `browser_service_worker_cache`
- `browser_download_cache`
- `browser_sync_state`
- `browser_extension_storage`
- `browser_hidden_system_addon`
- `browser_diagnostics`
- `browser_profile_repair_or_migration`
- `unknown`

## Extension inventory states

- `none_visible`: no user-installed extensions visible in the ordinary extension manager view.
- `installed`: visible user-installed extensions exist.
- `hidden_possible`: system, policy, hidden, or native-messaging add-ons may exist but were not fully enumerated.
- `unavailable`: the extension inventory could not be collected.
- `not_collected`: no extension inventory evidence was captured.

## Normative rule

If `extension_inventory_state=none_visible`, then `browser_extension_storage` must not be used as the primary actor class unless additional hidden/system/policy add-on evidence is attached.

## Evidence-quality rule

A complete browser-write receipt requires at minimum:

- Browser/version/profile identifier.
- Actor class.
- Extension inventory state.
- Operation class.
- Object class and path class.
- Byte count or write-pressure budget.
- Evidence-quality status and missing fields.

A report with only process name, stack offsets, and syscall class is partial evidence.

## Design consequence

SourceOS/BearBrowser must expose browser storage accountability by profile component and origin. The user should see whether writes came from core profile state, site/origin storage, service workers, downloads/cache, sync state, extensions, diagnostics, or migration/repair logic.
