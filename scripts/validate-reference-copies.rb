# frozen_string_literal: true

root = ARGV[0] ? File.expand_path(ARGV[0]) : File.expand_path("..", __dir__)
fragment_open = /^<!-- fragment: ([a-z0-9][a-z0-9-]*) -->$/
source_open = /^(\s*)<!-- source: (references\/[^#\s]+)#([a-z0-9][a-z0-9-]*) -->$/
errors = []
fragments = {}

Dir.glob(File.join(root, "references", "*.md")).sort.each do |path|
  lines = File.readlines(path, chomp: true)
  relative = path.delete_prefix("#{root}/")
  index = 0

  while index < lines.length
    line = lines[index]
    match = fragment_open.match(line)
    if line.include?("<!-- fragment:") && !match
      errors << "#{relative}:#{index + 1}: malformed fragment marker"
      index += 1
      next
    end
    if line.include?("<!-- /fragment:")
      errors << "#{relative}:#{index + 1}: orphan fragment closing marker"
      index += 1
      next
    end
    unless match
      index += 1
      next
    end

    fragment = match[1]
    closing = "<!-- /fragment: #{fragment} -->"
    close_index = ((index + 1)...lines.length).find { |candidate| lines[candidate] == closing }
    unless close_index
      errors << "#{relative}: missing #{closing}"
      break
    end

    key = [relative, fragment]
    if fragments.key?(key)
      errors << "#{relative}: duplicate fragment #{fragment}"
    else
      fragments[key] = lines[(index + 1)...close_index].join("\n")
    end
    index = close_index + 1
  end
end

consumer_count = 0
used_fragments = Hash.new(0)

Dir.glob(File.join(root, "{skills,agents}", "**", "*.md")).sort.each do |path|
  lines = File.readlines(path, chomp: true)
  relative = path.delete_prefix("#{root}/")
  index = 0

  while index < lines.length
    line = lines[index]
    match = source_open.match(line)
    if line.include?("<!-- source:") && !match
      errors << "#{relative}:#{index + 1}: malformed source marker"
      index += 1
      next
    end
    if line.include?("<!-- /source:")
      errors << "#{relative}:#{index + 1}: orphan source closing marker"
      index += 1
      next
    end
    unless match
      index += 1
      next
    end

    indent, source, fragment = match.captures
    closing = "#{indent}<!-- /source: #{source}##{fragment} -->"
    close_index = ((index + 1)...lines.length).find { |candidate| lines[candidate] == closing }
    unless close_index
      errors << "#{relative}:#{index + 1}: missing #{closing.strip}"
      break
    end

    key = [source, fragment]
    expected = fragments[key]
    if expected.nil?
      errors << "#{relative}:#{index + 1}: unknown source fragment #{source}##{fragment}"
    else
      copied_lines = lines[(index + 1)...close_index]
      bad_indent = copied_lines.find_index { |copied| !copied.empty? && !copied.start_with?(indent) }
      if bad_indent
        errors << "#{relative}:#{index + bad_indent + 2}: copied line escapes marker indentation"
      else
        actual = copied_lines.map { |copied| copied.empty? ? copied : copied.delete_prefix(indent) }.join("\n")
        errors << "#{relative}:#{index + 1}: drift from #{source}##{fragment}" unless actual == expected
      end
      used_fragments[key] += 1
    end

    consumer_count += 1
    index = close_index + 1
  end
end

fragments.each_key do |source, fragment|
  errors << "#{source}: fragment #{fragment} has no consumer" if used_fragments[[source, fragment]].zero?
end

if errors.empty?
  puts "OK: #{consumer_count} reference copies match #{fragments.size} source fragments"
  exit 0
end

errors.each { |error| warn "FAIL #{error}" }
exit 1
