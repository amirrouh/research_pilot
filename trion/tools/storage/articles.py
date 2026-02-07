"""
SQLite Paper Storage - Local Database for Research Papers

Stores research papers from PubMed and arXiv in a local SQLite database.
Provides search, tagging, and organization features.

Usage:
    from trion.tools.storage.articles import save_papers_batch, search_papers_db
    from trion.tools.research.articles import query

    # Search and save papers
    results = query(keywords="CRISPR", sources=[('pubmed', 5)])
    stats = save_papers_batch(results, tags=['genomics', 'crispr'])

    # Search saved papers
    papers = search_papers_db(keywords="gene editing", tags=['genomics'])

    # Agent usage
    from trion.agents.core import agent
    from trion.tools.storage.articles import save_papers_to_db, find_saved_papers

    research_agent = agent(save_papers_to_db, find_saved_papers)
"""

import sqlite3
import pandas as pd
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Union
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


def _load_config() -> dict:
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"

    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    else:
        return {}


def get_db_path() -> Path:
    """Get database path from config or use default"""
    config = _load_config()
    storage_config = config.get('storage', {})
    db_path_str = storage_config.get('database_path', 'files/dbs/papers.db')

    # Convert to absolute path relative to project root
    project_root = Path(__file__).parent.parent.parent.parent
    db_path = project_root / db_path_str

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return db_path


def init_db(db_path: Optional[Path] = None, verbose: bool = False) -> None:
    """
    Initialize database with schema.

    Args:
        db_path: Path to database file (uses config default if not provided)
        verbose: Print initialization messages
    """
    if db_path is None:
        db_path = get_db_path()

    # Check if auto_init is enabled
    config = _load_config()
    storage_config = config.get('storage', {})
    auto_init = storage_config.get('auto_init', True)

    if db_path.exists() and not verbose:
        logger.debug(f"Database already exists at {db_path}")
        return

    logger.info(f"Initializing database at {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create papers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Dual identifiers
            pmid TEXT UNIQUE,
            arxiv_id TEXT UNIQUE,
            doi TEXT,

            -- Core fields
            title TEXT NOT NULL,
            authors TEXT,
            year TEXT,
            date TEXT,

            -- Publication info
            journal TEXT,
            volume TEXT,
            issue TEXT,
            pages TEXT,

            -- Content
            abstract TEXT,

            -- URLs
            url TEXT,
            doi_url TEXT,

            -- Organization
            source TEXT,
            tags TEXT,
            notes TEXT,
            added_timestamp TEXT,

            CHECK (pmid IS NOT NULL OR arxiv_id IS NOT NULL)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_authors ON papers(authors)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_tags ON papers(tags)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")

    conn.commit()
    conn.close()

    if verbose:
        logger.info(f"Database initialized at {db_path}")


def save_paper(
    paper: Union[pd.Series, Dict],
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Save a single paper to the database.

    Args:
        paper: Paper data (DataFrame row or dict)
        tags: Optional list of tags
        notes: Optional notes
        verbose: Log save operations

    Returns:
        True if saved, False if duplicate skipped
    """
    db_path = get_db_path()
    init_db(db_path)

    # Convert Series to dict if needed
    if isinstance(paper, pd.Series):
        paper_dict = paper.to_dict()
    else:
        paper_dict = paper

    # Prepare tags
    tags_str = ','.join(tags) if tags else ''

    # Get timestamp
    timestamp = datetime.now().isoformat()

    # Extract fields
    pmid = paper_dict.get('pmid', 'N/A')
    pmid = None if pmid == 'N/A' else str(pmid)

    arxiv_id = paper_dict.get('arxiv_id', 'N/A')
    arxiv_id = None if arxiv_id == 'N/A' else str(arxiv_id)

    # Must have at least one ID
    if not pmid and not arxiv_id:
        logger.warning(f"Paper missing both PMID and arXiv ID: {paper_dict.get('title', 'Unknown')}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO papers (
                pmid, arxiv_id, doi, title, authors, year, date,
                journal, volume, issue, pages, abstract,
                url, doi_url, source, tags, notes, added_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pmid,
            arxiv_id,
            paper_dict.get('doi', 'N/A'),
            paper_dict.get('title', 'N/A'),
            paper_dict.get('authors', 'N/A'),
            paper_dict.get('year', 'N/A'),
            paper_dict.get('date', 'N/A'),
            paper_dict.get('journal', 'N/A'),
            paper_dict.get('volume', 'N/A'),
            paper_dict.get('issue', 'N/A'),
            paper_dict.get('pages', 'N/A'),
            paper_dict.get('abstract', 'N/A'),
            paper_dict.get('url', 'N/A'),
            paper_dict.get('doi_url', 'N/A'),
            paper_dict.get('source', 'N/A'),
            tags_str,
            notes,
            timestamp
        ))

        conn.commit()

        if verbose:
            logger.info(f"Saved: {paper_dict.get('title', 'Unknown')[:60]}...")

        return True

    except sqlite3.IntegrityError:
        # Duplicate paper (PMID or arXiv ID already exists)
        if verbose:
            logger.debug(f"Skipped duplicate: {paper_dict.get('title', 'Unknown')[:60]}...")
        return False

    finally:
        conn.close()


def save_papers_batch(
    papers: pd.DataFrame,
    tags: Optional[List[str]] = None,
    verbose: bool = False
) -> Dict[str, int]:
    """
    Save multiple papers to the database.

    Args:
        papers: DataFrame of papers (from articles.query())
        tags: Optional list of tags to apply to all papers
        verbose: Log save operations

    Returns:
        Dictionary with counts: {'saved': N, 'skipped': N, 'errors': N}
    """
    stats = {'saved': 0, 'skipped': 0, 'errors': 0}

    for _, row in papers.iterrows():
        try:
            if save_paper(row, tags=tags, verbose=verbose):
                stats['saved'] += 1
            else:
                stats['skipped'] += 1
        except Exception as e:
            logger.error(f"Error saving paper: {e}")
            stats['errors'] += 1

    if verbose:
        logger.info(f"Batch save complete: {stats}")

    return stats


def load_papers(
    limit: Optional[int] = None,
    tags: Optional[List[str]] = None,
    source: Optional[str] = None
) -> pd.DataFrame:
    """
    Load papers from database with optional filters.

    Args:
        limit: Maximum number of papers to return
        tags: Filter by tags (papers must have ALL tags)
        source: Filter by source ('PubMed' or 'arXiv')

    Returns:
        DataFrame matching articles.query() format
    """
    db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found at {db_path}")
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)

    # Build query
    query = "SELECT * FROM papers WHERE 1=1"
    params = []

    if source:
        query += " AND source = ?"
        params.append(source)

    if tags:
        # Check that all tags are present
        for tag in tags:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")

    query += " ORDER BY added_timestamp DESC"

    if limit:
        query += f" LIMIT {limit}"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Reorder columns to match articles.py format
    column_order = ['title', 'authors', 'year', 'journal', 'volume', 'issue',
                    'pages', 'doi', 'pmid', 'date', 'url', 'doi_url', 'abstract',
                    'source', 'arxiv_id', 'tags', 'notes', 'added_timestamp']
    column_order = [col for col in column_order if col in df.columns]

    if not df.empty:
        df = df[column_order]

    return df


def search_papers_db(
    keywords: Optional[str] = None,
    tags: Optional[List[str]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    source: Optional[str] = None
) -> pd.DataFrame:
    """
    Full-text search in saved papers.

    Searches in title, abstract, and authors using SQLite LIKE.

    Args:
        keywords: Search terms (searches title, abstract, authors)
        tags: Filter by tags (papers must have ALL tags)
        year_from: Minimum year
        year_to: Maximum year
        source: Filter by source ('PubMed' or 'arXiv')

    Returns:
        DataFrame of matching papers
    """
    db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found at {db_path}")
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)

    # Build query
    query = "SELECT * FROM papers WHERE 1=1"
    params = []

    if keywords:
        query += """ AND (
            title LIKE ? OR
            abstract LIKE ? OR
            authors LIKE ?
        )"""
        keyword_pattern = f"%{keywords}%"
        params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

    if tags:
        for tag in tags:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")

    if year_from:
        query += " AND CAST(year AS INTEGER) >= ?"
        params.append(year_from)

    if year_to:
        query += " AND CAST(year AS INTEGER) <= ?"
        params.append(year_to)

    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY year DESC, added_timestamp DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Reorder columns
    column_order = ['title', 'authors', 'year', 'journal', 'volume', 'issue',
                    'pages', 'doi', 'pmid', 'date', 'url', 'doi_url', 'abstract',
                    'source', 'arxiv_id', 'tags', 'notes', 'added_timestamp']
    column_order = [col for col in column_order if col in df.columns]

    if not df.empty:
        df = df[column_order]

    return df


def tag_paper(
    paper_id: str,
    id_type: str = "auto",
    tags: Optional[List[str]] = None,
    add_tags: Optional[List[str]] = None,
    remove_tags: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Update tags and notes for a paper.

    Args:
        paper_id: Paper identifier (PMID or arXiv ID)
        id_type: 'auto', 'pmid', or 'arxiv' (auto detects based on format)
        tags: Replace all tags with this list
        add_tags: Add these tags to existing tags
        remove_tags: Remove these tags from existing tags
        notes: Update notes (None = no change, empty string = clear notes)

    Returns:
        True if paper found and updated, False otherwise
    """
    db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Determine ID type
    if id_type == "auto":
        # Simple heuristic: arXiv IDs contain dots, PMIDs don't
        id_type = "arxiv_id" if "." in paper_id else "pmid"
    elif id_type == "arxiv":
        id_type = "arxiv_id"
    elif id_type == "pmid":
        id_type = "pmid"

    # Get current paper
    cursor.execute(f"SELECT tags FROM papers WHERE {id_type} = ?", (paper_id,))
    row = cursor.fetchone()

    if not row:
        logger.warning(f"Paper not found: {paper_id}")
        conn.close()
        return False

    current_tags = row[0] if row[0] else ''
    current_tags_set = set(current_tags.split(',')) if current_tags else set()
    current_tags_set.discard('')  # Remove empty strings

    # Update tags
    if tags is not None:
        # Replace all tags
        new_tags_set = set(tags)
    else:
        # Add/remove tags
        new_tags_set = current_tags_set.copy()

        if add_tags:
            new_tags_set.update(add_tags)

        if remove_tags:
            new_tags_set.difference_update(remove_tags)

    new_tags_str = ','.join(sorted(new_tags_set))

    # Update database
    if notes is not None:
        cursor.execute(
            f"UPDATE papers SET tags = ?, notes = ? WHERE {id_type} = ?",
            (new_tags_str, notes, paper_id)
        )
    else:
        cursor.execute(
            f"UPDATE papers SET tags = ? WHERE {id_type} = ?",
            (new_tags_str, paper_id)
        )

    conn.commit()
    conn.close()

    logger.info(f"Updated paper {paper_id}: tags={new_tags_str}")
    return True


def get_paper_by_id(paper_id: str, id_type: str = "auto") -> Optional[Dict]:
    """
    Get specific paper by ID.

    Args:
        paper_id: Paper identifier (PMID or arXiv ID)
        id_type: 'auto', 'pmid', or 'arxiv'

    Returns:
        Dictionary with paper data or None if not found
    """
    db_path = get_db_path()

    if not db_path.exists():
        return None

    # Determine ID type
    if id_type == "auto":
        id_type = "arxiv_id" if "." in paper_id else "pmid"
    elif id_type == "arxiv":
        id_type = "arxiv_id"
    elif id_type == "pmid":
        id_type = "pmid"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM papers WHERE {id_type} = ?", (paper_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)
    return None


def delete_paper(paper_id: str, id_type: str = "auto") -> bool:
    """
    Delete paper from database.

    Args:
        paper_id: Paper identifier (PMID or arXiv ID)
        id_type: 'auto', 'pmid', or 'arxiv'

    Returns:
        True if deleted, False if not found
    """
    db_path = get_db_path()

    if not db_path.exists():
        return False

    # Determine ID type
    if id_type == "auto":
        id_type = "arxiv_id" if "." in paper_id else "pmid"
    elif id_type == "arxiv":
        id_type = "arxiv_id"
    elif id_type == "pmid":
        id_type = "pmid"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM papers WHERE {id_type} = ?", (paper_id,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    if deleted:
        logger.info(f"Deleted paper: {paper_id}")

    return deleted


def get_database_stats() -> Dict:
    """
    Get statistics about the database.

    Returns:
        Dictionary with database statistics
    """
    db_path = get_db_path()

    if not db_path.exists():
        return {
            'database_exists': False,
            'database_path': str(db_path)
        }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total papers
    cursor.execute("SELECT COUNT(*) FROM papers")
    total = cursor.fetchone()[0]

    # By source
    cursor.execute("SELECT source, COUNT(*) FROM papers GROUP BY source")
    by_source = dict(cursor.fetchall())

    # By year (top 10)
    cursor.execute("""
        SELECT year, COUNT(*)
        FROM papers
        WHERE year != 'N/A'
        GROUP BY year
        ORDER BY year DESC
        LIMIT 10
    """)
    by_year = dict(cursor.fetchall())

    # All unique tags
    cursor.execute("SELECT tags FROM papers WHERE tags != ''")
    all_tags = []
    for row in cursor.fetchall():
        if row[0]:
            all_tags.extend(row[0].split(','))
    unique_tags = sorted(set(all_tags))

    conn.close()

    return {
        'database_exists': True,
        'database_path': str(db_path),
        'total_papers': total,
        'by_source': by_source,
        'recent_years': by_year,
        'tags': unique_tags
    }


# LangChain Tool Integration
try:
    from langchain_core.tools import tool

    @tool
    def save_papers_to_db(papers_json: str, tags: str = "") -> str:
        """
        Save research papers to local database for later reference.

        Use this after searching for papers to store them locally. This allows
        you to build a personal research library and avoid re-querying external
        sources.

        Args:
            papers_json: JSON string of papers (usually from search_papers results)
            tags: Comma-separated tags to organize papers (e.g., "genomics,crispr,2024")

        Returns:
            Summary of save operation with counts
        """
        try:
            import json
            papers_list = json.loads(papers_json)
            df = pd.DataFrame(papers_list)

            tags_list = [t.strip() for t in tags.split(',') if t.strip()]

            stats = save_papers_batch(df, tags=tags_list, verbose=True)

            return (
                f"Saved {stats['saved']} papers, "
                f"skipped {stats['skipped']} duplicates, "
                f"{stats['errors']} errors"
            )
        except Exception as e:
            return f"Error saving papers: {e}"

    @tool
    def find_saved_papers(keywords: str = "", tags: str = "", source: str = "") -> str:
        """
        Search previously saved papers in local database.

        Much faster than re-querying PubMed/arXiv. Use this to find papers you've
        already saved and organized.

        Args:
            keywords: Search in title, abstract, authors (e.g., "CRISPR gene editing")
            tags: Comma-separated tags to filter by (e.g., "genomics,crispr")
            source: Filter by source - "PubMed" or "arXiv" (leave empty for all)

        Returns:
            Formatted list of matching papers with titles, authors, and years
        """
        try:
            tags_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else None
            source_filter = source if source else None

            df = search_papers_db(
                keywords=keywords if keywords else None,
                tags=tags_list,
                source=source_filter
            )

            if len(df) == 0:
                return "No papers found matching criteria"

            output = [f"Found {len(df)} saved papers:\n"]

            for i, row in df.iterrows():
                tags_str = row.get('tags', '')
                tags_display = f" [Tags: {tags_str}]" if tags_str else ""

                output.append(
                    f"{i+1}. {row['title']}\n"
                    f"   Authors: {row['authors'][:100]}...\n"
                    f"   Year: {row['year']} | Source: {row['source']}{tags_display}\n"
                    f"   URL: {row['url']}\n"
                )

            return "\n".join(output)

        except Exception as e:
            return f"Error searching papers: {e}"

    @tool
    def tag_saved_paper(paper_id: str, tags: str, notes: str = "") -> str:
        """
        Add tags and notes to a saved paper for organization.

        Use this to organize your saved papers by topic, project, or any other
        category. Tags make it easy to find related papers later.

        Args:
            paper_id: Paper identifier (PMID like "38234567" or arXiv ID like "2301.07041")
            tags: Comma-separated tags to add (e.g., "important,review-paper,cite-in-thesis")
            notes: Optional notes about the paper

        Returns:
            Confirmation message
        """
        try:
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]

            success = tag_paper(
                paper_id=paper_id,
                add_tags=tags_list,
                notes=notes if notes else None
            )

            if success:
                return f"Updated paper {paper_id} with tags: {', '.join(tags_list)}"
            else:
                return f"Paper {paper_id} not found in database"

        except Exception as e:
            return f"Error tagging paper: {e}"

    @tool
    def get_database_info() -> str:
        """
        Get statistics about saved papers database.

        Shows how many papers you've saved, breakdown by source and year,
        and all available tags.

        Returns:
            Database statistics and summary
        """
        try:
            stats = get_database_stats()

            if not stats['database_exists']:
                return f"Database not initialized at {stats['database_path']}"

            output = [
                f"Database: {stats['database_path']}\n",
                f"Total papers: {stats['total_papers']}\n"
            ]

            if stats['by_source']:
                output.append("By source:")
                for source, count in stats['by_source'].items():
                    output.append(f"  - {source}: {count}")
                output.append("")

            if stats['recent_years']:
                output.append("Recent years:")
                for year, count in list(stats['recent_years'].items())[:5]:
                    output.append(f"  - {year}: {count}")
                output.append("")

            if stats['tags']:
                output.append(f"Tags ({len(stats['tags'])}): {', '.join(stats['tags'][:20])}")
                if len(stats['tags']) > 20:
                    output.append(f"  ... and {len(stats['tags']) - 20} more")

            return "\n".join(output)

        except Exception as e:
            return f"Error getting database info: {e}"

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db(verbose=True)

    # Get stats
    print("\nDatabase stats:")
    stats = get_database_stats()
    print(f"Total papers: {stats.get('total_papers', 0)}")
    print(f"Database: {stats.get('database_path')}")

    print("\n✅ Storage module ready!")
