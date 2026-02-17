# InstagramAuto: Drip Messaging & AI-Powered Lead Engine

An automated outreach system that captures engaged Instagram users, segments them using AI, and executes a deterministic drip messaging sequence with state tracking in Google Sheets.

The system is designed around one principle:

> Outreach is a state machine.
> Every user exists in a measurable stage.
> Transitions are triggered by time or reply events.

---

## System Architecture

```
Instagram Engagement → Apify Scraper → Data Enrichment (LLM)
        ↓
Excel / Google Sheets (State Store)
        ↓
Drip Engine (Scheduler + Logic)
        ↓
Instagram Messaging API / Automation Layer
        ↓
Sheet Update (Message # + Timestamp + Status)
```

---

## Core Capabilities

### 1. Engagement Data Collection

* Scrapes likes/comments using Apify actors
* Exports raw engagement data to Excel or Google Sheets
* Normalizes usernames and metadata
* Deduplicates existing leads

---

### 2. AI Segmentation Engine

Uses GPT/LLM to:

* Classify users by demographics
* Identify industry / interests
* Infer likely buyer intent
* Tag leads for messaging personalization

Example segmentation output:

```json
{
  "industry": "Tech",
  "location": "USA",
  "persona": "Founder",
  "intent_score": 0.82
}
```

This data is stored in the `Demographics` column.

---

### 3. Drip Messaging System (State Machine)

The drip engine follows deterministic logic.

Each user has tracked state:

| Username | Last Message Date | Message Number | Status | Demographics |
| -------- | ----------------- | -------------- | ------ | ------------ |

---

## Drip Logic

### Step 1 — New User

* If `Message Number = 0`
* Send Message #1 immediately
* Update:

  * `Message Number = 1`
  * `Last Message Date = now`

---

### Step 2 — Scheduled Follow-up

If:

```
Current Date - Last Message Date ≥ Delay (e.g., 3 days)
AND Status != Replied
AND Message Number < Max Sequence
```

Then:

* Send next message
* Increment `Message Number`
* Update timestamp

---

### Step 3 — Stop Conditions

Sequence halts if:

* User replies
* Status marked "Replied"
* Max message count reached
* User manually flagged "Stop"
* Account compliance rule triggered

---

## Drip Example Timeline

| Day | Action                       |
| --- | ---------------------------- |
| 0   | Send Message 1               |
| 3   | Send Message 2 (if no reply) |
| 6   | Send Message 3               |
| 9   | Final message                |
| Any | Stop if reply detected       |

---

## Message Sequence Structure

Example:

```
Message 1: Soft introduction
Message 2: Value-driven insight
Message 3: Social proof
Message 4: Direct CTA
```

Each message can be:

* Static template
* Dynamically personalized using LLM
* Segmentation-aware

---

## Tech Stack

| Layer           | Technology                  |
| --------------- | --------------------------- |
| Language        | Python / Node.js            |
| Data Store      | Google Sheets API (gspread) |
| Scraping        | Apify                       |
| AI              | OpenAI / Gemini / Any LLM   |
| Dev Environment | Visual Studio Code          |
| Data Analysis   | Excel / Pandas              |

---

## Installation

### 1. Install Dependencies

```bash
pip install gspread oauth2client pandas openai python-dotenv apify-client
```

---

### 2. Configure Google Sheets

Enable:

* Google Sheets API
* Service Account Credentials

Download:

```
service_account.json
```

Share the sheet with the service account email.

---

### 3. Environment Variables

Create `.env`

```
APIFY_API_TOKEN=your_token
LLM_API_KEY=your_key
SHEET_ID=your_sheet_id
DELAY_DAYS=3
MAX_SEQUENCE=4
```

---

## Workflow Execution

### 1. Scrape Engaged Audience

* Pull likes/comments via Apify
* Export to Sheet
* Remove duplicates

### 2. Enrich with AI

* Pass user bios to LLM
* Generate demographic tags
* Update `Demographics` column

### 3. Run Drip Engine

Scheduler logic:

```python
for each user:
    if status == "Replied":
        continue

    if message_number == 0:
        send_message(1)

    elif days_since_last_message >= DELAY:
        send_message(message_number + 1)

    update_sheet()
```

---

## Google Sheet Schema

Required Headers:

| Column Name       | Description                   |
| ----------------- | ----------------------------- |
| Username          | Instagram handle              |
| Last Message Date | ISO timestamp                 |
| Message Number    | Current stage                 |
| Status            | Pending / Replied / Completed |
| Demographics      | AI-generated segmentation     |
| Reply Detected    | Boolean                       |

---

## Reply Detection Logic

Possible implementations:

* Manual tagging in sheet
* Instagram inbox scraping
* Webhook listener (if API access exists)

When reply detected:

```
Status = Replied
Stop sequence
```

---

## Excel Data Usage

Excel sheets are used for:

* Engagement analysis
* Conversion tracking
* Segment performance comparison
* A/B testing message sequences

---

## Compliance & Risk Controls

* Enforce daily send limits
* Randomized delay jitter (avoid fixed intervals)
* Rate limiting
* Manual override system
* Respect platform Terms of Service

---

## Development Approach (Visual Studio)

Recommended modular structure:

```
/scraper
/segmentation
/drip_engine
/sheets
/config
```

Best practices:

* Use environment-based configuration
* Separate business logic from messaging transport
* Implement structured logging
* Add error handling and retry logic

---

## Future Improvements

* CRM migration (PostgreSQL)
* Dashboard (React + FastAPI)
* Multi-platform messaging
* Conversion analytics engine
* AI-optimized timing prediction

---

## Safety Notice

Automated messaging systems must comply with platform policies and legal regulations. Misuse can lead to account suspension or legal action. Use responsibly.

---

## Philosophy

This is not bulk messaging.

It is:

* Structured
* Measured
* State-driven
* AI-assisted

Every user is a tracked entity.
Every message is a transition.
Every transition is logged.
