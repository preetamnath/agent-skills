#!/usr/bin/env bash
# Validate every skill manifest before commit.
# Catches the class of bug that made `handoff` un-installable: a SKILL.md
# whose YAML frontmatter fails to parse (e.g. an unquoted description
# containing ": "), or is missing name/description, or whose name does not
# match its folder (the installer keys off `name`).
#
# Usage:  scripts/validate-skills.sh
# Exit 0 = all valid, non-zero = at least one manifest is broken.
set -euo pipefail

cd "$(dirname "$0")/.."

ruby -ryaml -e '
fails = 0
files = Dir.glob("skills/*/SKILL.md").sort
files.each do |f|
  txt = File.read(f)
  unless txt.start_with?("---")
    puts "FAIL #{f}: missing YAML frontmatter (must start with ---)"; fails += 1; next
  end
  parts = txt.split(/^---\s*$/, 3)
  begin
    d = YAML.load(parts[1])
  rescue => e
    puts "FAIL #{f}: YAML parse error -> #{e.message.lines.first.strip}"
    puts "       (tip: quote the value, e.g. description: \"...\", if it contains a colon)"
    fails += 1; next
  end
  unless d.is_a?(Hash)
    puts "FAIL #{f}: frontmatter is not a key:value mapping"; fails += 1; next
  end
  miss = []
  miss << "name" unless d["name"].is_a?(String) && !d["name"].strip.empty?
  miss << "description" unless d["description"].is_a?(String) && !d["description"].strip.empty?
  unless miss.empty?
    puts "FAIL #{f}: missing/empty #{miss.join(", ")}"; fails += 1; next
  end
  folder = File.basename(File.dirname(f))
  if d["name"] != folder
    puts "FAIL #{f}: name \"#{d["name"]}\" does not match folder \"#{folder}\""; fails += 1; next
  end
end

if fails.zero?
  puts "OK: #{files.size} skill manifests valid"
  exit 0
else
  puts "#{fails} skill manifest(s) failed validation"
  exit 1
end
'
