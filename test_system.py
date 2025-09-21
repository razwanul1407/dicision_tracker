#!/usr/bin/env python3
"""
Test script for the Event Decision Tracker system.
Tests logout functionality and template fixes.
"""

import requests
import time
from requests.cookies import RequestsCookieJar
import sys

class SystemTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.session = requests.Session()
        
    def test_logout_functionality(self):
        """Test the logout functionality with cookie clearing"""
        print("🔐 Testing logout functionality...")
        
        # Test GET request to logout
        try:
            response = self.session.get(f"{self.base_url}/accounts/logout/")
            print(f"   GET /accounts/logout/ -> Status: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✅ GET logout redirects properly")
            else:
                print(f"   ❌ GET logout failed with status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Server not running. Please start the server first.")
            return False
            
        # Test POST request to logout
        try:
            # Get CSRF token first
            csrf_response = self.session.get(f"{self.base_url}/accounts/login/")
            csrf_token = None
            if 'csrftoken' in self.session.cookies:
                csrf_token = self.session.cookies['csrftoken']
            
            if csrf_token:
                post_data = {'csrfmiddlewaretoken': csrf_token}
                response = self.session.post(f"{self.base_url}/accounts/logout/", data=post_data)
                print(f"   POST /accounts/logout/ -> Status: {response.status_code}")
                
                if response.status_code == 302:
                    print("   ✅ POST logout redirects properly")
                else:
                    print(f"   ❌ POST logout failed with status {response.status_code}")
            else:
                print("   ⚠️  Could not get CSRF token for POST test")
                
        except Exception as e:
            print(f"   ❌ POST logout test failed: {e}")
            
        return True
    
    def test_template_access(self):
        """Test access to key template pages"""
        print("\n📄 Testing template access...")
        
        test_pages = [
            ("/", "Home page"),
            ("/accounts/login/", "Login page"),
            ("/accounts/register/", "Register page"),
        ]
        
        for url, description in test_pages:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                status = "✅ OK" if response.status_code in [200, 302] else f"❌ {response.status_code}"
                print(f"   {description}: {status}")
            except Exception as e:
                print(f"   {description}: ❌ Error - {e}")
    
    def test_cookie_handling(self):
        """Test cookie handling in logout"""
        print("\n🍪 Testing cookie handling...")
        
        # Set some test cookies
        self.session.cookies.set('sessionid', 'test_session_id')
        self.session.cookies.set('csrftoken', 'test_csrf_token')
        
        print(f"   Cookies before logout: {len(self.session.cookies)} cookies")
        
        # Test logout
        try:
            response = self.session.get(f"{self.base_url}/accounts/logout/")
            print(f"   Cookies after logout: {len(self.session.cookies)} cookies")
            
            # Check if specific cookies are cleared
            if 'sessionid' not in self.session.cookies:
                print("   ✅ sessionid cookie cleared")
            else:
                print("   ⚠️  sessionid cookie still present")
                
        except Exception as e:
            print(f"   ❌ Cookie test failed: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Event Decision Tracker - System Test Suite")
        print("=" * 50)
        
        self.test_logout_functionality()
        self.test_template_access()
        self.test_cookie_handling()
        
        print("\n" + "=" * 50)
        print("✨ Test suite completed!")
        print("\nTo test the full system:")
        print("1. Start the server: python manage.py runserver")
        print("2. Create a user and login")
        print("3. Test the logout functionality")
        print("4. Verify cookies are cleared in browser dev tools")

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()