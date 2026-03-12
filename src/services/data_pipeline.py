"""
Service for cleaning and inserting raw JSON data into the database.
Orchestrates the validation and insertion pipeline.
"""

import json
import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rich.console import Console
from src.validation import validate_fields, normalize_json
from db.connection import get_session, init_db
from db.service import insert_company_bundle

console = Console()


def load_data_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load and parse data.json file.

    Args:
        file_path: Path to the data.json file

    Returns:
        List of company data dictionaries

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def clean_and_insert_data(data_json_path: str = None) -> Dict[str, Any]:
    """
    Main pipeline function: Load -> Validate -> Normalize -> Insert.

    This function mimics the test_insertion.py workflow but returns results
    instead of printing them.

    Args:
        data_json_path: Path to data.json file. If None, uses default location.

    Returns:
        Dict with summary of results:
        {
            'total_processed': int,
            'successful': int,
            'failed': int,
            'total_emails': int,
            'total_recruiters': int,
            'total_recruiter_emails': int,
            'total_jobs': int,
            'failed_companies': [list of dicts with error info],
            'error': str | None  # Overall error if pipeline fails
        }
    """
    result = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'total_emails': 0,
        'total_recruiters': 0,
        'total_recruiter_emails': 0,
        'total_jobs': 0,
        'failed_companies': [],
        'error': None
    }

    try:
        # Step 1: Initialize database (create tables if needed)
        init_db()

        # Step 2: Load data.json
        if data_json_path is None:
            data_json_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data.json'
            )

        raw_data = load_data_json(data_json_path)
        result['total_processed'] = len(raw_data)

        # Step 3: Validate fields
        validated_data = validate_fields(raw_data)

        # Step 4: Normalize to SQLAlchemy objects
        bundles = normalize_json(validated_data)

        # Step 5: Insert into database
        insertion_results = []
        for bundle in bundles:
            with get_session() as session:
                try:
                    insert_result = insert_company_bundle(bundle, session)
                    session.commit()
                    insertion_results.append(insert_result)

                    if insert_result.get('success'):
                        result['successful'] += 1
                        result['total_emails'] += insert_result.get('emails_inserted', 0)
                        result['total_recruiters'] += insert_result.get('recruiters_inserted', 0)
                        result['total_recruiter_emails'] += insert_result.get('recruiter_emails_inserted', 0)
                        result['total_jobs'] += insert_result.get('jobs_inserted', 0)
                    else:
                        result['failed'] += 1
                        result['failed_companies'].append({
                            'company_name': insert_result.get('company_name'),
                            'error': insert_result.get('error')
                        })

                except Exception as e:
                    session.rollback()
                    result['failed'] += 1
                    result['failed_companies'].append({
                        'company_name': bundle.company.cname,
                        'error': str(e)
                    })

        return result

    except FileNotFoundError as e:
        result['error'] = f"File not found: {e}"
        return result
    except json.JSONDecodeError as e:
        result['error'] = f"Invalid JSON: {e}"
        return result
    except Exception as e:
        result['error'] = f"Unexpected error: {e}"
        return result


def run_clean_and_insert_with_display(data_json_path: str = None) -> Dict[str, Any]:
    """
    Run the clean and insert pipeline with rich console output.

    Args:
        data_json_path: Path to data.json file. If None, uses default location.

    Returns:
        Dict with summary of results from clean_and_insert_data()
    """
    console.print("[cyan]Starting data cleaning and insertion pipeline...[/cyan]\n")

    try:
        # Run the pipeline
        result = clean_and_insert_data(data_json_path)

        # Check for overall pipeline error
        if result.get('error'):
            console.print(f"[red]Pipeline failed: {result['error']}[/red]")
            return result

        # Display results
        console.print("[bold]Pipeline Summary:[/bold]")
        console.print(f"  Total companies processed: {result['total_processed']}")
        console.print(f"  [green]Successful insertions: {result['successful']}[/green]")
        console.print(f"  [red]Failed insertions: {result['failed']}[/red]\n")

        if result['successful'] > 0:
            console.print("[bold]Inserted Entities:[/bold]")
            console.print(f"  Companies: {result['successful']}")
            console.print(f"  Emails: {result['total_emails']}")
            console.print(f"  Recruiters: {result['total_recruiters']}")
            console.print(f"  Recruiter Emails: {result['total_recruiter_emails']}")
            console.print(f"  Jobs: {result['total_jobs']}\n")

        if result['failed_companies']:
            console.print("[bold red]Failed Companies:[/bold red]")
            for failed in result['failed_companies']:
                console.print(f"  - {failed['company_name']}: {failed['error']}")
            console.print()

        console.print("[green]Data cleaning and insertion complete![/green]\n")

        return result

    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]\n")
        return {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'total_emails': 0,
            'total_recruiters': 0,
            'total_recruiter_emails': 0,
            'total_jobs': 0,
            'failed_companies': [],
            'error': str(e)
        }
