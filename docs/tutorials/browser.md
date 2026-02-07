# Browser Tool

## Basic Usage

```python
from assistant.tools.web.browser import get_content

# Fetch page content
content = get_content("https://example.com")
print(content)
```

## Custom Timeout

```python
# 60 second timeout
content = get_content("https://slow-site.com", timeout=60000)
```

## Wait for Element

```python
# Wait for specific content to load
content = get_content(
    "https://dynamic-site.com",
    wait_for_selector=".main-content"
)
```

## Extract Images

```python
from assistant.tools.web.browser import get_content_with_images

# Get text and images
result = get_content_with_images("https://example.com")

print(f"Text: {result['text']}")
print(f"Images: {result['images']}")
```

## Features

- Random delays (0-1s) to avoid bot detection
- Realistic user agent
- Clean formatted text (removes scripts, styles)
- Image URL extraction
- Proper error handling

That's it.
