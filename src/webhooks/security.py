"""
Webhook Security for ADCC Analysis Engine

This module provides security functionality for webhook authentication
and signature verification.
"""

import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class WebhookSecurity:
    """
    Handles webhook security and authentication.
    
    Provides methods for generating secrets, signing payloads,
    and verifying webhook signatures.
    """
    
    def __init__(self):
        """Initialize the webhook security module."""
        self.algorithm = "sha256"
    
    def generate_secret(self, length: int = 32) -> str:
        """
        Generate a secure random secret for webhook authentication.
        
        Args:
            length: Length of the secret in bytes
            
        Returns:
            Base64-encoded secret
        """
        secret = secrets.token_urlsafe(length)
        logger.debug("Generated webhook secret", length=length)
        return secret
    
    def sign_payload(self, payload: str, secret: str) -> str:
        """
        Sign a webhook payload with HMAC-SHA256.
        
        Args:
            payload: JSON string payload to sign
            secret: Webhook secret for signing
            
        Returns:
            HMAC signature
        """
        try:
            signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            logger.debug("Signed webhook payload", 
                        payload_length=len(payload),
                        algorithm=self.algorithm)
            
            return signature
        except Exception as e:
            logger.error("Failed to sign webhook payload", error=str(e))
            raise
    
    def verify_signature(
        self,
        payload: str,
        signature: str,
        secret: str,
        tolerance_seconds: int = 300
    ) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: JSON string payload
            signature: Expected signature
            secret: Webhook secret
            tolerance_seconds: Time tolerance for timestamp validation
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Generate expected signature
            expected_signature = self.sign_payload(payload, secret)
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if is_valid:
                logger.debug("Webhook signature verified successfully")
            else:
                logger.warning("Webhook signature verification failed")
            
            return is_valid
        except Exception as e:
            logger.error("Error during signature verification", error=str(e))
            return False
    
    def verify_timestamp(self, timestamp: int, tolerance_seconds: int = 300) -> bool:
        """
        Verify webhook timestamp to prevent replay attacks.
        
        Args:
            timestamp: Unix timestamp from webhook
            tolerance_seconds: Time tolerance in seconds
            
        Returns:
            True if timestamp is within tolerance, False otherwise
        """
        current_time = int(time.time())
        time_diff = abs(current_time - timestamp)
        
        is_valid = time_diff <= tolerance_seconds
        
        if is_valid:
            logger.debug("Webhook timestamp verified", 
                        time_diff=time_diff,
                        tolerance=tolerance_seconds)
        else:
            logger.warning("Webhook timestamp verification failed",
                         time_diff=time_diff,
                         tolerance=tolerance_seconds)
        
        return is_valid
    
    def create_webhook_headers(
        self,
        payload: str,
        secret: str,
        event_type: str,
        webhook_id: str
    ) -> Dict[str, str]:
        """
        Create headers for webhook delivery.
        
        Args:
            payload: JSON string payload
            secret: Webhook secret
            event_type: Type of event
            webhook_id: Webhook ID
            
        Returns:
            Dictionary of headers
        """
        timestamp = str(int(time.time()))
        signature = self.sign_payload(payload, secret)
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ADCC-Analysis-Engine/0.6.0",
            "X-Webhook-ID": webhook_id,
            "X-Event-Type": event_type,
            "X-Timestamp": timestamp,
            "X-Signature": f"{self.algorithm}={signature}",
            "X-ADCC-Version": "0.6.0"
        }
        
        logger.debug("Created webhook headers", 
                    event_type=event_type,
                    webhook_id=webhook_id)
        
        return headers
    
    def validate_webhook_request(
        self,
        payload: str,
        headers: Dict[str, str],
        secret: str
    ) -> Dict[str, Any]:
        """
        Validate incoming webhook request.
        
        Args:
            payload: Request payload
            headers: Request headers
            secret: Expected webhook secret
            
        Returns:
            Validation result with details
        """
        result = {
            "valid": False,
            "errors": [],
            "timestamp": None,
            "event_type": None,
            "webhook_id": None
        }
        
        try:
            # Extract headers
            signature = headers.get("X-Signature", "")
            timestamp_str = headers.get("X-Timestamp", "")
            event_type = headers.get("X-Event-Type", "")
            webhook_id = headers.get("X-Webhook-ID", "")
            
            # Validate required headers
            if not signature:
                result["errors"].append("Missing X-Signature header")
            if not timestamp_str:
                result["errors"].append("Missing X-Timestamp header")
            if not event_type:
                result["errors"].append("Missing X-Event-Type header")
            if not webhook_id:
                result["errors"].append("Missing X-Webhook-ID header")
            
            if result["errors"]:
                return result
            
            # Parse timestamp
            try:
                timestamp = int(timestamp_str)
                result["timestamp"] = timestamp
            except ValueError:
                result["errors"].append("Invalid timestamp format")
                return result
            
            # Verify timestamp
            if not self.verify_timestamp(timestamp):
                result["errors"].append("Timestamp out of tolerance")
            
            # Extract signature from header
            if not signature.startswith(f"{self.algorithm}="):
                result["errors"].append("Invalid signature format")
                return result
            
            signature_value = signature.split("=", 1)[1]
            
            # Verify signature
            if not self.verify_signature(payload, signature_value, secret):
                result["errors"].append("Invalid signature")
            
            # Set result fields
            result["event_type"] = event_type
            result["webhook_id"] = webhook_id
            
            # Mark as valid if no errors
            if not result["errors"]:
                result["valid"] = True
                logger.info("Webhook request validated successfully",
                           webhook_id=webhook_id,
                           event_type=event_type)
            else:
                logger.warning("Webhook request validation failed",
                             webhook_id=webhook_id,
                             errors=result["errors"])
            
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
            logger.error("Error during webhook validation", error=str(e))
        
        return result
    
    def generate_webhook_url_token(self, webhook_id: str, secret: str) -> str:
        """
        Generate a secure token for webhook URL validation.
        
        Args:
            webhook_id: Webhook ID
            secret: Webhook secret
            
        Returns:
            Secure token
        """
        timestamp = str(int(time.time()))
        data = f"{webhook_id}:{timestamp}"
        
        token = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{token}"
    
    def verify_webhook_url_token(
        self,
        token: str,
        webhook_id: str,
        secret: str,
        tolerance_seconds: int = 3600
    ) -> bool:
        """
        Verify webhook URL token.
        
        Args:
            token: Token to verify
            webhook_id: Webhook ID
            secret: Webhook secret
            tolerance_seconds: Time tolerance in seconds
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            if ":" not in token:
                return False
            
            timestamp_str, signature = token.split(":", 1)
            timestamp = int(timestamp_str)
            
            # Check timestamp
            if not self.verify_timestamp(timestamp, tolerance_seconds):
                return False
            
            # Verify signature
            data = f"{webhook_id}:{timestamp_str}"
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error("Error verifying webhook URL token", error=str(e))
            return False 