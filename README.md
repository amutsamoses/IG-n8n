InstagramAuto: Drip Messaging & Lead Gen
An automated outreach and lead management system that segments users via AI and executes a timed "drip" messaging sequence. This tool integrates Google Sheets for tracking, Apify/LLMs for data enrichment, and Visual Studio for workflow development.

🚀 Features
Lead Scraping & Segmentation: Uses Apify and LLMs to gather engagement data (likes/comments) and segment leads by demographics.

Smart Drip System:

Sends a sequence of messages based on a predefined schedule.

Implements a mandatory delay (e.g., 3 days) between messages.

Automated Tracking: Logs last_message_date and message_number directly to Google Sheets.

Reply Detection: Automatically stops sequences for users who have replied or completed the drip.

Data Enrichment: Exporting engaged audience data into Excel/Google Sheets for further analysis.

🛠️ Tech Stack
Language: Python / Node.js

Database: Google Sheets API (via gspread)

AI/Scraping: Apify, GPT/LLM Integration

IDE: Visual Studio Code

📋 Prerequisites
Before running the script, ensure you have:

Google Cloud Console credentials (service_account.json) for Sheets access.

API Keys for Apify and your chosen LLM (OpenAI/Gemini).

The following Python packages:

Bash
pip install gspread oauth2client pandas openai
⚙️ Configuration
Google Sheet Setup: Your sheet should have the following headers:
| Username | Last Message Date | Message Number | Status | Demographics |
| :--- | :--- | :--- | :--- | :--- |
| user_123 | 2026-02-13 | 1 | Pending | Tech/USA |

Environment Variables: Create a .env file:

Code snippet
APIFY_API_TOKEN=your_token
LLM_API_KEY=your_key
SHEET_ID=your_google_sheet_id
📈 Workflow Logic
Scrape: Pull followers/engagers via Apify.

Segment: LLM analyzes profile data to categorize leads.

Check: Script reads the Google Sheet to identify who is due for a message.

Send: If Current Date - Last Message Date >= 3 days, send Message Number + 1.

Update: Mark the new timestamp and increment the message count in the sheet.

⚠️ Safety Disclaimer
This tool is for educational/internal research purposes. Automated interaction with social media platforms must comply with their respective Terms of Service to avoid account suspension.