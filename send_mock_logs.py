import httpx
import time
import random
import sys

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "ops-team@company.com"
PASSWORD = "SecurePassword123"

# Mock logs list
SERVICES = ["gateway", "auth-service", "payment-service", "database-service"]
LEVELS = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]
MESSAGES = {
    "INFO": [
        "User login successful",
        "Connection pool refreshed",
        "Config reload initiated",
        "Health check passed",
        "Backup process completed successfully"
    ],
    "DEBUG": [
        "Session authenticated successfully",
        "Query execution time: 12ms",
        "Deserialized user object payload",
        "Fetching cache keys: errors:*"
    ],
    "WARNING": [
        "Database connection pool capacity at 85%",
        "Slow query detected: SELECT * FROM users (120ms)",
        "API rate limit threshold warning: user_id=482",
        "SMTP mail delivery queue latency above 2s"
    ],
    "ERROR": [
        "Failed to charge credit card: Insufficient funds",
        "OperationalError: Redis connection timed out",
        "Timeout waiting for upstream billing-service response",
        "Invalid token payload format"
    ],
    "CRITICAL": [
        "PostgreSQL ConnectionRefusedError: [WinError 1225]",
        "Out of memory: Heap space exhausted on auth-node-1",
        "Fatal exception: Payment Gateway down",
        "Security breach attempt: SQL Injection signature detected"
    ]
}

def run_simulation():
    print("🚀 Starting LogFlow Ingestion Simulator...\n")
    client = httpx.Client()
    
    # 1. Register or Login
    print(f"🔑 Authenticating user: {EMAIL}...")
    try:
        # Try registering first
        reg_res = client.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD})
        if reg_res.status_code == 201:
            print("✨ Registration successful (New user created).")
        else:
            print("ℹ️ User already registered. Proceeding to login...")
    except Exception:
         print("ℹ️ User already registered or registration skipped. Logging in...")

    # Login to get JWT Token
    try:
        login_res = client.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if login_res.status_code != 200:
            print(f"❌ Authentication failed: {login_res.text}")
            return
        token = login_res.json()["access_token"]
        print("✅ JWT Authentication token retrieved successfully.\n")
    except Exception as e:
        print(f"❌ Failed to reach backend API. Make sure FastAPI server is running on port 8000. Error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check and Create Alerting Rule
    print("📋 Checking alert rules...")
    rules_res = client.get(f"{BASE_URL}/alert-rules", headers=headers)
    existing_rules = rules_res.json()
    
    # If no rule for gateway exists, create one
    if not any(r["service"] == "gateway" for r in existing_rules):
        print("➕ Creating alert policy for 'gateway' service (Threshold: 3 errors, Window: 2 min)...")
        rule_payload = {
            "service": "gateway",
            "threshold": 3,
            "window_minutes": 2,
            "notify_email": "ops-alert-receiver@company.com",
            "notify_webhook_url": "https://httpbin.org/post"  # Dummy webhook URL
        }
        create_res = client.post(f"{BASE_URL}/alert-rules", json=rule_payload, headers=headers)
        if create_res.status_code == 201:
            print("🚀 Alerting rule successfully registered.")
        else:
            print(f"❌ Failed to create rule: {create_res.text}")
    else:
        print("ℹ️ Alert policy for 'gateway' already exists.")

    print("\n📦 Simulating log streams... Press CTRL+C to terminate.")
    print("-----------------------------------------------------")

    # Counter to track injected errors for gateway to verify breach
    gateway_errors = 0

    try:
        while True:
            # Pick a level
            # 70% chance of INFO/DEBUG/WARNING, 30% chance of ERROR/CRITICAL
            level_roll = random.random()
            if level_roll < 0.40:
                level = random.choice(["INFO", "DEBUG"])
            elif level_roll < 0.70:
                level = "WARNING"
            else:
                level = random.choice(["ERROR", "CRITICAL"])

            service = random.choice(SERVICES)
            message = random.choice(MESSAGES[level])

            # Force gateway error to test alert breach if we want to show it off
            if gateway_errors < 3 and level in ["ERROR", "CRITICAL"] and random.random() < 0.5:
                service = "gateway"

            if service == "gateway" and level in ["ERROR", "CRITICAL"]:
                gateway_errors += 1
                print(f"🔥 Error logged for gateway ({gateway_errors}/3 to trigger alert policy!)")

            log_payload = {
                "service": service,
                "level": level,
                "message": message
            }

            log_res = client.post(f"{BASE_URL}/logs", json=log_payload, headers=headers)
            if log_res.status_code == 201:
                print(f"📡 Sent log: [{level}] service={service} | msg={message}")
            else:
                print(f"❌ Log ingestion failed: {log_res.status_code}")

            # Sleep between 1.5s to 3s to simulate network ingestion delays
            time.sleep(random.uniform(1.5, 3.0))

    except KeyboardInterrupt:
        print("\n👋 Simulation stopped by user. Goodbye!")

if __name__ == "__main__":
    run_simulation()
