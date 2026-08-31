import fs from "node:fs";
import path from "node:path";

if (process.argv.includes("--help")) {
  console.log("Usage: node validate-agent-delivery.mjs [repository]");
  process.exit(0);
}

const repositoryRoot = path.resolve(process.argv[2] ?? process.cwd());
const canonicalSkillsRoot = path.join(repositoryRoot, ".agents", "skills");
const deliveredSkillsRoot = path.join(repositoryRoot, ".claude", "skills");

// Skip generated output, dependencies, caches, repository metadata, and skill roots while discovering instruction pairs.
const excludedDirectoryNames = new Set([
  ".agents",
  ".cache",
  ".claude",
  ".git",
  ".next",
  ".output",
  ".parcel-cache",
  ".swc",
  ".turbo",
  ".vercel",
  ".vite",
  "build",
  "coverage",
  "dist",
  "generated",
  "logs",
  "node_modules",
  "out",
  "storybook-static",
  "target",
  "tmp",
  "vendor",
]);

const failures = [];

function fail(message) {
  failures.push(message);
}

function displayPath(filePath) {
  return (path.relative(repositoryRoot, filePath) || ".").split(path.sep).join("/");
}

function inspectPath(filePath) {
  try {
    return fs.lstatSync(filePath);
  } catch (error) {
    if (error?.code !== "ENOENT" && error?.code !== "ENOTDIR") {
      fail(`${displayPath(filePath)}: cannot inspect path (${error.message})`);
    }
    return null;
  }
}

function readDirectory(directoryPath, description) {
  try {
    return fs.readdirSync(directoryPath, { withFileTypes: true });
  } catch (error) {
    fail(`${description} ${displayPath(directoryPath)}: cannot read directory (${error.message})`);
    return [];
  }
}

function assertReadable(filePath, description = displayPath(filePath)) {
  try {
    fs.accessSync(filePath, fs.constants.R_OK);
  } catch (error) {
    fail(`${description}: must be readable (${error.message})`);
  }
}

function resolvePath(filePath, description = displayPath(filePath)) {
  try {
    return fs.realpathSync(filePath);
  } catch (error) {
    fail(`${description}: cannot resolve path (${error.message})`);
    return null;
  }
}

function discoverInstructionDirectories() {
  const directories = [];

  function walk(directoryPath) {
    const entries = readDirectory(directoryPath, "Cannot scan");
    if (entries.some((entry) => entry.name === "AGENTS.md" || entry.name === "CLAUDE.md")) {
      directories.push(directoryPath);
    }

    for (const entry of entries) {
      if (!entry.isDirectory() || excludedDirectoryNames.has(entry.name)) continue;
      walk(path.join(directoryPath, entry.name));
    }
  }

  walk(repositoryRoot);
  return directories.sort((left, right) => left.localeCompare(right));
}

function validateInstructionDirectory(directoryPath) {
  const agentsPath = path.join(directoryPath, "AGENTS.md");
  const claudePath = path.join(directoryPath, "CLAUDE.md");
  const directoryLabel = displayPath(directoryPath);
  const agentsStat = inspectPath(agentsPath);
  const claudeStat = inspectPath(claudePath);
  let agentsResolved = null;
  let claudeResolved = null;

  if (!agentsStat) {
    fail(`${directoryLabel}: missing regular AGENTS.md`);
  } else if (agentsStat.isSymbolicLink() || !agentsStat.isFile()) {
    fail(`${displayPath(agentsPath)}: must be a regular file`);
  } else {
    assertReadable(agentsPath);
    agentsResolved = resolvePath(agentsPath);
  }

  if (!claudeStat) {
    fail(`${directoryLabel}: missing CLAUDE.md symlink to AGENTS.md`);
  } else if (!claudeStat.isSymbolicLink()) {
    fail(`${displayPath(claudePath)}: must be a relative symlink to AGENTS.md`);
  } else {
    const target = fs.readlinkSync(claudePath);
    if (path.isAbsolute(target) || target !== "AGENTS.md") {
      fail(`${displayPath(claudePath)}: expected target AGENTS.md, found ${target}`);
    }
    assertReadable(claudePath);
    claudeResolved = resolvePath(claudePath);
  }

  if (agentsResolved && claudeResolved && agentsResolved !== claudeResolved) {
    fail(`${directoryLabel}: AGENTS.md and CLAUDE.md resolve to different files`);
  }
}

function assertRealDirectory(directoryPath, description) {
  const stat = inspectPath(directoryPath);
  if (!stat) {
    fail(`${description} ${displayPath(directoryPath)}: directory is missing`);
    return false;
  }
  if (stat.isSymbolicLink() || !stat.isDirectory()) {
    fail(`${description} ${displayPath(directoryPath)}: must be a real directory`);
    return false;
  }
  assertReadable(directoryPath, `${description} ${displayPath(directoryPath)}`);
  return true;
}

function readSkillNames(directoryPath, description) {
  if (!assertRealDirectory(directoryPath, description)) return [];
  return readDirectory(directoryPath, "Cannot read skill root")
    .map((entry) => entry.name)
    .sort();
}

function validateCanonicalSkill(skillName) {
  const skillPath = path.join(canonicalSkillsRoot, skillName);
  if (!assertRealDirectory(skillPath, "Canonical skill")) return [];
  const files = [];

  function walk(directoryPath) {
    for (const entry of readDirectory(directoryPath, "Cannot read skill directory")) {
      const entryPath = path.join(directoryPath, entry.name);
      if (entry.isSymbolicLink()) {
        fail(`${displayPath(entryPath)}: canonical skill resources must not be symlinks`);
      } else if (entry.isDirectory()) {
        assertReadable(entryPath);
        walk(entryPath);
      } else if (entry.isFile()) {
        assertReadable(entryPath);
        resolvePath(entryPath);
        files.push(path.relative(skillPath, entryPath));
      } else {
        fail(`${displayPath(entryPath)}: canonical skill resource must be a regular file`);
      }
    }
  }

  walk(skillPath);
  if (!files.includes("SKILL.md")) fail(`${displayPath(skillPath)}: missing readable SKILL.md`);
  return files.sort();
}

function validateDeliveredSkill(skillName, canonicalFiles) {
  const canonicalPath = path.join(canonicalSkillsRoot, skillName);
  const deliveredPath = path.join(deliveredSkillsRoot, skillName);
  const expectedTarget = `../../.agents/skills/${skillName}`;
  const deliveredStat = inspectPath(deliveredPath);

  if (!deliveredStat) {
    fail(`${displayPath(deliveredPath)}: missing skill delivery symlink`);
    return 0;
  }
  if (!deliveredStat.isSymbolicLink()) {
    fail(`${displayPath(deliveredPath)}: must be a directory symlink`);
    return 0;
  }

  const target = fs.readlinkSync(deliveredPath);
  if (path.isAbsolute(target) || target !== expectedTarget) {
    fail(`${displayPath(deliveredPath)}: expected target ${expectedTarget}, found ${target}`);
  }

  const canonicalResolved = resolvePath(canonicalPath, `Canonical skill ${skillName}`);
  const deliveredResolved = resolvePath(deliveredPath, `Delivered skill ${skillName}`);
  if (canonicalResolved && deliveredResolved && canonicalResolved !== deliveredResolved) {
    fail(`${skillName}: delivered skill does not resolve to its canonical source`);
  }

  for (const relativeFile of canonicalFiles) {
    const canonicalFile = path.join(canonicalPath, relativeFile);
    const deliveredFile = path.join(deliveredPath, relativeFile);
    assertReadable(deliveredFile);
    const canonicalFileResolved = resolvePath(canonicalFile);
    const deliveredFileResolved = resolvePath(deliveredFile);
    if (canonicalFileResolved && deliveredFileResolved && canonicalFileResolved !== deliveredFileResolved) {
      fail(`${displayPath(deliveredFile)}: does not resolve to the canonical resource`);
    }
  }
  return canonicalFiles.length;
}

function validateSkillDelivery() {
  const canonicalExists = inspectPath(canonicalSkillsRoot);
  const deliveredExists = inspectPath(deliveredSkillsRoot);
  if (!canonicalExists && !deliveredExists) return { skillCount: 0, fileCount: 0 };

  const canonicalNames = readSkillNames(canonicalSkillsRoot, "Canonical skill root");
  const deliveredNames = readSkillNames(deliveredSkillsRoot, "Delivered skill root");
  const canonicalOnly = canonicalNames.filter((name) => !deliveredNames.includes(name));
  const deliveredOnly = deliveredNames.filter((name) => !canonicalNames.includes(name));
  if (canonicalOnly.length || deliveredOnly.length) {
    fail(`Skill name sets differ (canonical only: ${canonicalOnly.join(", ") || "none"}; delivery only: ${deliveredOnly.join(", ") || "none"})`);
  }

  let fileCount = 0;
  for (const skillName of [...new Set([...canonicalNames, ...deliveredNames])].sort()) {
    fileCount += validateDeliveredSkill(skillName, validateCanonicalSkill(skillName));
  }
  return { skillCount: canonicalNames.length, fileCount };
}

const rootStat = inspectPath(repositoryRoot);
if (!rootStat || !rootStat.isDirectory()) {
  fail(`Target ${repositoryRoot}: must be a readable repository directory`);
} else {
  assertReadable(repositoryRoot, `Target ${repositoryRoot}`);
}

const instructionDirectories = rootStat?.isDirectory() ? discoverInstructionDirectories() : [];
if (!instructionDirectories.length) fail("No repository instruction pairs found");
for (const directoryPath of instructionDirectories) validateInstructionDirectory(directoryPath);
const { skillCount, fileCount } = rootStat?.isDirectory()
  ? validateSkillDelivery()
  : { skillCount: 0, fileCount: 0 };

if (failures.length) {
  console.error(`Agent delivery validation failed for ${repositoryRoot} with ${failures.length} issue${failures.length === 1 ? "" : "s"}:`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exitCode = 1;
} else {
  console.log(`Agent delivery validation passed for ${repositoryRoot}: ${instructionDirectories.length} instruction pairs, ${skillCount} skills, ${fileCount} canonical skill files checked.`);
}
