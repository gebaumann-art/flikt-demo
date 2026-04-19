/**
 * Flikt.AI Demo — Cloudflare Worker
 *
 * Intercepts `flikt.ai/demo/*` at the Cloudflare edge and proxies to the
 * GitHub Pages site at gebaumann-art.github.io/flikt-demo/*.
 * Everything else passes through to the WordPress site at flikt.ai.
 *
 * Deploy via Cloudflare dashboard:
 *   1. Workers & Pages -> Create Worker -> paste this script -> Deploy
 *   2. Worker -> Triggers -> Add Route: `flikt.ai/demo*` -> select this Worker
 *   3. No DNS changes (flikt.ai already proxies through Cloudflare)
 *   4. No SSL changes (existing wildcard cert covers flikt.ai)
 */
export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Trailing-slash normalizer for bare /demo (so relative links resolve correctly)
    if (url.pathname === "/demo") {
      return Response.redirect(`${url.origin}/demo/`, 301);
    }

    // Proxy /demo/* -> gebaumann-art.github.io/flikt-demo/*
    if (url.pathname.startsWith("/demo/")) {
      const ghPath = url.pathname.replace(/^\/demo\//, "/flikt-demo/");
      const ghUrl = `https://gebaumann-art.github.io${ghPath}${url.search}`;

      // Forward headers but rewrite Host so GitHub Pages responds correctly
      const forwardHeaders = new Headers(request.headers);
      forwardHeaders.set("Host", "gebaumann-art.github.io");

      const ghResponse = await fetch(ghUrl, {
        method: request.method,
        headers: forwardHeaders,
        body: request.body,
        redirect: "follow",
      });

      // Pass the response back; Cloudflare's edge cache handles the rest
      const response = new Response(ghResponse.body, ghResponse);
      response.headers.set("X-Served-By", "flikt-demo-worker");
      return response;
    }

    // Everything else: pass through to the origin (WordPress at flikt.ai)
    return fetch(request);
  },
};
