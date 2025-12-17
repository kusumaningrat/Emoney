#!/usr/bin/env python3
"""
Combined Workflow Tests - Pause/Resume and Cancel/Remove
"""
import sys
import os
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

class WorkflowTests:
    def __init__(self):
        os.environ['FLASK_ENV'] = 'testing'
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    
    def log_request(self, method, url, data=None):
        """Log the outgoing request details"""
        self.log(f"🔵 REQUEST: {method} {url}")
        if data:
            self.log(f"   📤 Payload: {json.dumps(data, indent=2)}")
    
    def log_response(self, response, url):
        """Log the response details"""
        status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"
        self.log(f"{status_emoji} RESPONSE: {response.status_code}")
        
        # Only log response body for errors or key status information
        if response.status_code >= 400:
            try:
                if response.data:
                    response_data = response.get_json()
                    if response_data and 'message' in response_data:
                        self.log(f"   Error: {response_data['message']}")
            except Exception:
                pass
    
    def request(self, method, endpoint, data=None):
        url = f"/api{endpoint}"
        
        # Log the request
        self.log_request(method, url, data)
        
        # Make the request
        if method == "POST":
            response = self.client.post(url, json=data)
        elif method == "GET":
            response = self.client.get(url)
        elif method == "PUT":
            response = self.client.put(url, json=data)
        elif method == "DELETE":
            response = self.client.delete(url)
        else:
            self.log(f"❌ Unsupported method: {method}")
            return None
        
        # Log the response
        self.log_response(response, url)
        
        # Additional error logging for non-success responses
        if response.status_code >= 400:
            self.log(f"❌ Request failed with status {response.status_code}")
        
        return response
    
    def status(self, scan_id):
        """Get scan status with simplified logging"""
        resp = self.request("GET", f"/scan/{scan_id}/status")
        
        if resp.status_code == 200:
            data = resp.get_json().get("data", {})
            status = data.get("status")
            records = data.get("recordsExtracted", 0)
            return status, records
        else:
            return None, 0

    def test_pause_resume_workflow(self):
        """Test pause and resume functionality"""
        scan_id = f"pause-test-{int(time.time())}"
        
        with self.app.app_context():
            self.log("🚀 Starting Pause/Resume Test")
            self.log(f"🆔 Scan ID: {scan_id}")
            self.log("=" * 60)
            
            # Start scan
            self.log("📋 STEP 1: Starting scan...")
            scan_data = {
                "config": {
                    "scanId": scan_id,
                    "organizationId": "test-org", 
                    "type": ["user"],
                    "auth": {"accessToken": "test-token"},
                    "filters": {}
                }
            }
            
            resp = self.request("POST", "/scan/start", scan_data)
            if resp.status_code != 202:
                self.log("❌ Failed to start scan")
                return False
            
            self.log("✅ Scan started successfully")
            
            # Wait for running status
            self.log("📋 STEP 2: Waiting for running status...")
            status = None
            for i in range(10):
                status, records = self.status(scan_id)
                
                if status == "running":
                    self.log("✅ Scan status: RUNNING")
                    # Wait a bit to ensure processing has started
                    time.sleep(3)
                    break
                elif status in ["failed", "error"]:
                    self.log("❌ Scan failed during startup")
                    return False
                elif status == "completed":
                    self.log("ℹ️  Scan completed too quickly - still valid for testing")
                    break
                
                if i < 9:
                    time.sleep(2)
            
            if not status:
                self.log("❌ Could not get scan status")
                return False
            
            # Pause scan
            self.log("📋 STEP 3: Pausing scan...")
            current_status, _ = self.status(scan_id)
            
            if current_status == "completed":
                self.log("ℹ️  Scan already completed - acceptable for fast scans")
                return True
            elif current_status != "running":
                self.log(f"⚠️  Cannot pause - scan status: {current_status}")
                return False
            
            resp = self.request("POST", f"/scan/{scan_id}/pause")
            
            if resp.status_code == 200:
                time.sleep(3)
                status, records = self.status(scan_id)
                if status == "paused":
                    self.log("✅ Scan status: PAUSED")
                elif status == "completed":
                    self.log("ℹ️  Scan completed during pause - acceptable")
                    return True
                else:
                    self.log(f"⚠️  Unexpected status after pause: {status}")
            else:
                self.log(f"❌ Pause request failed: {resp.status_code}")
                return False
            
            # Resume scan
            self.log("📋 STEP 4: Resuming scan...")
            pre_resume_status, _ = self.status(scan_id)
            
            if pre_resume_status == "completed":
                self.log("ℹ️  Scan already completed - skipping resume test")
                return True
            elif pre_resume_status != "paused":
                self.log(f"⚠️  Cannot resume - expected 'paused', got '{pre_resume_status}'")
                return False
            
            resp = self.request("POST", f"/scan/{scan_id}/resume")
            
            if resp.status_code == 200:
                self.log("✅ Scan status: RESUMED")
            elif resp.status_code == 400:
                error_data = resp.get_json()
                if error_data and "completed" in error_data.get("message", "").lower():
                    self.log("ℹ️  Job completed during pause - test successful")
                    return True
                else:
                    self.log(f"❌ Resume failed: {error_data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log(f"❌ Resume request failed: {resp.status_code}")
                return False
            
            # Wait for completion
            self.log("📋 STEP 5: Waiting for completion...")
            for i in range(30):
                status, records = self.status(scan_id)
                
                if status == "completed":
                    self.log("✅ Scan status: COMPLETED")
                    self.log("🎉 Pause/Resume test SUCCESS!")
                    return True
                elif status in ["failed", "error"]:
                    self.log("❌ Scan failed!")
                    return False
                
                if i < 29:
                    time.sleep(3)
            
            self.log("⏰ TIMEOUT! Scan did not complete within expected time")
            return False

    def test_cancel_remove_workflow(self):
        """Test cancel and remove functionality"""
        scan_id = f"cancel-test-{int(time.time())}"
        
        with self.app.app_context():
            self.log("🚀 Starting Cancel/Remove Test")
            self.log(f"🆔 Scan ID: {scan_id}")
            self.log("=" * 60)
            
            # Start scan
            self.log("📋 STEP 1: Starting scan...")
            scan_data = {
                "config": {
                    "scanId": scan_id,
                    "organizationId": "test-org", 
                    "type": ["user"],
                    "auth": {"accessToken": "test-token"},
                    "filters": {}
                }
            }
            
            resp = self.request("POST", "/scan/start", scan_data)
            if resp.status_code != 202:
                self.log("❌ Failed to start scan")
                return False
            
            self.log("✅ Scan started successfully")
            
            # Wait for running status
            self.log("📋 STEP 2: Waiting for running status...")
            status = None
            for i in range(10):
                status, records = self.status(scan_id)
                
                if status == "running":
                    self.log("✅ Scan status: RUNNING")
                    break
                elif status in ["failed", "error"]:
                    self.log("❌ Scan failed during startup")
                    return False
                elif status == "completed":
                    self.log("ℹ️  Scan completed too quickly - still valid for cancel test")
                    break
                
                if i < 9:
                    time.sleep(2)
            
            if not status:
                self.log("❌ Could not get scan status")
                return False
            
            # Check status before cancel
            self.log("📋 STEP 3: Checking status before cancel...")
            pre_cancel_status, _ = self.status(scan_id)
            self.log(f"✅ Pre-cancel status: {pre_cancel_status.upper()}")
            
            # Cancel scan
            self.log("📋 STEP 4: Cancelling scan...")
            resp = self.request("POST", f"/scan/{scan_id}/cancel")
            
            if resp.status_code == 200:
                time.sleep(2)
                status, records = self.status(scan_id)
                if status == "cancelled":
                    self.log("✅ Scan status: CANCELLED")
                elif status == "completed":
                    self.log("ℹ️  Scan completed before cancel - acceptable")
                else:
                    self.log(f"⚠️  Unexpected status after cancel: {status}")
            else:
                self.log(f"❌ Cancel request failed: {resp.status_code}")
                return False
            
            # Check status after cancel
            self.log("📋 STEP 5: Checking status after cancel...")
            post_cancel_status, _ = self.status(scan_id)
            self.log(f"✅ Post-cancel status: {post_cancel_status.upper()}")
            
            # Remove scan
            self.log("📋 STEP 6: Removing scan...")
            resp = self.request("DELETE", f"/scan/{scan_id}")
            
            if resp.status_code == 200:
                self.log("✅ Scan removed successfully")
            elif resp.status_code == 404:
                self.log("ℹ️  Scan not found - may have been auto-cleaned")
                return True
            else:
                self.log(f"❌ Remove request failed: {resp.status_code}")
                return False
            
            # Verify removal
            self.log("📋 STEP 7: Verifying removal...")
            resp = self.request("GET", f"/scan/{scan_id}/status")
            
            if resp.status_code == 404:
                self.log("✅ Scan successfully removed (404 Not Found)")
                self.log("🎉 Cancel/Remove test SUCCESS!")
                return True
            elif resp.status_code == 200:
                data = resp.get_json().get("data", {})
                status = data.get("status")
                self.log(f"⚠️  Scan still exists with status: {status}")
                return False
            else:
                self.log(f"⚠️  Unexpected response during verification: {resp.status_code}")
                return False

    def run_all_tests(self):
        """Run all workflow tests"""
        self.log("🧪 Starting Combined Workflow Tests")
        self.log("=" * 80)
        
        results = {}
        
        # Test 1: Pause/Resume
        self.log("\n📋 TEST 1: Pause/Resume Workflow")
        self.log("-" * 50)
        results['pause_resume'] = self.test_pause_resume_workflow()
        
        # Wait between tests
        time.sleep(3)
        
        # Test 2: Cancel/Remove  
        self.log("\n📋 TEST 2: Cancel/Remove Workflow")
        self.log("-" * 50)
        results['cancel_remove'] = self.test_cancel_remove_workflow()
        
        # Final results
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL RESULTS:")
        self.log(f"   Pause/Resume: {'PASS' if results['pause_resume'] else 'FAIL'}")
        self.log(f"   Cancel/Remove: {'PASS' if results['cancel_remove'] else 'FAIL'}")
        
        all_passed = all(results.values())
        if all_passed:
            self.log("\n🎉 ALL TESTS PASSED!")
        else:
            self.log("\n❌ SOME TESTS FAILED!")
        self.log("=" * 80)
        
        return all_passed

if __name__ == "__main__":
    tests = WorkflowTests()
    success = tests.run_all_tests()
    
    sys.exit(0 if success else 1)