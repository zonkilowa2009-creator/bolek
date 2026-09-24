// Prosty serwer statyczny dla folderu strony/ (bez zależności). Użycie: node narzedzia/skrypty/serwer.mjs [port]
import http from "node:http"; import fs from "node:fs"; import path from "node:path";
const root = path.resolve("strony"), port = +process.argv[2] || 5173;
const types = {".html":"text/html; charset=utf-8",".css":"text/css",".js":"text/javascript",".mjs":"text/javascript",".json":"application/json",".svg":"image/svg+xml",".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp",".gif":"image/gif",".mp4":"video/mp4",".webm":"video/webm",".woff2":"font/woff2",".ico":"image/x-icon"};
http.createServer((req, res) => {
  let p = path.join(root, decodeURIComponent(req.url.split("?")[0]));
  if (!p.startsWith(root)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, "index.html");
  fs.readFile(p, (e, d) => {
    if (e) { res.writeHead(404).end("404"); return; }
    res.writeHead(200, {"Content-Type": types[path.extname(p).toLowerCase()] || "application/octet-stream", "Cache-Control": "no-store"}).end(d);
  });
}).listen(port, () => console.log(`strony/ -> http://localhost:${port}`));
