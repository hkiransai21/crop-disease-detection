const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const root = path.resolve(__dirname, "../dist");
const files = [
  "/",
  "/index.html",
  "/manifest.webmanifest",
  "/icon.svg",
  ...fs.readdirSync(path.join(root, "assets")).map((name) => "/assets/" + name),
];
const version = crypto
  .createHash("sha256")
  .update(files.join("|") + fs.readFileSync(path.join(root, "index.html")))
  .digest("hex")
  .slice(0, 16);
fs.writeFileSync(
  path.join(root, "precache.js"),
  `self.APP_VERSION=${JSON.stringify(version)}; self.APP_FILES=${JSON.stringify(files)};`,
);
console.log(
  `Offline app shell: ${files.length} files, revision ${version}. Audio remains opt-in.`,
);
