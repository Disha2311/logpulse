from datetime import datetime, timezone
import httpx
import logging

logger = logging.getLogger("app.webhook_service")

class WebhookService:
    @staticmethod
    def send_webhook_alert(url: str, service: str, error_count: int, threshold: int) -> bool:
        """
        Send a synchronous POST request containing alert details to the configured webhook URL.
        """
        payload = {
            "event": "threshold_breached",
            "service": service,
            "error_count": error_count,
            "threshold": threshold,
            "triggered_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            logger.info(f"Dispatching webhook to: {url}")
            response = httpx.post(url, json=payload, timeout=5.0)
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook alert successfully sent to {url} (Status: {response.status_code})")
                return True
            else:
                logger.error(f"Webhook URL {url} returned non-2xx status code: {response.status_code}")
                return False
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while sending webhook alert to {url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending webhook alert to {url}: {str(e)}")
            return False
