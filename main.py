import os
import hashlib
import requests
from celery import Celery
from bs4 import BeautifulSoup
from sqlalchemy import create_all, create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import smtplib
from email.message import EmailMessage

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/webdiff")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = Celery("diff_checker", broker=REDIS_URL)
app.conf.beat_schedule = {
    'check-every-10-minutes': {
        'task': 'tasks.check_website',
        'schedule': 600.0,
        'args': ('https://example.com',)
    },
}


engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Website(Base):
    __tablename__ = "websites"
    url = Column(String, primary_key=True)
    last_hash = Column(String)

Base.metadata.create_all(engine)

def send_email(url):
    msg = EmailMessage()
    msg.set_content(f"The website {url} has been updated!")
    msg['Subject'] = f"Update Alert: {url}"
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = os.getenv("NOTIFY_EMAIL")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)

@app.task
def check_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Focus on body to avoid false positives from header metadata
        content = str(soup.find('body'))
        new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        session = Session()
        site = session.query(Website).filter_by(url=url).first()

        if not site:
            session.add(Website(url=url, last_hash=new_hash))
            session.commit()
        elif site.last_hash != new_hash:
            site.last_hash = new_hash
            session.commit()
            send_email(url)
            print(f"Change detected for {url}!")
        
        session.close()
    except Exception as e:
        print(f"Error checking {url}: {e}")
