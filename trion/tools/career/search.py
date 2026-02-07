"""Job search tool using jobspy library.

Supports LinkedIn and Indeed with consistent interface.
"""

from typing import Literal, List, Dict, cast
from langchain.tools import tool
from trion.tools._dependencies import require_package


Platform = Literal["linkedin", "indeed"]


def search(
    platform: Platform,
    keywords: str,
    location: str,
    results_wanted: int = 10
) -> List[Dict[str, str]]:
    """
    Search for jobs on LinkedIn or Indeed.

    Args:
        platform: Job platform - "linkedin" or "indeed"
        keywords: Job title or keywords to search for
        location: Location for job search (e.g., "San Francisco, CA" or "remote")
        results_wanted: Number of results to return (default: 10)

    Returns:
        List of job dictionaries with keys: title, company, location, url, description,
        date_posted, job_type, salary_min, salary_max, is_remote

    Raises:
        ImportError: If python-jobspy is not installed
    """
    require_package("jobspy", "web", "python-jobspy")
    from jobspy import scrape_jobs

    # Scrape jobs
    df = scrape_jobs(
        site_name=platform,
        search_term=keywords,
        location=location,
        results_wanted=results_wanted
    )

    # Convert to list of dicts
    jobs = []
    for row in df.to_dict("records"):
        jobs.append({
            "title": row.get("title", "Unknown"),
            "company": row.get("company", "Unknown"),
            "location": row.get("location", "Unknown"),
            "url": row.get("job_url", ""),
            "description": row.get("description", ""),
            "date_posted": str(row.get("date_posted")) if row.get("date_posted") else None,
            "job_type": row.get("job_type", ""),
            "salary_min": row.get("min_amount"),
            "salary_max": row.get("max_amount"),
            "salary_currency": row.get("currency", ""),
            "is_remote": row.get("is_remote", False),
            "company_url": row.get("company_url", ""),
        })

    return jobs


@tool
def search_jobs(
    platform: str,
    keywords: str,
    location: str,
    results_wanted: int = 10
) -> str:
    """
    Search for jobs on LinkedIn or Indeed.

    Use this when you need to find job postings.
    Returns formatted job listings with all details.

    Args:
        platform: Job platform - "linkedin" or "indeed"
        keywords: Job title or keywords (e.g., "software engineer", "data scientist")
        location: Location (e.g., "San Francisco, CA", "New York, NY", "remote")
        results_wanted: Number of results to return (default: 10, max: 50)

    Returns:
        Formatted job listings with title, company, location, salary, and apply links
    """
    try:
        # Validate and cast platform
        platform_lower = platform.lower()
        if platform_lower not in ["linkedin", "indeed"]:
            return f"Error: Platform must be 'linkedin' or 'indeed', got '{platform}'"

        jobs = search(cast(Platform, platform_lower), keywords, location, min(results_wanted, 50))

        if not jobs:
            return f"No jobs found on {platform} for '{keywords}' in {location}"

        # Format results
        output = [f"Found {len(jobs)} jobs on {platform.capitalize()}:\n"]

        for i, job in enumerate(jobs, 1):
            output.append(f"{i}. **{job['title']}** at {job['company']}")
            output.append(f"   Location: {job['location']}")

            # Add salary if available
            if job.get('salary_min') and job.get('salary_max'):
                currency = job.get('salary_currency', '$')
                output.append(
                    f"   Salary: {currency}{job['salary_min']:,.0f} - "
                    f"{currency}{job['salary_max']:,.0f}"
                )
            elif job.get('salary_min'):
                currency = job.get('salary_currency', '$')
                output.append(f"   Salary: {currency}{job['salary_min']:,.0f}+")

            # Add job type
            if job.get('job_type'):
                output.append(f"   Type: {job['job_type']}")

            # Add remote indicator
            if job.get('is_remote'):
                output.append("   Remote: Yes")

            # Add apply link
            if job.get('url'):
                output.append(f"   Apply: {job['url']}")

            output.append("")

        return "\n".join(output)

    except ImportError as e:
        return (
            "Error: python-jobspy package not installed.\n\n"
            "Install it with one of:\n"
            "  pip install python-jobspy\n"
            "  pip install trion[web]\n"
            "  pip install trion[all]\n"
        )
    except Exception as e:
        return f"Error searching {platform}: {str(e)}"
