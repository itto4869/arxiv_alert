"""
Utility functions for the arXiv alert system.
"""
import json
import os
import logging
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/arxiv_alert_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def load_config(config_file='config.json'):
    """
    Load configuration from a JSON file.
    
    Args:
        config_file (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading configuration file: {e}")
        raise

def is_weekday():
    """
    Check if today is a weekday (Monday to Friday).
    
    Returns:
        bool: True if today is a weekday, False otherwise
    """
    # Monday = 0, Sunday = 6
    return datetime.now().weekday() < 5

def format_authors(authors, max_authors=3):
    """
    Format the list of authors for display.
    
    Args:
        authors (list): List of author names
        max_authors (int): Maximum number of authors to display before using "et al."
        
    Returns:
        str: Formatted author string
    """
    if not authors:
        return "Unknown"
    
    if len(authors) <= max_authors:
        return ", ".join(authors)
    else:
        return f"{', '.join(authors[:max_authors])} et al."
