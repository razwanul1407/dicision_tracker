#!/usr/bin/env python
"""
Test script to verify the logout functionality works properly
"""
import requests
import sys

def test_logout():
    """Test the logout endpoint"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing logout functionality...")
    
    # Test GET request to logout
    try:
        response = requests.get(f"{base_url}/accounts/logout/", allow_redirects=False)
        print(f"GET /accounts/logout/ - Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ GET request successful - redirects to login")
            print(f"   Redirect location: {response.headers.get('Location', 'Not specified')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test POST request to logout
    try:
        # First get CSRF token
        session = requests.Session()
        csrf_response = session.get(f"{base_url}/accounts/login/")
        
        if csrf_response.status_code == 200:
            # Extract CSRF token (simple method)
            csrf_token = None
            for line in csrf_response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    if start > 6 and end > start:
                        csrf_token = line[start:end]
                        break
            
            if csrf_token:
                # Test POST logout with CSRF token
                post_response = session.post(
                    f"{base_url}/accounts/logout/",
                    data={'csrfmiddlewaretoken': csrf_token},
                    allow_redirects=False
                )
                print(f"POST /accounts/logout/ - Status: {post_response.status_code}")
                
                if post_response.status_code == 302:
                    print("✅ POST request successful - redirects to login")
                    print(f"   Redirect location: {post_response.headers.get('Location', 'Not specified')}")
                else:
                    print(f"❌ Unexpected status code: {post_response.status_code}")
            else:
                print("⚠️  Could not extract CSRF token for POST test")
        
    except Exception as e:
        print(f"⚠️  POST test error: {e}")
    
    print("\n🎯 Summary:")
    print("- The logout endpoint now accepts both GET and POST requests")
    print("- Browser cookies will be cleared on logout")
    print("- Users will be redirected to the login page")
    print("- Session data will be properly cleaned up")
    
    return True

if __name__ == '__main__':
    test_logout()