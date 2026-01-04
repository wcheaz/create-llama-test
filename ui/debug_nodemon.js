// Debug script to check working directory and paths
console.log("=== Nodemon Debug Information ===");
console.log("Current working directory:", process.cwd());
console.log("Script directory:", __dirname);
console.log("Script path:", __filename);

// Check if the tsx CLI exists
const fs = require('fs');
const tsxPath = "node_modules/.pnpm/tsx@4.21.0/node_modules/tsx/dist/cli.mjs";
console.log("TSX path exists:", fs.existsSync(tsxPath));

// Try to resolve the path
try {
  const resolvedPath = require.resolve(tsxPath);
  console.log("Resolved TSX path:", resolvedPath);
} catch (e) {
  console.error("Failed to resolve TSX path:", e.message);
}

// Check if index.ts exists
const indexPath = "./index.ts";
console.log("Index.ts exists:", fs.existsSync(indexPath));

// List directory contents
try {
  const files = fs.readdirSync(".");
  console.log("Directory contents:", files);
} catch (e) {
  console.error("Failed to read directory:", e.message);
}