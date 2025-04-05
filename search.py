"""
Module for searching and filtering arXiv papers based on keywords.
"""
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def load_sent_papers(history_file):
    """
    Load the history of previously sent papers.
    
    Args:
        history_file (str): Path to the history file
        
    Returns:
        set: Set of paper IDs that have been sent
    """
    if not os.path.exists(history_file):
        return set()
    
    try:
        with open(history_file, 'r') as f:
            history = json.load(f)
            return set(history.get('sent_papers', []))
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading history file: {e}")
        return set()

def save_sent_papers(history_file, sent_papers):
    """
    Save the updated history of sent papers.
    
    Args:
        history_file (str): Path to the history file
        sent_papers (set): Set of paper IDs that have been sent
    """
    history_dir = os.path.dirname(history_file)
    if history_dir and not os.path.exists(history_dir):
        os.makedirs(history_dir)
    
    try:
        history = {
            'sent_papers': list(sent_papers),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving history file: {e}")

def search_papers(papers, keyword_groups, search_title=True, search_abstract=True, sent_papers=None):
    """
    Search papers for keyword matches.
    
    Args:
        papers (list): List of paper dictionaries
        keyword_groups (list): List of keyword groups, where each group is a list of keywords
                              Papers must match all keywords within a group (AND)
                              Papers must match at least one group (OR)
        search_title (bool): Whether to search in the title
        search_abstract (bool): Whether to search in the abstract
        sent_papers (set): Set of paper IDs that have already been sent
        
    Returns:
        list: List of papers that match the search criteria
    """
    if sent_papers is None:
        sent_papers = set()
    
    matched_papers = []
    
    for paper in papers:
        # Skip papers that have already been sent
        if paper['id'] in sent_papers:
            continue
        
        # Skip if we're not searching in either title or abstract
        if not search_title and not search_abstract:
            continue
        
        # Prepare the text to search in
        search_text = ""
        if search_title:
            search_text += paper['title'].lower() + " "
        if search_abstract:
            search_text += paper['abstract'].lower()
        
        # Check if the paper matches any keyword group
        for keyword_group in keyword_groups:
            # Check if ALL keywords in this group match (AND within group)
            all_keywords_match = True
            
            for keyword in keyword_group:
                if keyword.lower() not in search_text:
                    all_keywords_match = False
                    break
            
            # If all keywords in this group match, add the paper and move to next paper (OR between groups)
            if all_keywords_match:
                matched_papers.append(paper)
                break  # No need to check other groups
    
    logger.info(f"Found {len(matched_papers)} papers matching the search criteria")
    return matched_papers
