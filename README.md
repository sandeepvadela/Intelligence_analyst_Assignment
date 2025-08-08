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
Weekday 
WeekdayNum 
```

---

## Insights 
- High transaction count with moderate average ticket size indicates a high-volume, low-value processing model typical for large payment ecosystems.
- PJ customers dominate TPV; stability and service quality here are crucial for revenue protection.
- POS and Tap together drive ~75% of TPV. Pix and Link are growing digital channels worth expanding; Bank Slip is negligible.
- Likely seasonal or campaign-driven peaks , align promos  with these periods.
- Thursday–Friday–Monday are high-demand days; Sunday is the downtime opportunity for maintenance.
- PF customers spend more per transaction ,good segment for high-value promotions.
- Bank Slip and Link are premium-ticket channels; POS and Pix are high-volume but low-ticket.
- Credit has both highest TPV share and highest average ticket reinforcing its strategic importance.
- Most volume is in the normal pricing tier ,price optimizations here can have the largest impact.
- PJ customers are heavy D1 users; PF shows balanced D1/D0 usage.
- Transaction volume distribution mirrors TPV distribution ,normal tier dominates.

## Gmail KPI Bot (Detailed)
A simple Python bot that reads the CSV, computes KPIs, compares with the previous day, detects anomalies, and emails a summary via Gmail.

### Files
- `simple_gmail_kpi_bot.py`  (main bot)
- `Operations_analyst_data - Copy.csv` (data)


### How It Works
- load_data()
  - Reads the CSV with 
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

- Gmail App Password
  - Enable 2-Step Verification in Google Account
  - Create an App Password 
  

### Configuration
```
GMAIL_CONFIG = {
  'smtp_server': 'smtp.gmail.com',
  'smtp_port': 587,
  'sender_email': 'your_email@gmail.com',
  'password': 'app_password',
  'recipient_email': 'recipient@example.com'
}

bot = SimpleGmailKPIBot('Cleaned_Operations_analyst_data .csv')
bot.run_daily_report(gmail_config=GMAIL_CONFIG)
```


### Running
- Manual run:
  ```
  python simple_gmail_kpi_bot.py
  ```
- Expected console output:
  - Data loaded successfully
  - Gmail sent successfully!

### Extensibility
- Add new KPIs: extend `calculate_kpis`
- Add new alerts: update `detect_alerts`
- Change recipients: edit `recipient_email` or send to a list
- Add weekly/monthly modes: compute aggregates over ranges

---

## Deliverables Summary
- Power BI dashboard with KPI cards and analytical visuals (entity, product, payment method, weekday, installments, price tier, anticipation method)
- Python Gmail-only bot for daily KPI emails and alerts

