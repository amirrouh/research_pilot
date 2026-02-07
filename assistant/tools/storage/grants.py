"""
NIH grants storage and database management.

This module provides functionality to save, load, search, and manage
NIH grants in a local SQLite database.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import yaml
from langchain.tools import tool

# Configure logging
logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path("files/dbs/grants.db")


def get_db_path() -> Path:
    """
    Load database path from config.yaml.

    Returns:
        Path to grants database
    """
    try:
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                db_path = config.get('storage', {}).get('grants_database_path')
                if db_path:
                    return Path(db_path)
    except Exception as e:
        logger.warning(f"Could not load database path from config: {e}")

    return DEFAULT_DB_PATH


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initialize grants database with schema.

    Creates the database file and tables if they don't exist.

    Args:
        db_path: Path to database file (uses config default if not provided)

    Example:
        >>> init_db()
        >>> init_db(Path("custom/path/grants.db"))
    """
    if db_path is None:
        db_path = get_db_path()

    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Create grants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Unique identifier
                project_num TEXT UNIQUE NOT NULL,

                -- Core info
                title TEXT NOT NULL,
                pi_names TEXT,
                contact_pi_name TEXT,

                -- Organization
                organization TEXT,
                org_city TEXT,
                org_state TEXT,
                org_country TEXT,

                -- Financial
                fiscal_year INTEGER,
                award_amount INTEGER,
                award_notice_date TEXT,

                -- Timeline
                project_start_date TEXT,
                project_end_date TEXT,

                -- Content
                abstract TEXT,
                phr TEXT,

                -- Classification
                agency TEXT,
                activity_code TEXT,
                opportunity_number TEXT,
                full_study_section TEXT,

                -- URLs
                url TEXT,

                -- Organization metadata
                source TEXT,
                tags TEXT,
                notes TEXT,
                added_timestamp TEXT
            )
        """)

        # Create indexes for fast searching
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_title ON grants(title)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_pi_names ON grants(pi_names)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_organization ON grants(organization)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_fiscal_year ON grants(fiscal_year)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_tags ON grants(tags)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_agency ON grants(agency)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_grants_activity_code ON grants(activity_code)"
        )

        conn.commit()
        conn.close()

        logger.info(f"Database initialized at {db_path}")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def save_grant(
    grant: Union[pd.Series, Dict],
    tags: List[str] = None,
    notes: str = None,
    db_path: Optional[Path] = None
) -> bool:
    """
    Save a single grant to the database.

    Args:
        grant: Grant data (DataFrame row or dictionary)
        tags: Optional tags to add
        notes: Optional notes
        db_path: Database path (uses config default if not provided)

    Returns:
        True if saved successfully, False if duplicate

    Example:
        >>> save_grant(grant_data, tags=['genomics', 'crispr'], notes='Important study')
    """
    if db_path is None:
        db_path = get_db_path()

    # Ensure database exists
    init_db(db_path)

    # Convert Series to dict if needed
    if isinstance(grant, pd.Series):
        data = grant.to_dict()
    else:
        data = grant

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Prepare tags (comma-separated)
        tags_str = ",".join(tags) if tags else ""

        # Current timestamp
        timestamp = datetime.now().isoformat()

        # Insert grant
        cursor.execute("""
            INSERT INTO grants (
                project_num, title, pi_names, contact_pi_name,
                organization, org_city, org_state, org_country,
                fiscal_year, award_amount, award_notice_date,
                project_start_date, project_end_date,
                abstract, phr,
                agency, activity_code, opportunity_number, full_study_section,
                url, source, tags, notes, added_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('project_num'),
            data.get('title'),
            data.get('pi_names'),
            data.get('contact_pi_name'),
            data.get('organization'),
            data.get('org_city'),
            data.get('org_state'),
            data.get('org_country'),
            data.get('fiscal_year'),
            data.get('award_amount'),
            data.get('award_notice_date'),
            data.get('project_start_date'),
            data.get('project_end_date'),
            data.get('abstract'),
            data.get('phr'),
            data.get('agency'),
            data.get('activity_code'),
            data.get('opportunity_number'),
            data.get('full_study_section'),
            data.get('url'),
            data.get('source', 'NIH RePORTER'),
            tags_str,
            notes,
            timestamp
        ))

        conn.commit()
        logger.info(f"Saved grant: {data.get('project_num')}")
        return True

    except sqlite3.IntegrityError:
        logger.info(f"Grant already exists: {data.get('project_num')}")
        return False
    except Exception as e:
        logger.error(f"Error saving grant: {e}")
        return False
    finally:
        if conn:
            conn.close()


def save_grants_batch(
    grants: pd.DataFrame,
    tags: List[str] = None,
    db_path: Optional[Path] = None
) -> Dict[str, int]:
    """
    Save multiple grants to the database.

    Args:
        grants: DataFrame of grants
        tags: Optional tags to add to all grants
        db_path: Database path (uses config default if not provided)

    Returns:
        Dictionary with counts: {'saved': N, 'skipped': N, 'errors': N}

    Example:
        >>> results = save_grants_batch(grants_df, tags=['cancer', 'immunotherapy'])
        >>> print(f"Saved {results['saved']} grants")
    """
    stats = {'saved': 0, 'skipped': 0, 'errors': 0}

    for idx, row in grants.iterrows():
        try:
            success = save_grant(row, tags=tags, db_path=db_path)
            if success:
                stats['saved'] += 1
            else:
                stats['skipped'] += 1
        except Exception as e:
            logger.error(f"Error saving grant {idx}: {e}")
            stats['errors'] += 1

    logger.info(f"Batch save complete: {stats}")
    return stats


def load_grants(
    limit: int = None,
    tags: List[str] = None,
    agency: str = None,
    fiscal_year: int = None,
    db_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load grants from database with optional filters.

    Args:
        limit: Maximum number of grants to return
        tags: Filter by tags (returns grants with ANY of these tags)
        agency: Filter by NIH agency
        fiscal_year: Filter by fiscal year
        db_path: Database path (uses config default if not provided)

    Returns:
        DataFrame with matching grants

    Example:
        >>> grants = load_grants(limit=100, tags=['genomics'], agency='NCI')
        >>> grants = load_grants(fiscal_year=2024)
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)

        # Build query
        query = "SELECT * FROM grants WHERE 1=1"
        params = []

        if tags:
            # Match any tag
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])

        if agency:
            query += " AND agency = ?"
            params.append(agency)

        if fiscal_year:
            query += " AND fiscal_year = ?"
            params.append(fiscal_year)

        query += " ORDER BY added_timestamp DESC"

        if limit:
            query += f" LIMIT {limit}"

        df = pd.read_sql_query(query, conn, params=params)
        logger.info(f"Loaded {len(df)} grants")
        return df

    except Exception as e:
        logger.error(f"Error loading grants: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def search_grants_db(
    keywords: str = None,
    tags: List[str] = None,
    fiscal_year_from: int = None,
    fiscal_year_to: int = None,
    award_amount_min: int = None,
    award_amount_max: int = None,
    db_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Full-text search in grants database.

    Searches title, abstract, PI names, and organization fields.

    Args:
        keywords: Search terms (searches title, abstract, PI, organization)
        tags: Filter by tags
        fiscal_year_from: Start of fiscal year range
        fiscal_year_to: End of fiscal year range
        award_amount_min: Minimum award amount
        award_amount_max: Maximum award amount
        db_path: Database path (uses config default if not provided)

    Returns:
        DataFrame with matching grants

    Example:
        >>> results = search_grants_db(keywords="gene editing", tags=['genomics'])
        >>> results = search_grants_db(fiscal_year_from=2020, fiscal_year_to=2024)
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)

        # Build query
        query = "SELECT * FROM grants WHERE 1=1"
        params = []

        if keywords:
            # Full-text search across multiple fields
            query += """ AND (
                title LIKE ? OR
                abstract LIKE ? OR
                pi_names LIKE ? OR
                organization LIKE ?
            )"""
            keyword_pattern = f"%{keywords}%"
            params.extend([keyword_pattern] * 4)

        if tags:
            # Match any tag
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])

        if fiscal_year_from:
            query += " AND fiscal_year >= ?"
            params.append(fiscal_year_from)

        if fiscal_year_to:
            query += " AND fiscal_year <= ?"
            params.append(fiscal_year_to)

        if award_amount_min:
            query += " AND award_amount >= ?"
            params.append(award_amount_min)

        if award_amount_max:
            query += " AND award_amount <= ?"
            params.append(award_amount_max)

        query += " ORDER BY award_amount DESC"

        df = pd.read_sql_query(query, conn, params=params)
        logger.info(f"Found {len(df)} matching grants")
        return df

    except Exception as e:
        logger.error(f"Error searching database: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def tag_grant(
    project_num: str,
    tags: List[str] = None,
    add_tags: List[str] = None,
    remove_tags: List[str] = None,
    notes: str = None,
    db_path: Optional[Path] = None
) -> bool:
    """
    Add, update, or remove tags and notes for a grant.

    Args:
        project_num: Grant project number
        tags: Replace all tags with these (mutually exclusive with add/remove)
        add_tags: Add these tags to existing tags
        remove_tags: Remove these tags from existing tags
        notes: Update notes (None = no change, empty string = clear notes)
        db_path: Database path (uses config default if not provided)

    Returns:
        True if successful

    Example:
        >>> tag_grant("5R01CA123456", add_tags=['important', 'review'])
        >>> tag_grant("5R01CA123456", remove_tags=['draft'])
        >>> tag_grant("5R01CA123456", tags=['final'], notes='Approved')
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return False

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Get current tags
        cursor.execute("SELECT tags, notes FROM grants WHERE project_num = ?", (project_num,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Grant not found: {project_num}")
            return False

        current_tags, current_notes = result

        # Parse current tags
        tag_set = set(current_tags.split(',')) if current_tags else set()
        tag_set.discard('')  # Remove empty strings

        # Update tags
        if tags is not None:
            # Replace all tags
            new_tags = ','.join(tags)
        elif add_tags or remove_tags:
            # Add/remove tags
            if add_tags:
                tag_set.update(add_tags)
            if remove_tags:
                tag_set.difference_update(remove_tags)
            new_tags = ','.join(sorted(tag_set))
        else:
            new_tags = current_tags

        # Update notes
        new_notes = notes if notes is not None else current_notes

        # Update database
        cursor.execute(
            "UPDATE grants SET tags = ?, notes = ? WHERE project_num = ?",
            (new_tags, new_notes, project_num)
        )

        conn.commit()
        logger.info(f"Updated tags/notes for grant: {project_num}")
        return True

    except Exception as e:
        logger.error(f"Error tagging grant: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_grant_by_id(project_num: str, db_path: Optional[Path] = None) -> Optional[Dict]:
    """
    Get a specific grant from database by project number.

    Args:
        project_num: Grant project number
        db_path: Database path (uses config default if not provided)

    Returns:
        Dictionary with grant data, or None if not found

    Example:
        >>> grant = get_grant_by_id("5R01CA123456")
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return None

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM grants WHERE project_num = ?", (project_num,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return None

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Create dictionary
        grant = dict(zip(columns, result))
        return grant

    except Exception as e:
        logger.error(f"Error retrieving grant: {e}")
        return None
    finally:
        if conn:
            conn.close()


def delete_grant(project_num: str, db_path: Optional[Path] = None) -> bool:
    """
    Delete a grant from the database.

    Args:
        project_num: Grant project number
        db_path: Database path (uses config default if not provided)

    Returns:
        True if deleted successfully

    Example:
        >>> delete_grant("5R01CA123456")
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return False

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM grants WHERE project_num = ?", (project_num,))

        rows_deleted = cursor.rowcount
        conn.commit()

        if rows_deleted > 0:
            logger.info(f"Deleted grant: {project_num}")
            return True
        else:
            logger.warning(f"Grant not found: {project_num}")
            return False

    except Exception as e:
        logger.error(f"Error deleting grant: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_database_stats(db_path: Optional[Path] = None) -> Dict:
    """
    Get statistics about the grants database.

    Args:
        db_path: Database path (uses config default if not provided)

    Returns:
        Dictionary with statistics

    Example:
        >>> stats = get_database_stats()
        >>> print(f"Total grants: {stats['total_grants']}")
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return {
            'total_grants': 0,
            'by_agency': {},
            'by_fiscal_year': {},
            'total_funding': 0,
            'all_tags': []
        }

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)

        # Total grants
        total = pd.read_sql_query("SELECT COUNT(*) as count FROM grants", conn)
        total_grants = total.iloc[0]['count']

        # By agency
        by_agency = pd.read_sql_query(
            "SELECT agency, COUNT(*) as count FROM grants GROUP BY agency ORDER BY count DESC",
            conn
        )
        agency_dict = dict(zip(by_agency['agency'], by_agency['count']))

        # By fiscal year
        by_year = pd.read_sql_query(
            "SELECT fiscal_year, COUNT(*) as count FROM grants WHERE fiscal_year IS NOT NULL GROUP BY fiscal_year ORDER BY fiscal_year DESC",
            conn
        )
        year_dict = dict(zip(by_year['fiscal_year'].astype(str), by_year['count']))

        # Total funding
        funding = pd.read_sql_query("SELECT SUM(award_amount) as total FROM grants", conn)
        total_funding = int(funding.iloc[0]['total']) if funding.iloc[0]['total'] else 0

        # All unique tags
        tags_df = pd.read_sql_query("SELECT tags FROM grants WHERE tags != ''", conn)
        all_tags = set()
        for tag_str in tags_df['tags']:
            if tag_str:
                all_tags.update(tag_str.split(','))
        all_tags.discard('')

        return {
            'total_grants': total_grants,
            'by_agency': agency_dict,
            'by_fiscal_year': year_dict,
            'total_funding': total_funding,
            'all_tags': sorted(all_tags)
        }

    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            'total_grants': 0,
            'by_agency': {},
            'by_fiscal_year': {},
            'total_funding': 0,
            'all_tags': []
        }
    finally:
        if conn:
            conn.close()


# ============================================================================
# LangChain Tools
# ============================================================================


@tool
def save_grants_to_db(grants_json: str, tags: str = "") -> str:
    """
    Save NIH grants to local database.

    Use this tool to persist grants from search results to your local database
    for later reference and analysis. Duplicate grants are automatically skipped.

    Args:
        grants_json: JSON string with grant data (from search results)
        tags: Comma-separated tags to add (optional)

    Returns:
        Summary of save operation
    """
    try:
        import json

        # Parse JSON
        grants_data = json.loads(grants_json)

        # Convert to DataFrame
        if isinstance(grants_data, list):
            df = pd.DataFrame(grants_data)
        elif isinstance(grants_data, dict):
            df = pd.DataFrame([grants_data])
        else:
            return "Error: Invalid grant data format"

        # Parse tags
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else None

        # Save batch
        stats = save_grants_batch(df, tags=tag_list)

        return (
            f"Save complete:\n"
            f"  Saved: {stats['saved']} grants\n"
            f"  Skipped (duplicates): {stats['skipped']}\n"
            f"  Errors: {stats['errors']}"
        )

    except Exception as e:
        logger.error(f"Error in save_grants_to_db tool: {e}")
        return f"Error saving grants: {str(e)}"


@tool
def find_saved_grants(keywords: str = "", tags: str = "") -> str:
    """
    Search previously saved grants in local database.

    Use this tool to search your saved grants collection. Faster than
    searching NIH API since data is local.

    Args:
        keywords: Search terms (searches title, abstract, PI, organization)
        tags: Comma-separated tags to filter by

    Returns:
        Formatted string with matching grants
    """
    try:
        # Parse tags
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else None

        # Search database
        results = search_grants_db(
            keywords=keywords if keywords else None,
            tags=tag_list
        )

        if results.empty:
            return "No saved grants found matching the criteria."

        output = [f"Found {len(results)} saved grants:\n"]

        for idx, row in results.head(10).iterrows():
            output.append(f"\n{idx + 1}. {row['title']}")
            output.append(f"   Project: {row['project_num']}")
            output.append(f"   PI: {row['contact_pi_name']}")
            output.append(f"   FY: {row['fiscal_year']} | Award: ${row['award_amount']:,}")
            if row['tags']:
                output.append(f"   Tags: {row['tags']}")

        if len(results) > 10:
            output.append(f"\n... and {len(results) - 10} more")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in find_saved_grants tool: {e}")
        return f"Error searching saved grants: {str(e)}"


@tool
def tag_saved_grant(project_num: str, tags: str, notes: str = "") -> str:
    """
    Add tags and notes to a saved grant.

    Use this tool to organize and annotate your saved grants with custom
    tags and notes for better organization.

    Args:
        project_num: Grant project number
        tags: Comma-separated tags to add (prefix with + to add, - to remove)
        notes: Optional notes to add

    Returns:
        Confirmation message
    """
    try:
        # Parse tags
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]

        # Separate add/remove tags
        add_tags = [t[1:] for t in tag_list if t.startswith('+')]
        remove_tags = [t[1:] for t in tag_list if t.startswith('-')]
        replace_tags = [t for t in tag_list if not t.startswith('+') and not t.startswith('-')]

        if replace_tags:
            # Replace all tags
            success = tag_grant(project_num, tags=replace_tags, notes=notes if notes else None)
        else:
            # Add/remove tags
            success = tag_grant(
                project_num,
                add_tags=add_tags if add_tags else None,
                remove_tags=remove_tags if remove_tags else None,
                notes=notes if notes else None
            )

        if success:
            return f"Updated grant {project_num}"
        else:
            return f"Grant not found: {project_num}"

    except Exception as e:
        logger.error(f"Error in tag_saved_grant tool: {e}")
        return f"Error tagging grant: {str(e)}"


@tool
def get_grants_database_info() -> str:
    """
    Get statistics about saved grants database.

    Use this tool to see overview of your saved grants collection including
    totals, funding amounts, agencies, and available tags.

    Returns:
        Formatted statistics
    """
    try:
        stats = get_database_stats()

        output = [
            f"Grants Database Statistics:",
            f"\nTotal Grants: {stats['total_grants']}",
            f"Total Funding: ${stats['total_funding']:,}",
        ]

        if stats['by_agency']:
            output.append(f"\nTop Agencies:")
            for agency, count in list(stats['by_agency'].items())[:5]:
                output.append(f"  {agency}: {count} grants")

        if stats['by_fiscal_year']:
            output.append(f"\nRecent Fiscal Years:")
            for year, count in list(stats['by_fiscal_year'].items())[:5]:
                output.append(f"  FY{year}: {count} grants")

        if stats['all_tags']:
            output.append(f"\nAvailable Tags ({len(stats['all_tags'])}):")
            output.append(f"  {', '.join(stats['all_tags'][:10])}")
            if len(stats['all_tags']) > 10:
                output.append(f"  ... and {len(stats['all_tags']) - 10} more")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in get_grants_database_info tool: {e}")
        return f"Error getting database info: {str(e)}"
