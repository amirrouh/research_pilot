"""
Job postings storage and database management.

This module provides functionality to save, load, search, and manage
job postings in a local SQLite database.
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
DEFAULT_DB_PATH = Path("files/dbs/jobs.db")


def get_db_path() -> Path:
    """
    Load database path from config.yaml.

    Returns:
        Path to jobs database
    """
    try:
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                db_path = config.get('storage', {}).get('jobs_database_path')
                if db_path:
                    return Path(db_path)
    except Exception as e:
        logger.warning(f"Could not load database path from config: {e}")

    return DEFAULT_DB_PATH


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initialize jobs database with schema.

    Creates the database file and tables if they don't exist.

    Args:
        db_path: Path to database file (uses config default if not provided)

    Example:
        >>> init_db()
        >>> init_db(Path("custom/path/jobs.db"))
    """
    if db_path is None:
        db_path = get_db_path()

    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Core info
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT UNIQUE,

                -- Job details
                description TEXT,
                date_posted TEXT,
                job_type TEXT,

                -- Salary
                salary_min REAL,
                salary_max REAL,
                salary_currency TEXT,

                -- Remote/location
                is_remote BOOLEAN,

                -- Company
                company_url TEXT,

                -- Platform info
                platform TEXT,

                -- Organization metadata
                tags TEXT,
                notes TEXT,
                status TEXT,
                added_timestamp TEXT
            )
        """)

        # Create indexes for fast searching
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON jobs(job_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_tags ON jobs(tags)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_is_remote ON jobs(is_remote)"
        )

        conn.commit()
        conn.close()

        logger.info(f"Database initialized at {db_path}")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def save_job(
    job: Union[pd.Series, Dict],
    tags: List[str] = None,
    notes: str = None,
    status: str = "new",
    db_path: Optional[Path] = None
) -> bool:
    """
    Save a single job to the database.

    Args:
        job: Job data (DataFrame row or dictionary)
        tags: Optional tags to add (e.g., ['applied', 'frontend', 'priority'])
        notes: Optional notes
        status: Job status - 'new', 'applied', 'interviewing', 'offer', 'rejected', 'saved'
        db_path: Database path (uses config default if not provided)

    Returns:
        True if saved successfully, False if duplicate

    Example:
        >>> save_job(job_data, tags=['python', 'remote'], status='applied')
    """
    if db_path is None:
        db_path = get_db_path()

    # Ensure database exists
    init_db(db_path)

    # Convert Series to dict if needed
    if isinstance(job, pd.Series):
        data = job.to_dict()
    else:
        data = job

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Prepare tags (comma-separated)
        tags_str = ",".join(tags) if tags else ""

        # Current timestamp
        timestamp = datetime.now().isoformat()

        # Insert job
        cursor.execute("""
            INSERT INTO jobs (
                title, company, location, url,
                description, date_posted, job_type,
                salary_min, salary_max, salary_currency,
                is_remote, company_url, platform,
                tags, notes, status, added_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('title'),
            data.get('company'),
            data.get('location'),
            data.get('url'),
            data.get('description'),
            data.get('date_posted'),
            data.get('job_type'),
            data.get('salary_min'),
            data.get('salary_max'),
            data.get('salary_currency'),
            data.get('is_remote', False),
            data.get('company_url'),
            data.get('platform', 'unknown'),
            tags_str,
            notes,
            status,
            timestamp
        ))

        conn.commit()
        logger.info(f"Saved job: {data.get('title')} at {data.get('company')}")
        return True

    except sqlite3.IntegrityError:
        logger.info(f"Job already exists: {data.get('url')}")
        return False
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        return False
    finally:
        if conn:
            conn.close()


def save_jobs_batch(
    jobs: Union[pd.DataFrame, List[Dict]],
    tags: List[str] = None,
    status: str = "new",
    platform: str = "unknown",
    db_path: Optional[Path] = None
) -> Dict[str, int]:
    """
    Save multiple jobs to the database.

    Args:
        jobs: DataFrame or list of job dictionaries
        tags: Optional tags to add to all jobs
        status: Status for all jobs (default: 'new')
        platform: Platform name (e.g., 'linkedin', 'indeed')
        db_path: Database path (uses config default if not provided)

    Returns:
        Dictionary with counts: {'saved': N, 'skipped': N, 'errors': N}

    Example:
        >>> results = save_jobs_batch(jobs_df, tags=['python', 'remote'], platform='linkedin')
        >>> print(f"Saved {results['saved']} jobs")
    """
    stats = {'saved': 0, 'skipped': 0, 'errors': 0}

    # Convert to DataFrame if list
    if isinstance(jobs, list):
        jobs = pd.DataFrame(jobs)

    # Add platform to each job
    jobs = jobs.copy()
    if 'platform' not in jobs.columns:
        jobs['platform'] = platform

    for idx, row in jobs.iterrows():
        try:
            success = save_job(row, tags=tags, status=status, db_path=db_path)
            if success:
                stats['saved'] += 1
            else:
                stats['skipped'] += 1
        except Exception as e:
            logger.error(f"Error saving job {idx}: {e}")
            stats['errors'] += 1

    logger.info(f"Batch save complete: {stats}")
    return stats


def load_jobs(
    limit: int = None,
    tags: List[str] = None,
    status: str = None,
    platform: str = None,
    is_remote: bool = None,
    db_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load jobs from database with optional filters.

    Args:
        limit: Maximum number of jobs to return
        tags: Filter by tags (returns jobs with ANY of these tags)
        status: Filter by status ('new', 'applied', 'interviewing', etc.)
        platform: Filter by platform ('linkedin', 'indeed')
        is_remote: Filter by remote status (True/False)
        db_path: Database path (uses config default if not provided)

    Returns:
        DataFrame with matching jobs

    Example:
        >>> jobs = load_jobs(limit=100, tags=['python'], status='new')
        >>> remote_jobs = load_jobs(is_remote=True, platform='linkedin')
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)

        # Build query
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if tags:
            # Match any tag
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])

        if status:
            query += " AND status = ?"
            params.append(status)

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        if is_remote is not None:
            query += " AND is_remote = ?"
            params.append(1 if is_remote else 0)

        query += " ORDER BY added_timestamp DESC"

        if limit:
            query += f" LIMIT {limit}"

        df = pd.read_sql_query(query, conn, params=params)
        logger.info(f"Loaded {len(df)} jobs")
        return df

    except Exception as e:
        logger.error(f"Error loading jobs: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def search_jobs_db(
    keywords: str = None,
    location: str = None,
    tags: List[str] = None,
    job_type: str = None,
    salary_min: float = None,
    is_remote: bool = None,
    db_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Full-text search in jobs database.

    Searches title, description, company, and location fields.

    Args:
        keywords: Search terms (searches title, description, company)
        location: Location filter (searches location field)
        tags: Filter by tags
        job_type: Job type filter (e.g., 'fulltime', 'contract')
        salary_min: Minimum salary requirement
        is_remote: Filter by remote status
        db_path: Database path (uses config default if not provided)

    Returns:
        DataFrame with matching jobs

    Example:
        >>> results = search_jobs_db(keywords="python engineer", is_remote=True)
        >>> results = search_jobs_db(location="San Francisco", salary_min=100000)
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)

        # Build query
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if keywords:
            # Full-text search across multiple fields
            query += """ AND (
                title LIKE ? OR
                description LIKE ? OR
                company LIKE ?
            )"""
            keyword_pattern = f"%{keywords}%"
            params.extend([keyword_pattern] * 3)

        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        if tags:
            # Match any tag
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])

        if job_type:
            query += " AND job_type = ?"
            params.append(job_type)

        if salary_min is not None:
            query += " AND (salary_min >= ? OR salary_max >= ?)"
            params.extend([salary_min, salary_min])

        if is_remote is not None:
            query += " AND is_remote = ?"
            params.append(1 if is_remote else 0)

        query += " ORDER BY added_timestamp DESC"

        df = pd.read_sql_query(query, conn, params=params)
        logger.info(f"Found {len(df)} matching jobs")
        return df

    except Exception as e:
        logger.error(f"Error searching database: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def update_job_status(
    job_id: int = None,
    url: str = None,
    status: str = None,
    tags: List[str] = None,
    add_tags: List[str] = None,
    remove_tags: List[str] = None,
    notes: str = None,
    db_path: Optional[Path] = None
) -> bool:
    """
    Update status, tags, and notes for a job.

    Args:
        job_id: Database ID of the job (optional if url provided)
        url: Job URL (optional if job_id provided)
        status: New status ('applied', 'interviewing', 'offer', 'rejected', 'saved')
        tags: Replace all tags with these (mutually exclusive with add/remove)
        add_tags: Add these tags to existing tags
        remove_tags: Remove these tags from existing tags
        notes: Update notes (None = no change, empty string = clear notes)
        db_path: Database path (uses config default if not provided)

    Returns:
        True if successful

    Example:
        >>> update_job_status(job_id=1, status='applied', add_tags=['priority'])
        >>> update_job_status(url='https://...', status='interviewing', notes='Phone screen scheduled')
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return False

    if not job_id and not url:
        logger.error("Either job_id or url must be provided")
        return False

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        # Get current job data
        if job_id:
            cursor.execute("SELECT tags, notes FROM jobs WHERE id = ?", (job_id,))
        else:
            cursor.execute("SELECT tags, notes FROM jobs WHERE url = ?", (url,))

        result = cursor.fetchone()

        if not result:
            logger.warning(f"Job not found")
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

        # Build update query
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)

        if new_tags != current_tags:
            updates.append("tags = ?")
            params.append(new_tags)

        if new_notes != current_notes:
            updates.append("notes = ?")
            params.append(new_notes)

        if not updates:
            logger.info("No changes to make")
            return True

        # Execute update
        update_query = f"UPDATE jobs SET {', '.join(updates)} WHERE "
        if job_id:
            update_query += "id = ?"
            params.append(job_id)
        else:
            update_query += "url = ?"
            params.append(url)

        cursor.execute(update_query, params)
        conn.commit()

        logger.info(f"Updated job: {job_id or url}")
        return True

    except Exception as e:
        logger.error(f"Error updating job: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_job_by_id(job_id: int, db_path: Optional[Path] = None) -> Optional[Dict]:
    """
    Get a specific job from database by ID.

    Args:
        job_id: Database ID
        db_path: Database path (uses config default if not provided)

    Returns:
        Dictionary with job data, or None if not found

    Example:
        >>> job = get_job_by_id(42)
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

        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return None

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Create dictionary
        job = dict(zip(columns, result))
        return job

    except Exception as e:
        logger.error(f"Error retrieving job: {e}")
        return None
    finally:
        if conn:
            conn.close()


def delete_job(job_id: int = None, url: str = None, db_path: Optional[Path] = None) -> bool:
    """
    Delete a job from the database.

    Args:
        job_id: Database ID (optional if url provided)
        url: Job URL (optional if job_id provided)
        db_path: Database path (uses config default if not provided)

    Returns:
        True if deleted successfully

    Example:
        >>> delete_job(job_id=42)
        >>> delete_job(url='https://...')
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return False

    if not job_id and not url:
        logger.error("Either job_id or url must be provided")
        return False

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()

        if job_id:
            cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        else:
            cursor.execute("DELETE FROM jobs WHERE url = ?", (url,))

        rows_deleted = cursor.rowcount
        conn.commit()

        if rows_deleted > 0:
            logger.info(f"Deleted job: {job_id or url}")
            return True
        else:
            logger.warning(f"Job not found")
            return False

    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_database_stats(db_path: Optional[Path] = None) -> Dict:
    """
    Get statistics about the jobs database.

    Args:
        db_path: Database path (uses config default if not provided)

    Returns:
        Dictionary with statistics

    Example:
        >>> stats = get_database_stats()
        >>> print(f"Total jobs: {stats['total_jobs']}")
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return {
            'total_jobs': 0,
            'by_status': {},
            'by_platform': {},
            'by_company': {},
            'remote_jobs': 0,
            'all_tags': []
        }

    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)

        # Total jobs
        total = pd.read_sql_query("SELECT COUNT(*) as count FROM jobs", conn)
        total_jobs = total.iloc[0]['count']

        # By status
        by_status = pd.read_sql_query(
            "SELECT status, COUNT(*) as count FROM jobs GROUP BY status ORDER BY count DESC",
            conn
        )
        status_dict = dict(zip(by_status['status'], by_status['count']))

        # By platform
        by_platform = pd.read_sql_query(
            "SELECT platform, COUNT(*) as count FROM jobs GROUP BY platform ORDER BY count DESC",
            conn
        )
        platform_dict = dict(zip(by_platform['platform'], by_platform['count']))

        # By company (top 10)
        by_company = pd.read_sql_query(
            "SELECT company, COUNT(*) as count FROM jobs GROUP BY company ORDER BY count DESC LIMIT 10",
            conn
        )
        company_dict = dict(zip(by_company['company'], by_company['count']))

        # Remote jobs
        remote = pd.read_sql_query("SELECT COUNT(*) as count FROM jobs WHERE is_remote = 1", conn)
        remote_jobs = remote.iloc[0]['count']

        # All unique tags
        tags_df = pd.read_sql_query("SELECT tags FROM jobs WHERE tags != ''", conn)
        all_tags = set()
        for tag_str in tags_df['tags']:
            if tag_str:
                all_tags.update(tag_str.split(','))
        all_tags.discard('')

        return {
            'total_jobs': total_jobs,
            'by_status': status_dict,
            'by_platform': platform_dict,
            'by_company': company_dict,
            'remote_jobs': remote_jobs,
            'all_tags': sorted(all_tags)
        }

    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            'total_jobs': 0,
            'by_status': {},
            'by_platform': {},
            'by_company': {},
            'remote_jobs': 0,
            'all_tags': []
        }
    finally:
        if conn:
            conn.close()


# ============================================================================
# LangChain Tools
# ============================================================================


@tool
def save_jobs_to_db(jobs_json: str, tags: str = "", status: str = "new", platform: str = "unknown") -> str:
    """
    Save job postings to local database.

    Use this tool to persist jobs from search results to your local database
    for tracking applications and follow-up. Duplicate jobs are automatically skipped.

    Args:
        jobs_json: JSON string with job data (from search results)
        tags: Comma-separated tags to add (e.g., "python,remote,priority")
        status: Job status - 'new', 'applied', 'interviewing', 'offer', 'rejected', 'saved'
        platform: Platform name (e.g., 'linkedin', 'indeed')

    Returns:
        Summary of save operation
    """
    try:
        import json

        # Parse JSON
        jobs_data = json.loads(jobs_json)

        # Convert to DataFrame
        if isinstance(jobs_data, list):
            df = pd.DataFrame(jobs_data)
        elif isinstance(jobs_data, dict):
            df = pd.DataFrame([jobs_data])
        else:
            return "Error: Invalid job data format"

        # Parse tags
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else None

        # Save batch
        stats = save_jobs_batch(df, tags=tag_list, status=status, platform=platform)

        return (
            f"Save complete:\n"
            f"  Saved: {stats['saved']} jobs\n"
            f"  Skipped (duplicates): {stats['skipped']}\n"
            f"  Errors: {stats['errors']}"
        )

    except Exception as e:
        logger.error(f"Error in save_jobs_to_db tool: {e}")
        return f"Error saving jobs: {str(e)}"


@tool
def find_saved_jobs(keywords: str = "", location: str = "", tags: str = "", status: str = "") -> str:
    """
    Search previously saved jobs in local database.

    Use this tool to search your saved job applications. Faster than
    searching job sites since data is local.

    Args:
        keywords: Search terms (searches title, description, company)
        location: Location filter
        tags: Comma-separated tags to filter by
        status: Status filter ('new', 'applied', 'interviewing', etc.)

    Returns:
        Formatted string with matching jobs
    """
    try:
        # Parse tags
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else None

        # Search database
        results = search_jobs_db(
            keywords=keywords if keywords else None,
            location=location if location else None,
            tags=tag_list
        )

        # Filter by status if provided
        if status and not results.empty:
            results = results[results['status'] == status]

        if results.empty:
            return "No saved jobs found matching the criteria."

        output = [f"Found {len(results)} saved jobs:\n"]

        for idx, row in results.head(10).iterrows():
            output.append(f"\n{idx + 1}. **{row['title']}** at {row['company']}")
            output.append(f"   Location: {row['location']}")

            if row.get('salary_min') and row.get('salary_max'):
                output.append(f"   Salary: ${row['salary_min']:,.0f} - ${row['salary_max']:,.0f}")

            output.append(f"   Status: {row['status']}")

            if row.get('tags'):
                output.append(f"   Tags: {row['tags']}")

            if row.get('url'):
                output.append(f"   URL: {row['url']}")

        if len(results) > 10:
            output.append(f"\n... and {len(results) - 10} more")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in find_saved_jobs tool: {e}")
        return f"Error searching saved jobs: {str(e)}"


@tool
def update_job(job_id: int, status: str = "", tags: str = "", notes: str = "") -> str:
    """
    Update a saved job's status, tags, or notes.

    Use this tool to track your job application progress and organize
    your job search.

    Args:
        job_id: Database ID of the job (from find_saved_jobs)
        status: New status ('applied', 'interviewing', 'offer', 'rejected', 'saved')
        tags: Tags (prefix with + to add, - to remove, or just list to replace)
        notes: Notes to add or update

    Returns:
        Confirmation message
    """
    try:
        # Parse tags
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []

        # Separate add/remove tags
        add_tags = [t[1:] for t in tag_list if t.startswith('+')]
        remove_tags = [t[1:] for t in tag_list if t.startswith('-')]
        replace_tags = [t for t in tag_list if not t.startswith('+') and not t.startswith('-')]

        if replace_tags:
            # Replace all tags
            success = update_job_status(
                job_id=job_id,
                status=status if status else None,
                tags=replace_tags,
                notes=notes if notes else None
            )
        else:
            # Add/remove tags
            success = update_job_status(
                job_id=job_id,
                status=status if status else None,
                add_tags=add_tags if add_tags else None,
                remove_tags=remove_tags if remove_tags else None,
                notes=notes if notes else None
            )

        if success:
            return f"Updated job {job_id}"
        else:
            return f"Job not found: {job_id}"

    except Exception as e:
        logger.error(f"Error in update_job tool: {e}")
        return f"Error updating job: {str(e)}"


@tool
def get_jobs_database_info() -> str:
    """
    Get statistics about saved jobs database.

    Use this tool to see overview of your job search progress including
    totals, applications by status, platforms used, and available tags.

    Returns:
        Formatted statistics
    """
    try:
        stats = get_database_stats()

        output = [
            f"Jobs Database Statistics:",
            f"\nTotal Jobs: {stats['total_jobs']}",
            f"Remote Jobs: {stats['remote_jobs']}",
        ]

        if stats['by_status']:
            output.append(f"\nBy Status:")
            for status, count in stats['by_status'].items():
                output.append(f"  {status}: {count}")

        if stats['by_platform']:
            output.append(f"\nBy Platform:")
            for platform, count in stats['by_platform'].items():
                output.append(f"  {platform}: {count}")

        if stats['by_company']:
            output.append(f"\nTop Companies:")
            for company, count in list(stats['by_company'].items())[:5]:
                output.append(f"  {company}: {count} jobs")

        if stats['all_tags']:
            output.append(f"\nAvailable Tags ({len(stats['all_tags'])}):")
            output.append(f"  {', '.join(stats['all_tags'][:10])}")
            if len(stats['all_tags']) > 10:
                output.append(f"  ... and {len(stats['all_tags']) - 10} more")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in get_jobs_database_info tool: {e}")
        return f"Error getting database info: {str(e)}"
