import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Amazon product URL
URL = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"

# Headers (to prevent blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Email config
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Price threshold
TARGET_PRICE = 100  # Change this to your desired price


def get_price():
    """Scrape the Amazon page and extract the price."""
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find price (Amazon sometimes uses different classes)
    price_whole = soup.find("span", class_="a-price-whole")
    price_fraction = soup.find("span", class_="a-price-fraction")

    if price_whole and price_fraction:
        price = float(price_whole.text.replace(",", "") + price_fraction.text)
        return price
    else:
        return None


def send_email(price):
    """Send an email alert if the price drops below the threshold."""
    subject = f"Price Drop Alert! Now ${price}"
    body = f"""
    Good news! The price has dropped to ${price}.

    Check it out here: {URL}

    Best,
    Your Price Tracker
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")


def main():
    """Check the price and send an alert if needed."""
    price = get_price()
    if price:
        print(f"Current price: ${price}")
        if price <= TARGET_PRICE:
            send_email(price)
    else:
        print("❌ Couldn't fetch the price. Amazon may have changed the structure.")


if __name__ == "__main__":
    main()
