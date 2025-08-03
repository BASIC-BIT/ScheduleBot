#!/usr/bin/env python3
"""
RDS Connection Diagnostic Tool
Tests various aspects of RDS connectivity
"""

import os
import socket
import subprocess
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dns_resolution(hostname):
    """Test if the hostname resolves"""
    print(f"\n1. Testing DNS resolution for: {hostname}")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"   [OK] Resolved to IP: {ip}")
        return True
    except socket.gaierror as e:
        print(f"   [FAIL] DNS resolution failed: {e}")
        return False

def test_port_connectivity(hostname, port=3306):
    """Test if the port is reachable"""
    print(f"\n2. Testing port {port} connectivity")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"   [OK] Port {port} is open")
            return True
        else:
            print(f"   [FAIL] Port {port} is closed or filtered (error code: {result})")
            return False
    except Exception as e:
        print(f"   [FAIL] Connection test failed: {e}")
        return False

def test_mysql_connection(host, user, password, database):
    """Test MySQL connection"""
    print(f"\n3. Testing MySQL connection")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            connect_timeout=10
        )
        print("   [OK] MySQL connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   [OK] MySQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"   [FAIL] MySQL error: {err}")
        print(f"   Error code: {err.errno if hasattr(err, 'errno') else 'N/A'}")
        return False

def ping_test(hostname):
    """Test basic ICMP ping (might be blocked by AWS)"""
    print(f"\n4. Testing ping (may be blocked by AWS)")
    try:
        # Windows ping command
        result = subprocess.run(
            ["ping", "-n", "2", "-w", "2000", hostname],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   [OK] Ping successful")
        else:
            print("   [WARN] Ping failed (this is normal for RDS)")
    except Exception as e:
        print(f"   [FAIL] Ping test error: {e}")

def main():
    """Run all diagnostics"""
    print("RDS Connection Diagnostics")
    print("=" * 50)
    
    # Get configuration
    host = os.getenv('MYSQL_SERVER', 'scheduleBot-db')
    user = os.getenv('MYSQL_USER', 'schedulebot')
    password = os.getenv('MYSQL_USER_PW', 'schedulebot')
    database = os.getenv('MYSQL_DB', 'ScheduleBot')
    
    print(f"Configuration:")
    print(f"  Host: {host}")
    print(f"  User: {user}")
    print(f"  Database: {database}")
    print(f"  Password: {'[SET]' if password != 'schedulebot' else '[USING DEFAULT]'}")
    
    # Run tests
    dns_ok = test_dns_resolution(host)
    
    if dns_ok:
        port_ok = test_port_connectivity(host)
        ping_test(host)
        
        if port_ok:
            test_mysql_connection(host, user, password, database)
        else:
            print("\n[WARN] Port connectivity failed. Possible causes:")
            print("  1. Security group not allowing your IP")
            print("  2. RDS not publicly accessible")
            print("  3. Network ACL blocking traffic")
            print("  4. RDS in private subnet without internet route")
    else:
        print("\n[WARN] DNS resolution failed. Check:")
        print("  1. RDS endpoint is correct")
        print("  2. You have internet connectivity")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()