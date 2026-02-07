"""
NIH grant proposals search and utilities.

This module provides functionality to search NIH RePORTER database for grant proposals,
retrieve grant details, find related grants, and generate citations.
"""

import logging
import time
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
from langchain.tools import tool

# Configure logging
logger = logging.getLogger(__name__)

# NIH RePORTER API configuration
NIH_API_URL = "https://api.reporter.nih.gov/v2/projects/search"
RATE_LIMIT_SECONDS = 1  # NIH API enforces 1 request per second


def _build_api_payload(
    keywords: Optional[str] = None,
    pi_name: Optional[str] = None,
    organization: Optional[str] = None,
    fiscal_years: Optional[List[int]] = None,
    award_amount_min: Optional[int] = None,
    award_amount_max: Optional[int] = None,
    activity_codes: Optional[List[str]] = None,
    agencies: Optional[List[str]] = None,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """
    Build NIH API request payload.

    Args:
        keywords: Search terms for title, abstract, or keywords
        pi_name: Principal investigator name
        organization: Institution name
        fiscal_years: List of fiscal years to include
        award_amount_min: Minimum award amount
        award_amount_max: Maximum award amount
        activity_codes: Grant type codes (R01, R21, etc.)
        agencies: NIH institutes (NCI, NIAID, etc.)
        limit: Maximum results to return
        offset: Result offset for pagination

    Returns:
        Dictionary payload for NIH API
    """
    payload = {
        "offset": offset,
        "limit": min(limit, 500),  # API max is 500
        "sort_field": "award_amount",
        "sort_order": "desc",
    }

    criteria = {}

    if keywords:
        criteria["advanced_text_search"] = {
            "operator": "and",
            "search_field": "terms",
            "search_text": keywords,
        }

    if pi_name:
        criteria["pi_names"] = [{"any_name": pi_name}]

    if organization:
        criteria["org_names"] = [organization]

    if fiscal_years:
        criteria["fiscal_years"] = fiscal_years

    if award_amount_min is not None or award_amount_max is not None:
        amount_range = {}
        if award_amount_min is not None:
            amount_range["min_amount"] = award_amount_min
        if award_amount_max is not None:
            amount_range["max_amount"] = award_amount_max
        criteria["award_amount_range"] = amount_range

    if activity_codes:
        criteria["activity_codes"] = activity_codes

    if agencies:
        criteria["agencies"] = agencies

    if criteria:
        payload["criteria"] = criteria

    return payload


def _make_api_request(payload: dict, limit: int) -> list:
    """
    Make POST request to NIH API with rate limiting.

    CRITICAL: NIH API enforces 1 request per second. Will block IP if violated.

    Args:
        payload: Request payload
        limit: Maximum results to return

    Returns:
        List of grant records from API
    """
    try:
        # CRITICAL: Rate limiting - 1 request per second
        time.sleep(RATE_LIMIT_SECONDS)

        response = requests.post(NIH_API_URL, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        logger.info(f"Retrieved {len(results)} grants from NIH API")
        return results

    except requests.exceptions.RequestException as e:
        logger.error(f"NIH API request error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in API request: {e}")
        return []


def _parse_grant_record(record: dict) -> dict:
    """
    Extract fields from NIH API response record.

    Uses .get() with 'N/A' defaults for safe field access.

    Args:
        record: Raw grant record from API

    Returns:
        Dictionary with standardized grant fields
    """
    # Extract PI names
    pi_list = record.get("principal_investigators", [])
    pi_names = "; ".join([pi.get("full_name", "N/A") for pi in pi_list]) if pi_list else "N/A"
    contact_pi = pi_list[0].get("full_name", "N/A") if pi_list else "N/A"

    # Extract organization info
    org = record.get("organization", {})
    org_name = org.get("org_name", "N/A")
    org_city = org.get("org_city", "N/A")
    org_state = org.get("org_state", "N/A")
    org_country = org.get("org_country", "N/A")

    # Extract project info
    project_num = str(record.get("appl_id") or record.get("project_num", "N/A"))
    title = record.get("project_title", "N/A")
    abstract_text = record.get("abstract_text", "N/A")
    phr_text = record.get("phr_text", "N/A")

    # Extract financial info
    fiscal_year = int(record.get("fiscal_year")) if record.get("fiscal_year") else None
    award_amount = int(record.get("award_amount", 0))

    # Extract dates
    award_notice_date = record.get("award_notice_date", "N/A")
    project_start_date = record.get("project_start_date", "N/A")
    project_end_date = record.get("project_end_date", "N/A")

    # Extract classification
    agency = record.get("agency_ic_admin", {}).get("abbreviation", "N/A")
    activity_code = record.get("activity_code", "N/A")
    opportunity_number = record.get("opportunity_number", "N/A")
    full_study_section = record.get("full_study_section", {}).get("name", "N/A")

    # Build RePORTER URL
    url = f"https://reporter.nih.gov/project-details/{project_num}" if project_num != "N/A" else "N/A"

    return {
        "project_num": project_num,
        "title": title,
        "pi_names": pi_names,
        "contact_pi_name": contact_pi,
        "organization": org_name,
        "org_city": org_city,
        "org_state": org_state,
        "org_country": org_country,
        "fiscal_year": fiscal_year,
        "award_amount": award_amount,
        "award_notice_date": award_notice_date,
        "project_start_date": project_start_date,
        "project_end_date": project_end_date,
        "abstract": abstract_text,
        "phr": phr_text,
        "agency": agency,
        "activity_code": activity_code,
        "opportunity_number": opportunity_number,
        "full_study_section": full_study_section,
        "url": url,
        "source": "NIH RePORTER",
    }


def query(
    keywords: Optional[str] = None,
    pi_name: Optional[str] = None,
    organization: Optional[str] = None,
    fiscal_years: Optional[List[int]] = None,
    award_amount_min: Optional[int] = None,
    award_amount_max: Optional[int] = None,
    activity_codes: Optional[List[str]] = None,
    agencies: Optional[List[str]] = None,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Search NIH grant proposals using RePORTER API.

    All parameters are optional. At least one search criterion should be provided
    for meaningful results.

    Args:
        keywords: Search terms for title, abstract, or project description
        pi_name: Principal investigator name
        organization: Institution/organization name
        fiscal_years: List of fiscal years (e.g., [2023, 2024])
        award_amount_min: Minimum award amount in dollars
        award_amount_max: Maximum award amount in dollars
        activity_codes: Grant type codes (e.g., ['R01', 'R21'])
        agencies: NIH institute abbreviations (e.g., ['NCI', 'NIAID'])
        limit: Maximum number of results (default 10, max 500)

    Returns:
        DataFrame with grant information, or empty DataFrame on error

    Example:
        >>> grants = query(keywords="cancer immunotherapy", limit=5)
        >>> grants = query(pi_name="Smith", fiscal_years=[2023, 2024])
        >>> grants = query(keywords="CRISPR", award_amount_min=1000000)
    """
    if limit > 500:
        logger.warning(f"Limit {limit} exceeds API max of 500, using 500")
        limit = 500

    # Build and execute request
    payload = _build_api_payload(
        keywords=keywords,
        pi_name=pi_name,
        organization=organization,
        fiscal_years=fiscal_years,
        award_amount_min=award_amount_min,
        award_amount_max=award_amount_max,
        activity_codes=activity_codes,
        agencies=agencies,
        limit=limit,
    )

    records = _make_api_request(payload, limit)

    if not records:
        logger.warning("No grants found or API request failed")
        return pd.DataFrame(columns=[
            'project_num', 'title', 'pi_names', 'contact_pi_name',
            'organization', 'org_city', 'org_state', 'org_country',
            'fiscal_year', 'award_amount', 'award_notice_date',
            'project_start_date', 'project_end_date', 'abstract', 'phr',
            'agency', 'activity_code', 'opportunity_number',
            'full_study_section', 'url', 'source'
        ])

    # Parse records
    parsed_grants = [_parse_grant_record(record) for record in records]

    # Create DataFrame
    df = pd.DataFrame(parsed_grants)

    logger.info(f"Returning {len(df)} grants")
    return df


def get_grant_details(project_num: str) -> dict:
    """
    Get full details for a specific grant by project number.

    Args:
        project_num: NIH project/application number

    Returns:
        Dictionary with complete grant information, or empty dict on error

    Example:
        >>> details = get_grant_details("5R01CA123456-05")
    """
    try:
        # NIH API expects application IDs as integers if they are numeric
        # Try to use appl_id (integer) field if project_num is numeric
        payload = {
            "criteria": {"appl_ids": [int(project_num)] if project_num.isdigit() else []},
            "limit": 1,
        }

        # If project_num is not numeric, try project_nums field
        if not project_num.isdigit():
            payload = {
                "criteria": {"project_nums": [project_num]},
                "limit": 1,
            }

        records = _make_api_request(payload, limit=1)

        if not records:
            logger.warning(f"No grant found with project_num: {project_num}")
            return {}

        return _parse_grant_record(records[0])

    except Exception as e:
        logger.error(f"Error retrieving grant details: {e}")
        return {}


def find_related_grants(project_num: str, count: int = 5) -> list:
    """
    Find grants related to a specific grant.

    Searches for grants with the same PI or organization as the target grant.

    Args:
        project_num: Reference grant project number
        count: Number of related grants to return

    Returns:
        List of related grant dictionaries

    Example:
        >>> related = find_related_grants("5R01CA123456-05", count=5)
    """
    try:
        # Get the reference grant
        grant = get_grant_details(project_num)
        if not grant:
            return []

        # Search for grants with same PI
        pi_name = grant.get("contact_pi_name")
        if pi_name and pi_name != "N/A":
            results = query(pi_name=pi_name, limit=count + 1)
            # Filter out the original grant
            related = results[results['project_num'] != project_num].head(count)
            return related.to_dict('records')

        return []

    except Exception as e:
        logger.error(f"Error finding related grants: {e}")
        return []


def get_pi_portfolio(
    pi_name: str,
    fiscal_years: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Get all grants for a principal investigator.

    Args:
        pi_name: Principal investigator name
        fiscal_years: Optional list of fiscal years to filter

    Returns:
        DataFrame with PI's grants

    Example:
        >>> portfolio = get_pi_portfolio("Smith", fiscal_years=[2023, 2024])
    """
    return query(pi_name=pi_name, fiscal_years=fiscal_years, limit=500)


def get_organization_portfolio(
    org_name: str,
    fiscal_years: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Get all grants for an institution/organization.

    Args:
        org_name: Organization name
        fiscal_years: Optional list of fiscal years to filter

    Returns:
        DataFrame with organization's grants

    Example:
        >>> portfolio = get_organization_portfolio("Harvard University")
    """
    return query(organization=org_name, fiscal_years=fiscal_years, limit=500)


def format_citation(
    row: Union[pd.Series, Dict],
    style: str = 'APA'
) -> str:
    """
    Generate citation for an NIH grant.

    Args:
        row: Grant data (DataFrame row or dictionary)
        style: Citation style - 'APA', 'Vancouver', or 'Bibtex'

    Returns:
        Formatted citation string

    Example:
        >>> citation = format_citation(grant, style='APA')
    """
    # Convert Series to dict if needed
    if isinstance(row, pd.Series):
        data = row.to_dict()
    else:
        data = row

    # Extract fields with defaults
    pi_names = data.get('pi_names', 'N/A')
    title = data.get('title', 'N/A')
    project_num = str(data.get('project_num', 'N/A'))  # Convert to string
    fiscal_year = data.get('fiscal_year', 'N/A')
    award_amount = data.get('award_amount', 0)
    agency = data.get('agency', 'NIH')

    # Format award amount
    amount_str = f"${award_amount:,}" if isinstance(award_amount, (int, float)) else "N/A"

    style = style.upper()

    if style == 'APA':
        # APA format
        return (
            f"{pi_names}. ({fiscal_year}). {title} "
            f"[Grant {project_num}]. Funder: National Institutes of Health ({agency}). "
            f"Award Amount: {amount_str}."
        )

    elif style == 'VANCOUVER':
        # Vancouver format
        return (
            f"{pi_names}. {title}. "
            f"Grant: {project_num}; Funder: NIH ({agency}); "
            f"Year: {fiscal_year}; Award: {amount_str}."
        )

    elif style == 'BIBTEX':
        # Bibtex format
        # Clean up PI names for author field
        first_pi = pi_names.split(';')[0].strip() if ';' in pi_names else pi_names
        # Create citation key
        key = f"NIH{project_num.replace('-', '')}" if project_num != 'N/A' else "NIHGrant"

        return (
            f"@misc{{{key},\n"
            f"  author = {{{first_pi}}},\n"
            f"  title = {{{title}}},\n"
            f"  year = {{{fiscal_year}}},\n"
            f"  note = {{NIH Grant {project_num}, Award: {amount_str}}},\n"
            f"  howpublished = {{National Institutes of Health ({agency})}}\n"
            f"}}"
        )

    else:
        logger.warning(f"Unknown citation style: {style}, using APA")
        return format_citation(row, style='APA')


# ============================================================================
# LangChain Tools
# ============================================================================


@tool
def search_grants(
    keywords: str = "",
    fiscal_year: int = 0,
    pi_name: str = "",
    organization: str = "",
    limit: int = 10
) -> str:
    """
    Search NIH grant proposals by keywords, fiscal year, PI name, or organization.

    This tool searches the NIH RePORTER database and returns grant information.
    You should call this tool directly to find grants - don't just explain how to use it.

    Args:
        keywords: Search terms like "Alzheimer's", "cancer immunotherapy", "CRISPR" (optional)
        fiscal_year: Fiscal year to filter by, e.g. 2023, 2024 (optional, use 0 for no filter)
        pi_name: Principal investigator name (optional)
        organization: Institution name (optional)
        limit: Number of results to return (default 10, max 500)

    Returns:
        Formatted string with grant details including project numbers, titles, PIs, funding amounts

    Example:
        To find Alzheimer's grants from 2023, call:
        search_grants(keywords="Alzheimer's", fiscal_year=2023, limit=10)
    """
    try:
        # Build fiscal_years list if provided
        fiscal_years = [fiscal_year] if fiscal_year > 0 else None

        results = query(
            keywords=keywords if keywords else None,
            pi_name=pi_name if pi_name else None,
            organization=organization if organization else None,
            fiscal_years=fiscal_years,
            limit=limit
        )

        if results.empty:
            return "No grants found matching the criteria."

        output = [f"Found {len(results)} NIH grants:\n"]

        for idx, row in results.iterrows():
            output.append(f"\n{idx + 1}. {row['title']}")
            output.append(f"   Project: {row['project_num']}")
            output.append(f"   PI: {row['contact_pi_name']}")
            output.append(f"   Organization: {row['organization']}")
            output.append(f"   Fiscal Year: {row['fiscal_year']}")
            output.append(f"   Award: ${row['award_amount']:,}")
            output.append(f"   Agency: {row['agency']}")
            output.append(f"   URL: {row['url']}")

            # Include abstract preview
            abstract = row['abstract']
            if abstract and abstract != 'N/A':
                preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
                output.append(f"   Abstract: {preview}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in search_grants tool: {e}")
        return f"Error searching grants: {str(e)}"


@tool
def get_grant_info(project_num: str) -> str:
    """
    Get complete details for a specific NIH grant by project number.

    Use this tool when you need full information about a specific grant,
    including complete abstract, public health relevance, study section,
    and all metadata.

    Args:
        project_num: NIH project/application number (e.g., "5R01CA123456-05")

    Returns:
        Formatted string with complete grant information
    """
    try:
        grant = get_grant_details(project_num)

        if not grant:
            return f"Grant not found: {project_num}"

        output = [
            f"Grant: {grant['title']}",
            f"\nProject Number: {grant['project_num']}",
            f"Principal Investigators: {grant['pi_names']}",
            f"Contact PI: {grant['contact_pi_name']}",
            f"\nOrganization: {grant['organization']}",
            f"Location: {grant['org_city']}, {grant['org_state']}, {grant['org_country']}",
            f"\nFiscal Year: {grant['fiscal_year']}",
            f"Award Amount: ${grant['award_amount']:,}",
            f"Award Date: {grant['award_notice_date']}",
            f"Project Period: {grant['project_start_date']} to {grant['project_end_date']}",
            f"\nAgency: {grant['agency']}",
            f"Activity Code: {grant['activity_code']}",
            f"Opportunity Number: {grant['opportunity_number']}",
            f"Study Section: {grant['full_study_section']}",
            f"\nAbstract:\n{grant['abstract']}",
        ]

        if grant['phr'] and grant['phr'] != 'N/A':
            output.append(f"\nPublic Health Relevance:\n{grant['phr']}")

        output.append(f"\nURL: {grant['url']}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in get_grant_info tool: {e}")
        return f"Error retrieving grant info: {str(e)}"


@tool
def find_pi_grants(pi_name: str, limit: int = 10) -> str:
    """
    Find all grants for a principal investigator.

    Use this tool to get a researcher's funding portfolio and see all
    grants they have received from NIH.

    Args:
        pi_name: Principal investigator name
        limit: Number of results (default 10)

    Returns:
        Formatted string with PI's grants
    """
    try:
        results = get_pi_portfolio(pi_name)
        results = results.head(limit)

        if results.empty:
            return f"No grants found for PI: {pi_name}"

        total_funding = results['award_amount'].sum()
        output = [
            f"Found {len(results)} grants for {pi_name}",
            f"Total funding: ${total_funding:,}\n"
        ]

        for idx, row in results.iterrows():
            output.append(f"\n{idx + 1}. {row['title']}")
            output.append(f"   Project: {row['project_num']}")
            output.append(f"   FY: {row['fiscal_year']} | Award: ${row['award_amount']:,}")
            output.append(f"   Organization: {row['organization']}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in find_pi_grants tool: {e}")
        return f"Error finding PI grants: {str(e)}"


@tool
def cite_grant(project_num: str, style: str = "APA") -> str:
    """
    Generate a citation for an NIH grant.

    Use this tool to create properly formatted citations for grants
    in different citation styles.

    Args:
        project_num: NIH project number
        style: Citation style - "APA", "Vancouver", or "Bibtex" (default "APA")

    Returns:
        Formatted citation
    """
    try:
        grant = get_grant_details(project_num)

        if not grant:
            return f"Grant not found: {project_num}"

        citation = format_citation(grant, style=style)
        return f"{style} citation:\n\n{citation}"

    except Exception as e:
        logger.error(f"Error in cite_grant tool: {e}")
        return f"Error generating citation: {str(e)}"


@tool
def search_and_save_grants(
    keywords: str,
    fiscal_year: int = 0,
    tags: str = "",
    limit: int = 10
) -> str:
    """
    Search NIH grants and save them to the database in one step.

    This tool combines searching and saving. Use this when you want to find
    grants and store them for later reference.

    Args:
        keywords: Search terms like "Alzheimer's", "cancer", "CRISPR"
        fiscal_year: Fiscal year to filter by, e.g. 2023, 2024 (optional, use 0 for all years)
        tags: Comma-separated tags to organize grants (e.g., "alzheimer,neuroscience")
        limit: Number of grants to find and save (default 10)

    Returns:
        Summary of grants found and saved

    Example:
        To find and save Alzheimer's grants from 2023:
        search_and_save_grants(keywords="Alzheimer's", fiscal_year=2023, tags="alzheimer,neuroscience", limit=10)
    """
    try:
        # Search for grants
        fiscal_years = [fiscal_year] if fiscal_year > 0 else None
        results = query(keywords=keywords, fiscal_years=fiscal_years, limit=limit)

        if results.empty:
            return f"No grants found for '{keywords}' in {fiscal_year}"

        # Save to database
        from trion.tools.storage.grants import save_grants_batch
        tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
        stats = save_grants_batch(results, tags=tag_list)

        # Format response
        output = [
            f"Found and processed {len(results)} NIH grants for '{keywords}' from {fiscal_year}:",
            f"\n✓ Saved: {stats['saved']} grants",
            f"✓ Skipped (duplicates): {stats['skipped']}",
            f"\nTop 3 grants:"
        ]

        for idx, row in results.head(3).iterrows():
            output.append(f"\n{idx + 1}. {row['title']}")
            output.append(f"   PI: {row['contact_pi_name']}")
            output.append(f"   Award: ${row['award_amount']:,}")
            output.append(f"   Project: {row['project_num']}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in search_and_save_grants tool: {e}")
        return f"Error: {str(e)}"
