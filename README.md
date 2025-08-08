## Business Intelligence & AI Automation Project

### Overview
This project delivers a complete BI solution with:
- Power BI dashboard for KPIs and exploratory analysis
- A Python-based Gmail-only bot that sends daily KPI summaries and alerts

### Dataset
- Source: `Cleaned_Operations_Analyst_Data.csv`
- Key columns: `day`, `entity`, `product`, `price_tier`, `anticipation_method`, `payment_method`, `installments`, `amount_transacted`, `quantity_transactions`, `quantity_of_merchants`

---

## Power BI Visuals (Brief)
These visuals enable answering core business questions.

- KPI Cards
- TPV, Average Ticket, Total Transactions, Total Merchants
- TPV by Entity
- TPV by Product
- TPV by Payment Method
- TPV Trend Over Time
- TPV by Weekday
- Average Ticket by Entity
- Top Products By Average Ticket
- Average Ticket by Payment Method
- TPV By price Tier
- TPV by Installments
- Total Transactions by Price Tier
- Avg Ticket Top N
- Anticipation Method Usage by Entity
  

DAX Measures used:
```
TPV 
Average Ticket 
Total Transactions 
Total Merchants 
```

Optional calculated columns:
```
Weekday = FORMAT('Operations_analyst_data - Copy'[day], "dddd")
WeekdayNum = WEEKDAY('Operations_analyst_data - Copy'[day], 2)  // Monday=1 ... Sunday=7
```

---

## Gmail KPI Bot (Detailed)
A simple Python bot that reads the CSV, computes KPIs, compares with the previous day, detects anomalies, and emails a summary via Gmail.

### Files
- `simple_gmail_kpi_bot.py`  (main bot)
- `Operations_analyst_data - Copy.csv` (data)
- `requirements.txt` (dependencies)

### How It Works
- load_data()
  - Reads the CSV with `parse_dates=['day']`
  - Stores the latest date in the dataset for analysis
- calculate_kpis(target_date)
  - Computes for a given date:
    - TPV (sum of `amount_transacted`)
    - Average Ticket (TPV / `quantity_transactions`)
    - Total Transactions (sum of `quantity_transactions`)
    - Total Merchants (sum of `quantity_of_merchants`)
    - Breakdowns: TPV by `entity`, `product`, `payment_method`
- calculate_growth(current_kpis, previous_kpis)
  - Percentage change for TPV, Average Ticket, Total Transactions (vs previous day)
- detect_alerts(current_kpis, previous_kpis, growth_rates)
  - Alerts if: TPV ↓ >20%, Avg Ticket ↓ >15%, Transactions ↓ >25%, or zero transactions
- generate_email_summary(current_kpis, growth_rates, alerts)
  - Builds a readable text email with metrics, growth, top performers, and alerts
- send_gmail(subject, message, gmail_config)
  - Sends the email via Gmail SMTP with TLS and App Password authentication
- run_daily_report(gmail_config)
  - Orchestrates the full workflow and sends the email

### Setup
- Requirements
  - Python 3.9+
  - Install deps:
    ```
    pip install -r requirements.txt
    ```
- Gmail App Password
  - Enable 2-Step Verification in Google Account
  - Create an App Password (select "Mail" → device = Other → name it e.g. "KPI Bot")
  - Copy the 16-character password

### Configuration
Edit `simple_gmail_kpi_bot.py` (bottom section):
```
GMAIL_CONFIG = {
  'smtp_server': 'smtp.gmail.com',
  'smtp_port': 587,
  'sender_email': 'your_email@gmail.com',
  'password': 'your_16_char_app_password',
  'recipient_email': 'recipient@example.com'
}

bot = SimpleGmailKPIBot('Operations_analyst_data - Copy.csv')
bot.run_daily_report(gmail_config=GMAIL_CONFIG)
```

Tip (optional): store secrets in environment variables instead of in code.

### Running
- Manual run:
  ```
  python simple_gmail_kpi_bot.py
  ```
- Expected console output:
  - Data loaded successfully
  - Gmail sent successfully!

### Scheduling (Windows Task Scheduler)
- Open Task Scheduler → Create Basic Task
- Trigger: Daily at desired time
- Action: Start a program
  - Program/script: `python`
  - Add arguments: `simple_gmail_kpi_bot.py`
  - Start in: the project folder path
- Ensure your Python and CSV paths are correct and accessible to the task user

### Troubleshooting
- ModuleNotFoundError (e.g., pandas)
  - Run `pip install -r requirements.txt`
- Gmail auth error
  - Use an App Password (not your regular password)
  - Verify `smtp.gmail.com:587` and TLS (starttls)
- No data found for latest day
  - Check the `day` column is parsed as Date and matches available dates
- Email sent but not received
  - Check Spam folder / filters
  - Verify recipient address

### Extensibility
- Add new KPIs: extend `calculate_kpis`
- Add new alerts: update `detect_alerts`
- Change recipients: edit `recipient_email` or send to a list
- Add weekly/monthly modes: compute aggregates over ranges

---

## Deliverables Summary
- Power BI dashboard with KPI cards and analytical visuals (entity, product, payment method, weekday, installments, price tier, anticipation method)
- Python Gmail-only bot for daily KPI emails and alerts
- Setup and scheduling instructions to run unattended
