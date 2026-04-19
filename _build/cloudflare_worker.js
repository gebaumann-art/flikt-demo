/**
 * Flikt.AI Demo — Cloudflare Worker
 *
 * Serves the demo portal from GitHub Pages under a Flikt.AI domain.
 *
 * Deployment modes supported:
 *
 *   A. Custom Domain on demo.flikt.ai (PRIMARY — current production):
 *      Worker bound as Custom Domain for demo.flikt.ai. Every path on
 *      that host proxies to gebaumann-art.github.io/flikt-demo/*.
 *
 *   B. Worker Route on flikt.ai/demo* (LEGACY — retained for safety):
 *      If anyone reattaches the zone-level route, `/demo/*` requests on
 *      the apex host still proxy correctly. Non-/demo apex traffic falls
 *      back to origin (WordPress).
 *
 * Deploy via Cloudflare dashboard:
 *   1. Workers & Pages -> Create Worker -> paste this script -> Deploy
 *   2. Worker -> Settings -> Domains & Routes -> Add -> Custom Domain
 *      -> demo.flikt.ai
 *   3. CF auto-creates the DNS record and provisions a cert.
 */
const GH_ORIGIN = "https://gebaumann-art.github.io";
const GH_BASE_PATH = "/flikt-demo";

async function proxyToGithubPages(request, pathname, search) {
  const ghUrl = `${GH_ORIGIN}${GH_BASE_PATH}${pathname}${search}`;
  const forwardHeaders = new Headers(request.headers);
  forwardHeaders.set("Host", "gebaumann-art.github.io");
  const ghResponse = await fetch(ghUrl, {
    method: request.method,
    headers: forwardHeaders,
    body: request.body,
    redirect: "follow",
  });
  const response = new Response(ghResponse.body, ghResponse);
  response.headers.set("X-Served-By", "flikt-demo-worker");
  return response;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const host = url.hostname.toLowerCase();

    // Mode A: demo.flikt.ai -> every path is a demo path.
    if (host === "demo.flikt.ai") {
      // Normalize bare / to /index.html via the GH base path (GH serves it).
      const pathname = url.pathname === "/" ? "/" : url.pathname;
      return proxyToGithubPages(request, pathname, url.search);
    }

    // Mode B (legacy): apex flikt.ai with /demo prefix.
    if (host === "flikt.ai" || host === "www.flikt.ai") {
      if (url.pathname === "/demo") {
        return Response.redirect(`https://demo.flikt.ai/`, 301);
      }
      if (url.pathname.startsWith("/demo/")) {
        const pathname = url.pathname.replace(/^\/demo\//, "/");
        return proxyToGithubPages(request, pathname, url.search);
      }
      // Non-/demo apex traffic: pass through to origin (WordPress).
      return fetch(request);
    }

    // Any other host that somehow hits this Worker: pass through.
    return fetch(request);
  },
};
