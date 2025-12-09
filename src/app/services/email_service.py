"""
Email Service

Handles sending emails for OTP verification and other notifications.
"""

import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional

from app.config.settings import settings
from app.connectors.mongodb_connector import get_collection


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.SMTP_FROM_NAME
        self.otp_collection = "email_otps"
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_otp_email(self, email: str) -> dict:
        """Generate and send OTP to email"""
        try:
            # Generate OTP
            otp = self.generate_otp(settings.OTP_LENGTH)
            expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
            
            # Store OTP in database
            collection = get_collection(self.otp_collection)
            
            # Delete any existing OTPs for this email
            collection.delete_many({"email": email.lower()})
            
            # Insert new OTP
            otp_doc = {
                "email": email.lower(),
                "otp": otp,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "verified": False
            }
            collection.insert_one(otp_doc)
            
            # Send email
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 30px; border-radius: 10px;">
                        <h2 style="color: #333;">Email Verification</h2>
                        <p style="color: #666; font-size: 16px;">
                            Thank you for registering with AVPE! Please use the following OTP to verify your email address:
                        </p>
                        <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #4CAF50; font-size: 36px; letter-spacing: 5px; margin: 0;">
                                {otp}
                            </h1>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            This OTP will expire in {settings.OTP_EXPIRE_MINUTES} minutes.
                        </p>
                        <p style="color: #999; font-size: 12px; margin-top: 30px;">
                            If you didn't request this, please ignore this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            success = self.send_email(email, "Verify Your Email - AVPE", html_content)
            
            if success:
                return {
                    "success": True,
                    "message": f"OTP sent to {email}",
                    "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to send email"
                }
                
        except Exception as e:
            print(f"❌ Error sending OTP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_otp(self, email: str, otp: str, mark_as_used: bool = False) -> dict:
        """Verify OTP for an email
        
        Args:
            email: Email address
            otp: OTP code
            mark_as_used: If True, mark OTP as verified (for final registration)
        """
        try:
            collection = get_collection(self.otp_collection)
            
            # Find OTP (check both verified and unverified)
            otp_doc = collection.find_one({
                "email": email.lower(),
                "otp": otp
            })
            
            if not otp_doc:
                return {
                    "success": False,
                    "error": "Invalid OTP"
                }
            
            # Check if expired
            if datetime.utcnow() > otp_doc["expires_at"]:
                return {
                    "success": False,
                    "error": "OTP has expired"
                }
            
            # Mark as verified only if requested (during registration)
            if mark_as_used and not otp_doc.get("used", False):
                collection.update_one(
                    {"_id": otp_doc["_id"]},
                    {"$set": {"verified": True, "used": True, "verified_at": datetime.utcnow()}}
                )
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
            
        except Exception as e:
            print(f"❌ Error verifying OTP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_otp(self, email: str) -> bool:
        """Delete OTP for an email after successful registration"""
        try:
            collection = get_collection(self.otp_collection)
            result = collection.delete_many({"email": email.lower()})
            print(f"🗑️  Deleted {result.deleted_count} OTP(s) for {email}")
            return True
        except Exception as e:
            print(f"❌ Error deleting OTP: {str(e)}")
            return False


# Global instance
email_service = EmailService()
