import requests
import datetime as dt
from twilio.rest import Client
import config

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

ALPHA_API_KEY = config.ALPHA_API_KEY
NEWS_API_KEY = config.NEWS_API_KEY

TWILIO_SID = config.TWILIO_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN

FROM_PHONE_NUM = config.FROM_PHONE_NUM
TO_PHONE_NUM = config.TO_PHONE_NUM


def send_sms(body):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=body,
        from_=FROM_PHONE_NUM,
        to=TO_PHONE_NUM
    )


def percent_text(percentage):
    if percentage < 0:
        return f"🔻{str(percentage * -1)}%"
    else:
        return f"🔺{str(percentage)}%"


alpha_URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={ALPHA_API_KEY}"
response = requests.get(url=alpha_URL)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]

today = str(dt.datetime.now().date())
yesterday = str((dt.datetime.now() - dt.timedelta(days=1)).date())
two_days_ago = str((dt.datetime.now() - dt.timedelta(days=2)).date())

yesterdays_closing_price = float(data[yesterday]["4. close"])
day_before_yesterday_closing_price = float(data[two_days_ago]["4. close"])

difference = yesterdays_closing_price - day_before_yesterday_closing_price
diff_percent = round(difference / day_before_yesterday_closing_price * 100, 2)


if abs(diff_percent) >= 4:
    news_params = {
        "q": COMPANY_NAME,
        "searchIn": "title,description",
        "from": yesterday,
        "language": 'en',
        "sortBy": "popularity",
        "pageSize": 3,
        "apiKey": NEWS_API_KEY
    }
    rs = requests.get(url="https://newsapi.org/v2/everything", params=news_params)
    rs.raise_for_status()
    news_list = rs.json()["articles"]
    for news in news_list:
        news_title = news["title"]
        news_desc = news["description"]
        text_body = f"{STOCK}:{percent_text(diff_percent)}\nHeadline: {news_title}\nBrief: {news_desc}"
        print(text_body)
        send_sms(text_body)


# https://www.alphavantage.co
# https://newsapi.org
# https://www.twilio.com