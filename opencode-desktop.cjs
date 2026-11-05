// Adds opencode-desktop.json to OpenCode Desktop's theme list. The app bundles
// its themes at build time and has no folder for custom ones, so this adds the
// theme to the app's script as it's served, leaving the installed files alone.
// Electron preloads it from ~/.config/electron44-flags.conf (see README.md).
"use strict"

const APP = "/usr/lib/opencode-desktop"
const SCRIPT = /^\/assets\/main-[^/]+\.js$/
const ANCHOR = '"./themes/amoled.json":'

if (process.argv.includes(APP)) {
  const { protocol } = require("electron")
  const { readFileSync } = require("node:fs")
  const { join } = require("node:path")

  const theme = JSON.parse(readFileSync(join(__dirname, "opencode-desktop.json"), "utf8"))
  const entry = `"./themes/${theme.id}.json":()=>Promise.resolve({default:${JSON.stringify(theme)}}),`
  const handle = protocol.handle

  protocol.handle = function (scheme, handler) {
    if (scheme !== "oc") return handle.call(this, scheme, handler)

    return handle.call(this, scheme, async (request) => {
      const response = await handler(request)
      if (!response.ok || !SCRIPT.test(new URL(request.url).pathname)) return response

      const source = await response.text()
      const at = source.indexOf(ANCHOR)
      // A later release may lay this out differently. The app then runs stock
      // and falls back to its default theme.
      if (at < 0) console.warn("ono-sendai: theme list not found; theme not added")
      const body = at < 0 ? source : source.slice(0, at) + entry + source.slice(at)
      const headers = new Headers(response.headers)
      headers.delete("content-length")

      return new Response(body, { status: response.status, statusText: response.statusText, headers })
    })
  }
}
