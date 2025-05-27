import requests
import sys
import json
from datetime import datetime
import re

def log(message):
    print(f"[{datetime.now().isoformat()}] {message}")

def get_csrf_token(response_text):
    try:
        # Try to find CSRF token in the HTML response
        match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
        if match:
            return match.group(1)
    except Exception as e:
        log(f"Error extracting CSRF token: {str(e)}")
    return None

def test_deployment(base_url):
    try:
        # Test health endpoint
        log("Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health")
        log(f"Health check status: {health_response.status_code}")
        try:
            health_data = health_response.json()
            log(f"Health check response: {json.dumps(health_data, indent=2)}")
        except json.JSONDecodeError:
            log(f"Raw health check response: {health_response.text}")
        
        # Test static file
        log("\nTesting static file access...")
        static_response = requests.get(f"{base_url}/static/css/style.css")
        log(f"Static file status: {static_response.status_code}")
        
        # Test login page
        log("\nTesting login page...")
        session = requests.Session()
        login_response = session.get(f"{base_url}/login")
        log(f"Login page status: {login_response.status_code}")
        
        # Get CSRF token
        csrf_token = get_csrf_token(login_response.text)
        if csrf_token:
            log("Found CSRF token")
        else:
            log("No CSRF token found")
        
        # Test invalid login
        log("\nTesting invalid login...")
        login_data = {
            'username': 'test_user',
            'password': 'wrong_password'
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
            
        invalid_login_response = session.post(
            f"{base_url}/login",
            data=login_data,
            headers={'Referer': f"{base_url}/login"}
        )
        log(f"Invalid login status: {invalid_login_response.status_code}")
        
        log("\nAll tests completed!")
        
    except requests.exceptions.RequestException as e:
        log(f"Network error during testing: {str(e)}")
        sys.exit(1)
    except Exception as e:
        log(f"Error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <base_url>")
        print("Example: python test_deployment.py https://epospea-eight.vercel.app")
        sys.exit(1)
        
    base_url = sys.argv[1].rstrip('/')
    test_deployment(base_url) 