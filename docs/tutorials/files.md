# File Operations

Simple tools for downloading, reading, and writing files.

## Download Files

```python
from trion.tools.web.download import download

# Download from URL
download("https://example.com/paper.pdf", "downloads/paper.pdf")

# Directories created automatically
download("https://data.gov/dataset.csv", "data/2024/dataset.csv")
```

## Read Files

```python
from trion.tools.document.read import read

# Read text file
content = read("document.txt")

# Read markdown
notes = read("notes.md")

# Read JSON
data = read("config.json")
```

## Write Files

```python
from trion.tools.document.write import write

# Write text
write("Hello World", "output.txt")

# Write markdown
write("# Title\n\nContent here", "document.md")

# Write JSON
write('{"key": "value"}', "data.json")
```

## Common Workflows

### Download and Extract

```python
from trion.tools.web.download import download
from trion.tools.document.ocr import read as ocr_read
from trion.tools.document.write import write

# Download PDF
download("https://example.com/paper.pdf", "papers/paper.pdf")

# Extract text
text = ocr_read("papers/paper.pdf")

# Save as markdown
write(text, "papers/paper.md")
```

### Read, Process, Write

```python
from trion.tools.document.read import read
from trion.tools.document.write import write

# Read
content = read("input.txt")

# Process
processed = content.upper()

# Write
write(processed, "output.txt")
```

### Save Search Results

```python
from trion.tools.research.articles import query
from trion.tools.document.write import write
import json

# Search papers
papers = query(keywords="CRISPR")

# Export to JSON
data = papers.to_dict(orient='records')
write(json.dumps(data, indent=2), "papers.json")
```

## Using with Agents

```python
from trion.agents.core import agent
from trion.tools.web.download import download_file
from trion.tools.document.read import read_file
from trion.tools.document.write import write_file

# Create agents
dl = agent(download_file, llm_type="function_calling")
reader = agent(read_file, llm_type="function_calling")
writer = agent(write_file, llm_type="function_calling")

# Natural language
dl.call("Download https://example.com/file.pdf to downloads/file.pdf")
content = reader.call("Read document.txt")
writer.call("Write Hello World to output.txt")
```

## Features

**Download:**
- Automatic directory creation
- Stream downloads (memory efficient)
- Timeout support

**Read:**
- All text formats
- UTF-8 encoding
- Error handling

**Write:**
- Any extension (.txt, .md, .json, .csv, etc.)
- Creates parent directories
- Returns absolute path

Simple.
