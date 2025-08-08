
import pandas as pd  
from datetime import datetime, timedelta 
import smtplib  # For sending emails via Gmail
from email.mime.text import MIMEText  # For creating email content
from email.mime.multipart import MIMEMultipart  # For HTML + text emails

class SimpleGmailKPIBot:
   
    
    def __init__(self, csv_file_path):
        
        self.csv_file_path = csv_file_path  
        self.df = None  # Will store the loaded data
        self.latest_day = None  # Will store the most recent date in data
        
    def load_data(self):
       
        try:
            
            self.df = pd.read_csv(self.csv_file_path, parse_dates=['day'])
            
            #most recent date
            self.latest_day = self.df['day'].max()
            
            
            print(f"Data loaded successfully. Latest date: {self.latest_day.date()}")
            return True
            
        except Exception as e:
            
            print(f" Error loading data: {e}")
            return False
    
    def calculate_kpis(self, target_date):
        
        # Filter data to only include rows for the target date
        day_df = self.df[self.df['day'] == target_date]
        
  
        if day_df.empty:
            return None
            
        #
        kpis = {
            'date': target_date,  
            'tpv': day_df['amount_transacted'].sum(),  # Total Payment Volume
            'avg_ticket': day_df['amount_transacted'].sum() / day_df['quantity_transactions'].sum() if day_df['quantity_transactions'].sum() > 0 else 0,  # Average ticket size
            'total_transactions': day_df['quantity_transactions'].sum(),  # Total number of transactions
            'total_merchants': day_df['quantity_of_merchants'].sum(),  # Total number of merchants
            'entity_breakdown': day_df.groupby('entity')['amount_transacted'].sum().to_dict(),  # TPV by entity
            'product_breakdown': day_df.groupby('product')['amount_transacted'].sum().to_dict(),  # TPV by product
            'payment_method_breakdown': day_df.groupby('payment_method')['amount_transacted'].sum().to_dict()  # TPV by payment method
        }
        return kpis
    
    def calculate_growth(self, current_kpis, previous_kpis):
       
        # If no previous data, return empty dictionary
        if not previous_kpis:
            return {}
            
        growth = {}  # Will store growth percentages
        
        # Cgrowth for each KPI
        for key in ['tpv', 'avg_ticket', 'total_transactions']:
            if key in current_kpis and key in previous_kpis and previous_kpis[key] > 0:
                
                growth[f'{key}_growth'] = ((current_kpis[key] - previous_kpis[key]) / previous_kpis[key]) * 100
            else:
                growth[f'{key}_growth'] = 0  
        return growth
    
    def detect_alerts(self, current_kpis, previous_kpis, growth_rates):
       
        alerts = []  
        
        # Check if TPV dropped significantly (more than 20%)
        if 'tpv_growth' in growth_rates and growth_rates['tpv_growth'] < -20:
            alerts.append(f"TPV dropped {abs(growth_rates['tpv_growth']):.1f}% vs previous day")
        
        # Check if average ticket dropped significantly (more than 15%)
        if 'avg_ticket_growth' in growth_rates and growth_rates['avg_ticket_growth'] < -15:
            alerts.append(f"Average ticket dropped {abs(growth_rates['avg_ticket_growth']):.1f}% vs previous day")
        
        # Check if transaction volume dropped significantly (more than 25%)
        if 'total_transactions_growth' in growth_rates and growth_rates['total_transactions_growth'] < -25:
            alerts.append(f"Transaction volume dropped {abs(growth_rates['total_transactions_growth']):.1f}% vs previous day")
        
        # Check if there are no transactions at all
        if current_kpis['total_transactions'] == 0:
            alerts.append("No transactions recorded today")
        
        return alerts
    
    def generate_email_summary(self, current_kpis, growth_rates, alerts):
        
        summary = f"""
📊 Daily KPI Report - {current_kpis['date'].strftime('%A, %B %d, %Y')}

🔢 Key Metrics:
• Total Payment Volume (TPV): ${current_kpis['tpv']:,.2f} {f"({growth_rates.get('tpv_growth', 0):+.1f}%)" if 'tpv_growth' in growth_rates else ''}
• Average Ticket: ${current_kpis['avg_ticket']:,.2f} {f"({growth_rates.get('avg_ticket_growth', 0):+.1f}%)" if 'avg_ticket_growth' in growth_rates else ''}
• Total Transactions: {current_kpis['total_transactions']:,} {f"({growth_rates.get('total_transactions_growth', 0):+.1f}%)" if 'total_transactions_growth' in growth_rates else ''}
• Total Merchants: {current_kpis['total_merchants']:,}

📈 Top Performers:
• Highest TPV Entity: {max(current_kpis['entity_breakdown'].items(), key=lambda x: x[1])[0]} (${max(current_kpis['entity_breakdown'].values()):,.2f})
• Top Product: {max(current_kpis['product_breakdown'].items(), key=lambda x: x[1])[0]} (${max(current_kpis['product_breakdown'].values()):,.2f})
• Leading Payment Method: {max(current_kpis['payment_method_breakdown'].items(), key=lambda x: x[1])[0]} (${max(current_kpis['payment_method_breakdown'].values()):,.2f})

"""
        
        # Add alerts if any exist
        if alerts:
            summary += "🚨 Alerts:\n"
            for alert in alerts:
                summary += f"• {alert}\n"
        else:
            summary += "✅ No alerts - All metrics within normal ranges\n"
        
        # Add footer with timestamp
        summary += f"\n📅 Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | KPI SUMMARY"
        
        return summary
    

    
    def send_gmail(self, subject, message, gmail_config):
       
        try:
            #  email message
            msg = MIMEMultipart('alternative')  # Allows both HTML and text
            msg['Subject'] = subject  #
            msg['From'] = gmail_config['sender_email']  
            msg['To'] = gmail_config['recipient_email']  
            
            # 
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)  
            
            # Connection to Gmail's SMTP server
            with smtplib.SMTP(gmail_config['smtp_server'], gmail_config['smtp_port']) as server:
                server.starttls()  
                server.login(gmail_config['sender_email'], gmail_config['password'])  # Login
                server.send_message(msg)  # Send the email
            
            print("Gmail sent successfully!")
            return True
            
        except Exception as e:
            print(f"Error sending Gmail: {e}")
            return False
    
    def run_daily_report(self, gmail_config=None):
        
        print("🤖 Daily Data Summary - Starting Daily Analysis...")
        
        
        if not self.load_data():
            return False
        
        # Calculated KPIs for today and yesterday
        current_kpis = self.calculate_kpis(self.latest_day)  # Today's KPIs
        previous_day = self.latest_day - timedelta(days=1)  # Yesterday's date
        previous_kpis = self.calculate_kpis(previous_day)  # Yesterday's KPIs
        
        
        if not current_kpis:
            print(" No data found for latest day")
            return False
        
        #  growth rates
        growth_rates = self.calculate_growth(current_kpis, previous_kpis)
        
        # alerts
        alerts = self.detect_alerts(current_kpis, previous_kpis, growth_rates)
        
        # email summary
        email_summary = self.generate_email_summary(current_kpis, growth_rates, alerts)
        
        # Send email if Gmail config is provided
        if gmail_config:
            # Create subject line
            subject = f"📊 Daily Data Report - {current_kpis['date'].strftime('%B %d, %Y')}"
            if alerts:
                subject += " 🚨"  # Add alert emoji if there are alerts
            
            # Send the email
            success = self.send_gmail(subject, email_summary, gmail_config)
            return success
        else:
            print("📧 Gmail not configured - HTML report saved locally")
            return True



if __name__ == "__main__":
    
    GMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',  # Gmail's SMTP server
        'smtp_port': 587,  # Gmail's SMTP port
        'sender_email': 'your_email@gmail.com',  
        'password': 'your_app_password',  #  Gmail app password 
        'recipient_email': 'recipient@example.com'  # senders ID
    }
    
    #  Initializing the bot with my CSV file
    bot = SimpleGmailKPIBot('Operations_analyst_data - Copy.csv')
    
    #
    success = bot.run_daily_report(
        gmail_config=GMAIL_CONFIG  
    )
    
    
    if success:
        print("🎉 Daily data analysis completed successfully!")
        print("📧 Email sent via Gmail")
    else:
        print("❌ Analysis failed")
