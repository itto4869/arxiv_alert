#!/usr/bin/env python3
"""
arXiv Alert - A tool to fetch and email arXiv papers based on keywords.

This script fetches the latest papers from arXiv in the specified categories,
searches for papers matching the configured keywords, and sends an email
with the matching papers.

Usage:
    python arxiv_alert.py [--config CONFIG_FILE] [--dry-run] [--list-papers]

Options:
    --config CONFIG_FILE    Path to the configuration file (default: config.json)
    --dry-run               Run without sending emails (for testing)
    --list-papers           List all fetched papers (for debugging)
"""

import argparse
import logging
import sys
from datetime import datetime

from arxiv_api import fetch_papers, filter_papers_by_date, fetch_papers_from_rss
from search import search_papers, load_sent_papers, save_sent_papers
from email_sender import send_email
from utils import setup_logging, load_config, is_weekday

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Fetch and email arXiv papers based on keywords.')
    parser.add_argument('--config', default='config.json', help='Path to the configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Run without sending emails')
    parser.add_argument('--list-papers', action='store_true', help='List all fetched papers')
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting arXiv Alert")
    
    # Check if today is a weekday
    if not is_weekday():
        logger.info("Today is not a weekday, exiting")
        return
    
    try:
        # Load configuration
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
        
        # Extract configuration
        arxiv_config = config.get('arxiv', {})
        search_config = config.get('search', {})
        email_config = config.get('email', {})
        history_config = config.get('history', {})
        
        # Load history of sent papers
        history_file = history_config.get('file', 'sent_papers.json')
        sent_papers = load_sent_papers(history_file)
        logger.info(f"Loaded {len(sent_papers)} previously sent papers from {history_file}")
        
        # Fetch papers from arXiv
        categories = arxiv_config.get('categories', ['cs.LG'])
        max_results = arxiv_config.get('max_results', 50)
        use_rss = arxiv_config.get('use_rss', True)  # New config option
        
        if use_rss:
            # Use optimized API query to get the most recent submissions
            logger.info("Using optimized API query to fetch the most recent papers")
            papers = fetch_papers_from_rss(categories, max_results)
        else:
            # Use the standard API with date filtering
            logger.info("Using standard API query with date filtering")
            papers = fetch_papers(categories, max_results)
            
            # Filter papers by date
            # For production, use 1 day to get the last 24 hours
            # For testing, we can use more days to ensure we have some papers
            days_to_filter = 1 if args.dry_run else 1
            papers = filter_papers_by_date(papers, days=days_to_filter)
        
        # List all fetched papers if requested
        if args.list_papers:
            logger.info(f"Listing all {len(papers)} fetched papers:")
            for i, paper in enumerate(papers, 1):
                logger.info(f"Paper {i}: {paper['title']} by {', '.join(paper['authors'][:3])}")
        
        # Search for papers matching the keywords
        keyword_groups = search_config.get('keyword_groups', [])
        search_title = search_config.get('search_title', True)
        search_abstract = search_config.get('search_abstract', True)
        
        matched_papers = search_papers(
            papers,
            keyword_groups,
            search_title,
            search_abstract,
            sent_papers
        )
        
        # Send email with matched papers
        if matched_papers:
            if args.dry_run:
                logger.info(f"DRY RUN: Would send email with {len(matched_papers)} matched papers")
                # Print matched papers for inspection
                for i, paper in enumerate(matched_papers, 1):
                    logger.info(f"Paper {i}: {paper['title']} by {', '.join(paper['authors'][:3])}")
                success = True
            else:
                logger.info(f"Sending email with {len(matched_papers)} matched papers")
                success = send_email(email_config, matched_papers, keyword_groups)
            
            # Update sent papers history if email was sent successfully
            if success and not args.dry_run:
                for paper in matched_papers:
                    sent_papers.add(paper['id'])
                save_sent_papers(history_file, sent_papers)
                logger.info(f"Updated sent papers history ({len(sent_papers)} papers)")
        else:
            logger.info("No papers matched the search criteria")
        
        logger.info("arXiv Alert completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
