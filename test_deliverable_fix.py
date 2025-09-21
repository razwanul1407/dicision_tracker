#!/usr/bin/env python3
"""
Test script to verify deliverable template fixes.
"""

import requests
import time

def test_deliverable_pages():
    """Test that deliverable pages now load without template errors"""
    base_url = "http://127.0.0.1:8000"
    
    test_pages = [
        ("/core/my-deliverables/", "My Deliverables page"),
        ("/core/assigned-deliverables/", "Assigned Deliverables page"),
    ]
    
    print("🔍 Testing deliverable template fixes...")
    
    session = requests.Session()
    
    for url, description in test_pages:
        try:
            response = session.get(f"{base_url}{url}")
            
            if response.status_code == 200:
                print(f"   ✅ {description}: OK (200)")
            elif response.status_code == 302:
                print(f"   ↗️  {description}: Redirect (302) - likely needs login")
            elif response.status_code == 500:
                print(f"   ❌ {description}: Server Error (500) - template issue persists")
                # Check if it's the specific created_by error
                if "created_by" in response.text:
                    print(f"      Still has created_by error")
                else:
                    print(f"      Different server error")
            else:
                print(f"   ⚠️  {description}: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   🔌 {description}: Server not running")
        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")
    
    print("\n📝 Summary:")
    print("   - Fixed deliverable.created_by → deliverable.decision.created_by")
    print("   - Updated templates: my_deliverables.html, assigned_deliverables.html, deliverable_detail.html")
    print("   - The 'created_by' attribute error should now be resolved")

if __name__ == "__main__":
    test_deliverable_pages()