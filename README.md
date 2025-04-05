# arXiv Alert

A tool to fetch the latest papers from arXiv's cs.LG category and send email alerts for papers matching specific keywords.

## Features

- Fetches the latest papers from arXiv's cs.LG (Machine Learning) category
- Searches for papers matching configured keywords in both titles and abstracts
- Supports AND operations between multiple keyword groups
- Sends formatted HTML emails with paper details via Gmail SMTP
- Tracks previously sent papers to avoid duplicates
- Designed to run daily on weekdays at 10 PM via an external scheduler

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/arxiv-alert.git
   cd arxiv-alert
   ```

2. Install the required dependencies:
   ```
   pip install -e .
   ```

## Configuration

Create a `config.json` file with the following structure:

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "app_password": "your-app-password",
    "recipients": ["recipient@example.com"]
  },
  "arxiv": {
    "categories": ["cs.LG"],
    "max_results": 50
  },
  "search": {
    "keyword_groups": [
      ["reinforcement learning", "RL"],
      ["transformer", "attention", "large language model"],
      ["graph neural network", "GNN"]
    ],
    "search_title": true,
    "search_abstract": true
  },
  "history": {
    "file": "sent_papers.json"
  }
}
```

### Configuration Options

- **email**: Email settings
  - `smtp_server`: SMTP server address
  - `smtp_port`: SMTP server port
  - `sender_email`: Your Gmail address
  - `app_password`: Your Gmail app password (not your regular password)
  - `recipients`: List of email addresses to receive alerts

- **arxiv**: arXiv API settings
  - `categories`: List of arXiv categories to fetch papers from
  - `max_results`: Maximum number of results to fetch
  - `use_rss`: Whether to use an optimized API query for the most recent submissions (recommended for getting the most recent papers)

- **search**: Search settings
  - `keyword_groups`: List of keyword groups. Each group is a list of keywords.
    - Papers must match all keywords within a group (AND operation within a group)
    - Papers must match at least one group (OR operation between groups)
  - `search_title`: Whether to search in the title
  - `search_abstract`: Whether to search in the abstract

- **history**: History settings
  - `file`: Path to the file to store the history of sent papers

## Gmail App Password

To use Gmail SMTP, you need to create an app password:

1. Go to your Google Account settings
2. Navigate to Security > 2-Step Verification
3. Scroll down and select "App passwords"
4. Generate a new app password for "Mail" and "Other (Custom name)"
5. Use this password in your configuration file

## Usage

Run the script manually:

```
python arxiv_alert.py
```

With a custom configuration file:

```
python arxiv_alert.py --config my_config.json
```

Test without sending emails (dry run):

```
python arxiv_alert.py --dry-run
```

List all fetched papers (for debugging):

```
python arxiv_alert.py --list-papers
```

## Scheduling

To run the script daily at 10 PM on weekdays, set up a cron job:

```
0 22 * * 1-5 /path/to/python /path/to/arxiv_alert.py
```

## Project Structure

- `arxiv_alert.py`: Main script
- `arxiv_api.py`: arXiv API interaction
- `email_sender.py`: Email formatting and sending
- `search.py`: Keyword search implementation
- `utils.py`: Utility functions
- `config.json`: Configuration file

## License

MIT
