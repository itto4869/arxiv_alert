"""
Module for interacting with the arXiv API and RSS feeds to fetch papers.
"""
import feedparser
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def fetch_papers(categories, max_results=50):
    """
    Fetch papers from arXiv API for the specified categories.
    
    Args:
        categories (list): List of arXiv categories (e.g., ["cs.LG"])
        max_results (int): Maximum number of results to fetch
        
    Returns:
        list: List of paper dictionaries with title, abstract, authors, etc.
    """
    # Construct the query URL
    category_query = " OR ".join(f"cat:{cat}" for cat in categories)
    base_url = "https://export.arxiv.org/api/query?"
    
    # Get papers from the last 24 hours
    # ArXiv API doesn't have a direct "last 24 hours" filter, so we'll fetch recent papers
    # and filter by date later if needed
    query = f"search_query={category_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    url = base_url + query
    
    logger.info(f"Fetching papers from arXiv API: {url}")
    
    # Add a small delay to be nice to the API
    time.sleep(1)
    
    # Fetch and parse the feed
    feed = feedparser.parse(url)
    
    if hasattr(feed, 'status') and feed.status != 200:
        logger.error(f"Error fetching arXiv feed: {feed.get('status', 'Unknown error')}")
        return []
    
    # Process the entries
    papers = []
    for entry in feed.entries:
        # Extract paper details
        paper = {
            'id': entry.id.split('/abs/')[-1],
            'title': entry.title.replace('\n', ' ').strip(),
            'abstract': entry.summary.replace('\n', ' ').strip(),
            'authors': [author.name for author in entry.authors],
            'link': entry.link,
            'published': entry.published,
            'updated': entry.updated,
            'categories': [tag['term'] for tag in entry.tags],
        }
        papers.append(paper)
    
    logger.info(f"Fetched {len(papers)} papers from arXiv")
    return papers

def filter_papers_by_date(papers, days=1):
    """
    Filter papers to only include those published within the specified number of days.
    
    Args:
        papers (list): List of paper dictionaries
        days (int): Number of days to look back
        
    Returns:
        list: Filtered list of papers
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    filtered_papers = []
    for paper in papers:
        # Parse the published date
        published_date = datetime.strptime(paper['published'], "%Y-%m-%dT%H:%M:%SZ")
        
        if published_date >= cutoff_date:
            filtered_papers.append(paper)
    
    logger.info(f"Filtered to {len(filtered_papers)} papers published in the last {days} days")
    return filtered_papers

def fetch_papers_from_rss(categories, max_results=50):
    """
    Fetch the most recent papers for the specified categories using the arXiv API.
    
    This function uses the arXiv API to get the most recent submissions, which
    addresses the gap between paper publication and appearance on arXiv.
    
    Args:
        categories (list): List of arXiv categories (e.g., ["cs.LG"])
        max_results (int): Maximum number of results to fetch
        
    Returns:
        list: List of paper dictionaries with title, abstract, authors, etc.
    """
    # Construct the query URL for recent submissions
    category_query = " OR ".join(f"cat:{cat}" for cat in categories)
    base_url = "https://export.arxiv.org/api/query?"
    
    # Use the 'submittedDate' sort parameter to get the most recent submissions
    query = f"search_query={category_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    url = base_url + query
    
    logger.info(f"Fetching recent papers from arXiv API: {url}")
    
    # Add a small delay to be nice to the API
    time.sleep(1)
    
    # Fetch and parse the feed
    feed = feedparser.parse(url)
    
    if hasattr(feed, 'status') and feed.status != 200:
        logger.error(f"Error fetching arXiv feed: {feed.get('status', 'Unknown error')}")
        return []
    
    # Process the entries
    papers = []
    for entry in feed.entries:
        # Extract paper details
        paper = {
            'id': entry.id.split('/abs/')[-1],
            'title': entry.title.replace('\n', ' ').strip(),
            'abstract': entry.summary.replace('\n', ' ').strip(),
            'authors': [author.name for author in entry.authors],
            'link': entry.link,
            'published': entry.published,
            'updated': entry.updated,
            'categories': [tag['term'] for tag in entry.tags],
        }
        papers.append(paper)
    
    logger.info(f"Fetched {len(papers)} recent papers from arXiv")
    return papers
