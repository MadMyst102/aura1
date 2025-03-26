import sys
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib
import base64

# Use the same encryption configuration as the main application
LICENSE_SECRET = b'yXn8kp2lMqRtWvZaEoHgUjIcFbNdSxKp'
ENCRYPTION_KEY = base64.urlsafe_b64encode(b'dR7mK9pL4nX2wS5vY8hB3gA6tU9jC1eQ'[:32])

def generate_key(machine_id, days):
    """Generate a license key for a specific machine ID"""
    try:
        # Create Fernet cipher
        fernet = Fernet(ENCRYPTION_KEY)
        
        # Set expiration date
        expiration = datetime.now() + timedelta(days=days)
        
        # Generate signature
        h = hashlib.sha256()
        h.update(machine_id.encode())
        h.update(expiration.isoformat().encode())
        h.update(LICENSE_SECRET)
        signature = h.hexdigest()
        
        # Create license payload
        payload = {
            'machine_id': machine_id,
            'expiration': expiration.isoformat(),
            'signature': signature
        }
        
        # Encrypt and return the license key
        return fernet.encrypt(json.dumps(payload).encode()).decode()
        
    except Exception as e:
        print(f"Error generating license key: {e}")
        return None

def main():
    print("AURA pro+ farm License Key Generator")
    print("-" * 50)
    
    # Get machine ID
    machine_id = input("Enter customer's machine ID: ").strip()
    if not machine_id:
        print("Error: Machine ID is required")
        sys.exit(1)
    
    # Get license duration
    try:
        days = int(input("Enter license duration in days: "))
        if days <= 0:
            raise ValueError("Duration must be positive")
    except ValueError as e:
        print(f"Error: Invalid duration - {e}")
        sys.exit(1)
    
    # Generate and display the license key
    license_key = generate_key(machine_id, days)
    if license_key:
        print("\nLicense key generated successfully!")
        print("-" * 50)
        print(f"Machine ID: {machine_id}")
        print(f"Duration: {days} days")
        print("-" * 50)
        print("License Key:")
        print(license_key)
        
        # Save to file
        filename = f"license_{machine_id[:8]}_{days}days.txt"
        with open(filename, 'w') as f:
            f.write(f"Machine ID: {machine_id}\n")
            f.write(f"Duration: {days} days\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\nLicense Key:\n")
            f.write(license_key)
        print(f"\nKey has been saved to {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"Unexpected error: {e}")
