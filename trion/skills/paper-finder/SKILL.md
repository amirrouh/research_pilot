---
name: paper-finder
description: Use this skill when the user wants to search for academic papers on a specific topic from PubMed or arXiv
---

# Paper Finder Skill

## Overview
Searches PubMed and arXiv for academic papers on a given topic and presents the results in a clear, organized format.

## Instructions

1. Identify the research topic from the user's request
2. Use the `search_papers` tool to find relevant papers
3. Display results showing:
   - Paper title
   - Authors
   - Publication year
   - Source (PubMed/arXiv)
4. Provide clear, organized results to the user

## Example Usage

**User**: "Find recent papers about CRISPR gene editing"

**Steps**:
1. Search PubMed and arXiv for "CRISPR gene editing"
2. Display top 5-10 results with key details
3. Offer to refine the search if needed

## Available Tools

- `search_papers`: Searches PubMed and arXiv databases for academic papers
