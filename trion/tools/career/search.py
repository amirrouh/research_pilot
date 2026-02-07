"""Job search tool using jobspy library.

Supports LinkedIn and Indeed with consistent interface.
"""

from typing import Literal, List, Dict, cast
from langchain.tools import tool
from jobspy import scrape_jobs


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

    """

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

        try:
            jobs = search(cast(Platform, platform_lower), keywords, location, min(results_wanted, 50))
        except Exception as scrape_error:
            error_msg = str(scrape_error)

            # Handle common scraping errors
            if "401" in error_msg or "403" in error_msg:
                return (
                    f"{platform.capitalize()} is blocking automated requests (error: {error_msg}).\n\n"
                    f"Try:\n"
                    f"1. Use 'linkedin' instead: search_jobs('linkedin', '{keywords}', '{location}')\n"
                    f"2. Wait a few minutes and try again\n"
                    f"3. Search manually at https://{platform_lower}.com/jobs"
                )
            elif "timeout" in error_msg.lower():
                return f"{platform.capitalize()} request timed out. Try again or use a different platform."
            else:
                raise  # Re-raise if it's not a known scraping issue

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

    except Exception as e:
        return f"Error searching {platform}: {str(e)}"


@tool
def search_and_save_jobs(
    platform: str,
    keywords: str,
    location: str,
    tags: str = "",
    status: str = "new",
    results_wanted: int = 10
) -> str:
    """
    Search for jobs and save them to the database in one step.

    This tool combines searching and saving. Use this when you want to find
    jobs and store them for tracking applications.

    Args:
        platform: Job platform - "linkedin" or "indeed"
        keywords: Job title or keywords (e.g., "software engineer", "data scientist")
        location: Location (e.g., "San Francisco, CA", "remote")
        tags: Comma-separated tags to organize jobs (e.g., "python,remote,priority")
        status: Job status - "new", "saved", "applied", "interviewing", "offer", "rejected"
        results_wanted: Number of jobs to find and save (default: 10, max: 50)

    Returns:
        Summary of jobs found and saved

    Example:
        To find and save software engineer jobs in SF:
        search_and_save_jobs(platform="linkedin", keywords="software engineer", location="San Francisco, CA", tags="python,fulltime", status="new", results_wanted=10)
    """
    try:
        # Validate platform
        platform_lower = platform.lower()
        if platform_lower not in ["linkedin", "indeed"]:
            return f"Error: Platform must be 'linkedin' or 'indeed', got '{platform}'"

        # Search for jobs
        try:
            jobs = search(cast(Platform, platform_lower), keywords, location, min(results_wanted, 50))
        except Exception as scrape_error:
            error_msg = str(scrape_error)

            # Handle common scraping errors
            if "401" in error_msg or "403" in error_msg:
                return (
                    f"{platform.capitalize()} is blocking automated requests.\n\n"
                    f"Try:\n"
                    f"1. Use 'linkedin' instead if you used Indeed\n"
                    f"2. Wait a few minutes and try again\n"
                    f"3. Search manually at https://{platform_lower}.com/jobs"
                )
            else:
                raise  # Re-raise if it's not a known scraping issue

        if not jobs:
            return f"No jobs found on {platform} for '{keywords}' in {location}"

        # Save to database
        from trion.tools.storage.career import save_jobs_batch
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
        stats = save_jobs_batch(jobs, tags=tag_list, status=status, platform=platform_lower)

        # Format response
        output = [
            f"Found and processed {len(jobs)} jobs for '{keywords}' on {platform.capitalize()}:",
            f"\n✓ Saved: {stats['saved']} jobs",
            f"✓ Skipped (duplicates): {stats['skipped']}",
            f"\nTop 3 jobs:"
        ]

        for i, job in enumerate(jobs[:3], 1):
            output.append(f"\n{i}. {job['title']} at {job['company']}")
            output.append(f"   Location: {job['location']}")

            if job.get('salary_min') and job.get('salary_max'):
                currency = job.get('salary_currency', '$')
                output.append(f"   Salary: {currency}{job['salary_min']:,.0f} - {currency}{job['salary_max']:,.0f}")

            if job.get('url'):
                output.append(f"   URL: {job['url']}")

        return "\n".join(output)

    except Exception as e:
        return f"Error: {str(e)}"
