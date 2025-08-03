import telnetlib
import sys

host = "terraform-20250123164008602600000001.cqcqvqkwjtl5.us-east-1.rds.amazonaws.com"
port = 3306

print(f"Testing telnet connection to {host}:{port}")
try:
    tn = telnetlib.Telnet(host, port, timeout=10)
    print("[OK] Connected! Port is open.")
    tn.close()
except Exception as e:
    print(f"[FAIL] Could not connect: {e}")
    
# Also test with direct IP
ip = "54.90.45.147"
print(f"\nTesting direct IP connection to {ip}:{port}")
try:
    tn = telnetlib.Telnet(ip, port, timeout=10)
    print("[OK] Connected via IP! Port is open.")
    tn.close()
except Exception as e:
    print(f"[FAIL] Could not connect via IP: {e}")