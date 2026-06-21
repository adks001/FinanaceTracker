import imaplib
import email
from email.header import decode_header
import json
import re
import hashlib
import logging
from bs4 import BeautifulSoup
import google.generativeai as genai
from app.config import GEMINI_API_KEY
from app.db import supabase, get_categories, insert_expense

logger = logging.getLogger(__name__)

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Define transaction markers
TRANSACTION_MARKERS = [
    "debited", "credited", "spent", "alert", "transaction", "payment",
    "upi", "purchase", "order", "charge", "refund", "receipt", "invoice",
    "transfer", "bank", "credit card", "ebill", "spent on", "received from"
]

def get_imap_host(email_address: str) -> str:
    """
    Dynamically maps an email suffix to standard IMAP hosts, or falls back to domain-based host.
    """
    email_address = email_address.lower().strip()
    if email_address.endswith("@gmail.com"):
        return "imap.gmail.com"
    elif email_address.endswith("@yahoo.com") or email_address.endswith("@ymail.com"):
        return "imap.mail.yahoo.com"
    elif email_address.endswith("@outlook.com") or email_address.endswith("@hotmail.com") or email_address.endswith("@live.com") or email_address.endswith("@msn.com"):
        return "outlook.office365.com"
    
    # Fallback: extract domain and guess IMAP server
    match = re.search(r"@([\w.-]+)$", email_address)
    if match:
        domain = match.group(1)
        return f"imap.{domain}"
    return ""

def clean_html_body(html_content: str) -> str:
    """Uses BeautifulSoup to strip HTML tags and return clean plain text to save tokens."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text
        text = soup.get_text(separator=" ")
        
        # Collapse whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        logger.error(f"Error cleaning HTML body: {e}")
        return html_content

def extract_email_text(msg) -> tuple:
    """
    Extracts plain text body and Message-ID from an email message object.
    """
    body = ""
    message_id = msg.get("Message-ID", "")
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    pass
            elif content_type == "text/html" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    html_text = payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                    body += clean_html_body(html_text)
                except Exception:
                    pass
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True)
            text = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
            if content_type == "text/html":
                body = clean_html_body(text)
            else:
                body = text
        except Exception:
            pass
            
    return body.strip(), message_id

def contains_transaction_markers(subject: str, snippet: str) -> bool:
    """Checks if email headers indicate a transaction."""
    text_to_check = f"{subject} {snippet}".lower()
    return any(marker in text_to_check for marker in TRANSACTION_MARKERS)

def parse_transaction_with_gemini(sender: str, subject: str, date_str: str, body_text: str) -> dict:
    """
    Sends the email snippet to Gemini 1.5 Flash to parse details.
    Guarantees returning structured JSON.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key is missing.")
        
    # Limit body text size to prevent token blowup (first 3000 chars are usually plenty for alerts)
    body_snippet = body_text[:3000]
    
    prompt = f"""
You are an expert financial assistant. Analyze this email details and determine if it represents a transaction alert (expense, purchase, credit, debit, refund, deposit, salary, etc.).

Email Details:
- Sender: {sender}
- Subject: {subject}
- Date: {date_str}
- Content:
---
{body_snippet}
---

Task:
1. Identify if this is a transaction (debit, credit, spent, received, order, invoice, payment, etc.).
2. If it is NOT a transaction, set "is_transaction" to false and leave other fields empty.
3. If it IS a transaction, extract details:
   - "date": Date in "YYYY-MM-DD" format. (Standardize the email date to YYYY-MM-DD).
   - "merchant": Clean, recognizable merchant/source/destination name (e.g. "Uber", "Walmart", "Netflix", "HDFC Bank").
   - "amount": The numeric transaction amount (float). Do not include currency symbols.
   - "description": A concise summary (e.g. "Monthly subscription payment", "Grocery purchase", "Salary credited").
   - "earning_vs_expense": Either "Earning" (if money added/credited/refunded) or "Expense" (if spent/debited/withdrawn).
   - "category_name": Classify this transaction into one of these EXACT categories:
     * "Income/Earnings"
     * "Groceries"
     * "Fuel & Transport"
     * "Dining & Food"
     * "Utilities & Bills"
     * "Medical & Health"
     * "Entertainment & Subs"
     * "Home Maintenance"
     * "Miscellaneous"

Provide your output ONLY in a valid JSON object of this structure:
{{
  "is_transaction": true/false,
  "date": "YYYY-MM-DD",
  "merchant": "Merchant Name",
  "amount": 0.00,
  "description": "Short description",
  "earning_vs_expense": "Expense" or "Earning",
  "category_name": "Category Name"
}}
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        result = json.loads(response.text)
        return result
    except Exception as e:
        logger.error(f"Gemini transaction parsing failed: {e}")
        return {"is_transaction": False}

def fetch_and_parse_emails(email_address: str, password: str, user_id: str, limit: int = 15, imap_host: str = None) -> list:
    """
    Logs in to the IMAP server, searches for UNSEEN transaction messages,
    parses them with Gemini, and records them in Supabase.
    """
    host = imap_host or get_imap_host(email_address)
    if not host:
        raise ValueError(f"Could not resolve IMAP server for email: {email_address}")
        
    logger.info(f"Connecting to IMAP host {host} for {email_address}...")
    
    try:
        mail = imaplib.IMAP4_SSL(host, 993)
        mail.login(email_address, password)
    except Exception as e:
        logger.error(f"IMAP login failed: {e}")
        raise RuntimeError(f"IMAP authentication failed: {e}")
        
    added_expenses = []
    
    try:
        mail.select("INBOX")
        # Search for unseen emails
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return []
            
        message_ids = messages[0].split()
        if not message_ids:
            logger.info("No unread emails found.")
            return []
            
        # Limit the number of emails to process to avoid API rate limits
        message_ids = message_ids[-limit:]
        logger.info(f"Checking {len(message_ids)} unread emails...")
        
        # Load user categories for matching names
        db_categories = get_categories(user_id)
        categories_map = {c["name"].lower(): c["id"] for c in db_categories}
        
        # Find default "Miscellaneous" category ID
        misc_category_id = None
        for c in db_categories:
            if c["name"] == "Miscellaneous":
                misc_category_id = c["id"]
                break
        if not misc_category_id and db_categories:
            misc_category_id = db_categories[0]["id"] # fallback
            
        for mail_id in reversed(message_ids):
            # Fetch email envelope & body
            res, msg_data = mail.fetch(mail_id, "(RFC822)")
            if res != "OK":
                continue
                
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Parse headers
            subject_header = decode_header(msg.get("Subject", ""))[0]
            subject = ""
            if isinstance(subject_header[0], bytes):
                subject = subject_header[0].decode(subject_header[1] or "utf-8", errors="ignore")
            else:
                subject = str(subject_header[0])
                
            from_header = msg.get("From", "")
            date_header = msg.get("Date", "")
            
            # Extract plain text content and unique Message-ID
            body_text, msg_id = extract_email_text(msg)
            
            # Create a raw_email_uid to catch duplicates
            # Use Message-ID or fall back to SHA-256 hash of sender+subject+body snippet
            email_uid = msg_id
            if not email_uid:
                hash_input = f"{from_header}_{date_header}_{subject}_{body_text[:100]}"
                email_uid = "hash_" + hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
            
            # Verify if it contains transaction markers first to save Gemini costs
            if contains_transaction_markers(subject, body_text[:200]):
                logger.info(f"Parsing potential transaction alert: '{subject}'")
                
                parsed = parse_transaction_with_gemini(from_header, subject, date_header, body_text)
                
                if parsed.get("is_transaction") and parsed.get("amount", 0) > 0:
                    # Match Gemini's suggested category to database category_id
                    suggested_cat = parsed.get("category_name", "Miscellaneous")
                    category_id = categories_map.get(suggested_cat.lower(), misc_category_id)
                    
                    # Prepare expense object
                    expense_data = {
                        "profile_id": user_id,
                        "date": parsed.get("date"),
                        "merchant": parsed.get("merchant", "Unknown Merchant"),
                        "description": parsed.get("description", f"Parsed from email: {subject}"),
                        "amount": parsed.get("amount"),
                        "earning_vs_expense": parsed.get("earning_vs_expense", "Expense"),
                        "category_id": category_id,
                        "is_shared": False,
                        "split_percentage": 100.00,
                        "raw_email_uid": email_uid
                    }
                    
                    # Attempt DB insert (which filters out raw_email_uid duplicates)
                    inserted = insert_expense(expense_data)
                    if inserted:
                        added_expenses.append(inserted)
                        # Mark email as read on server
                        mail.store(mail_id, "+FLAGS", "\\Seen")
                        logger.info(f"Logged transaction alert: {parsed.get('merchant')} - {parsed.get('amount')}")
                    else:
                        # Email was a duplicate and ignored in DB, mark it seen anyway so we don't query again
                        mail.store(mail_id, "+FLAGS", "\\Seen")
                        logger.info("Skipped duplicate transaction alert.")
                else:
                    # Not a transaction email, mark as seen so we don't parse it again
                    mail.store(mail_id, "+FLAGS", "\\Seen")
            else:
                # Doesn't contain markers, mark as seen so we skip next time
                mail.store(mail_id, "+FLAGS", "\\Seen")
                
    except Exception as e:
        logger.error(f"Error fetching/parsing emails: {e}")
        raise e
    finally:
        try:
            mail.close()
            mail.logout()
        except Exception:
            pass
            
    return added_expenses
