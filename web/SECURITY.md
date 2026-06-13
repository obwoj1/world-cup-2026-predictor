# Security notes — web app

## Dependency audit (last reviewed 2026-06-13)

`npm audit` flags advisories against `next` and `postcss`. Status and reasoning:

- **Next.js** is pinned to the latest `14.2.x` patch (currently 14.2.35), which clears the
  prior **critical** cache-poisoning advisory. The remaining advisories (Image Optimizer
  DoS, middleware/rewrite/proxy issues, Server Actions DoS, dev-server origin, SSRF via
  WebSocket upgrades, RSC cache poisoning) all require **runtime features this app does not
  use**. Every route is statically prerendered (`○ Static` in the build output): there is no
  middleware, no `next/image` optimizer, no rewrites, no Server Actions, and no SSR request
  handling in production. These vectors are therefore not exploitable in our deployment.
  They are only fully resolved in Next 15.x; a major upgrade is deferred as low-value for a
  static site.
- **postcss** advisory is a build-time CSS-stringify XSS that does not affect the shipped
  static output.

This app reads only local, committed JSON (no user input, no auth, no database, no secrets),
which further limits the attack surface.

Re-run `npm audit` after each dependency bump and update this note.
