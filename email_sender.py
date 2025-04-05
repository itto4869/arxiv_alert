"""
Module for formatting and sending emails with arXiv paper information.
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from jinja2 import Template

logger = logging.getLogger(__name__)

# HTML template for the email
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #0066cc;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        h2 {
            color: #0066cc;
            margin-top: 20px;
        }
        .paper {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .authors {
            color: #666;
            font-style: italic;
        }
        .abstract {
            margin-top: 10px;
            text-align: justify;
        }
        .link {
            margin-top: 10px;
        }
        .link a {
            color: #0066cc;
            text-decoration: none;
        }
        .link a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: 30px;
            font-size: 0.8em;
            color: #999;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>arXiv Paper Alert - {{ date }}</h1>
    
    <p>The following papers match your search criteria:</p>
    
    {% for paper in papers %}
    <div class="paper">
        <h2>{{ paper.title }}</h2>
        <div class="authors">{{ paper.authors|join(', ') }}</div>
        <div class="abstract">{{ paper.abstract }}</div>
        <div class="link"><a href="{{ paper.link }}">Read on arXiv</a></div>
    </div>
    {% endfor %}
    
    <div class="footer">
        <p>This email was sent automatically by arXiv Alert.</p>
        <p>Keywords: {{ keywords }}</p>
    </div>
</body>
</html>
"""

def format_email_content(papers, keyword_groups):
    """
    Format the email content with the matched papers.
    
    Args:
        papers (list): List of paper dictionaries
        keyword_groups (list): List of keyword groups used for searching
        
    Returns:
        str: HTML content for the email
    """
    # Format the keywords for display
    keywords_display = []
    for group in keyword_groups:
        keywords_display.append(f"({' OR '.join(group)})")
    keywords_str = ' AND '.join(keywords_display)
    
    # Render the template
    template = Template(EMAIL_TEMPLATE)
    html_content = template.render(
        papers=papers,
        date=datetime.now().strftime("%Y-%m-%d"),
        keywords=keywords_str
    )
    
    return html_content

def send_email(config, papers, keyword_groups):
    """
    Send an email with the matched papers.
    
    Args:
        config (dict): Email configuration
        papers (list): List of paper dictionaries
        keyword_groups (list): List of keyword groups used for searching
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    if not papers:
        logger.info("No papers to send, skipping email")
        return True
    
    # Extract email configuration
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    sender_email = config['sender_email']
    app_password = config['app_password']
    recipients = config['recipients']
    
    # Format the email content
    html_content = format_email_content(papers, keyword_groups)
    
    # Create the email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"arXiv Paper Alert - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    
    # Attach the HTML content
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login to the SMTP server
        server.login(sender_email, app_password)
        
        # Send the email
        server.sendmail(sender_email, recipients, msg.as_string())
        
        # Close the connection
        server.quit()
        
        logger.info(f"Email sent successfully to {len(recipients)} recipients")
        return True
    
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False
