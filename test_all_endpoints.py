import requests
import json
import time
import os
from datetime import datetime, date
from typing import Dict, Any, Optional

class EtlabAPITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.test_results = {}
        self.response_data = {}
        self.output_dir = f"test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
        
    def save_response_data(self, endpoint_name: str, response: requests.Response, success: bool):
        """Save response data to individual files"""
        try:
            # Create filename
            filename = f"{endpoint_name.lower().replace(' ', '_')}_response.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Prepare response data
            response_info = {
                'endpoint': endpoint_name,
                'url': response.url,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'request_method': response.request.method,
            }
            
            # Try to parse JSON response
            try:
                response_info['data'] = response.json()
            except json.JSONDecodeError:
                response_info['data'] = response.text
                response_info['data_type'] = 'text'
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_info, f, indent=2, ensure_ascii=False)
            
            # Store in memory for summary
            self.response_data[endpoint_name] = response_info
            
            print(f"      💾 Response saved to: {filename}")
            
        except Exception as e:
            print(f"      ⚠️  Failed to save response: {str(e)}")

    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
    
    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        """Print test result with formatting"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token exists
        if self.token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.token:
            kwargs['headers']['Authorization'] = self.token
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            raise
    
    def test_status(self) -> bool:
        """Test the status endpoint"""
        try:
            response = self.make_request('GET', '/api/status')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'I am alive':
                    self.print_test_result("Status Check", True, "API is alive and responding")
                    self.save_response_data("Status Check", response, True)
                    return True
                else:
                    self.print_test_result("Status Check", False, f"Unexpected message: {data}")
                    self.save_response_data("Status Check", response, False)
                    return False
            else:
                self.print_test_result("Status Check", False, f"Status code: {response.status_code}")
                self.save_response_data("Status Check", response, False)
                return False
        except Exception as e:
            self.print_test_result("Status Check", False, f"Error: {str(e)}")
            return False
    
    def test_login(self, username: str, password: str) -> bool:
        """Test login functionality"""
        try:
            payload = {
                "username": username,
                "password": password
            }
            
            response = self.make_request('POST', '/api/login', json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    self.print_test_result("Login", True, f"Token received: {self.token[:20]}...")
                    self.save_response_data("Login", response, True)
                    return True
                else:
                    self.print_test_result("Login", False, "No token in response")
                    self.save_response_data("Login", response, False)
                    return False
            elif response.status_code == 401:
                self.print_test_result("Login", False, "Invalid credentials")
                self.save_response_data("Login", response, False)
                return False
            else:
                self.print_test_result("Login", False, f"Status code: {response.status_code}")
                self.save_response_data("Login", response, False)
                return False
        except Exception as e:
            self.print_test_result("Login", False, f"Error: {str(e)}")
            return False
    
    def test_profile(self) -> bool:
        """Test profile endpoint"""
        if not self.token:
            self.print_test_result("Profile", False, "No authentication token")
            return False
        
        try:
            response = self.make_request('GET', '/api/profile')
            
            if response.status_code == 200:
                data = response.json()
                if 'name' in data and 'university_reg_no' in data:
                    self.print_test_result("Profile", True, f"Profile data retrieved for: {data.get('name', 'Unknown')}")
                    self.save_response_data("Profile", response, True)
                    return True
                else:
                    self.print_test_result("Profile", False, "Missing expected profile fields")
                    self.save_response_data("Profile", response, False)
                    return False
            elif response.status_code == 401:
                self.print_test_result("Profile", False, "Token expired or invalid")
                self.save_response_data("Profile", response, False)
                return False
            else:
                self.print_test_result("Profile", False, f"Status code: {response.status_code}")
                self.save_response_data("Profile", response, False)
                return False
        except Exception as e:
            self.print_test_result("Profile", False, f"Error: {str(e)}")
            return False
    
    def test_attendance(self, semester: int = 3) -> bool:
        """Test attendance endpoint"""
        if not self.token:
            self.print_test_result("Attendance", False, "No authentication token")
            return False
        
        try:
            response = self.make_request('GET', f'/api/attendance?semester={semester}')
            
            if response.status_code == 200:
                data = response.json()
                if 'university_reg_no' in data:
                    subject_count = len([k for k in data.keys() if k not in ['university_reg_no', 'roll_no', 'name']])
                    self.print_test_result("Attendance", True, f"Attendance data for {subject_count} subjects")
                    self.save_response_data("Attendance", response, True)
                    return True
                else:
                    self.print_test_result("Attendance", False, "Missing expected attendance fields")
                    self.save_response_data("Attendance", response, False)
                    return False
            elif response.status_code == 400:
                self.print_test_result("Attendance", False, "Invalid semester parameter")
                self.save_response_data("Attendance", response, False)
                return False
            elif response.status_code == 401:
                self.print_test_result("Attendance", False, "Token expired or invalid")
                self.save_response_data("Attendance", response, False)
                return False
            else:
                self.print_test_result("Attendance", False, f"Status code: {response.status_code}")
                self.save_response_data("Attendance", response, False)
                return False
        except Exception as e:
            self.print_test_result("Attendance", False, f"Error: {str(e)}")
            return False
    
    def test_timetable(self) -> bool:
        """Test timetable endpoint"""
        if not self.token:
            self.print_test_result("Timetable", False, "No authentication token")
            return False
        
        try:
            response = self.make_request('GET', '/api/timetable')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.print_test_result("Timetable", True, f"Timetable with {len(data)} entries")
                    self.save_response_data("Timetable", response, True)
                    return True
                else:
                    self.print_test_result("Timetable", True, "Timetable retrieved (empty or different format)")
                    self.save_response_data("Timetable", response, True)
                    return True
            elif response.status_code == 401:
                self.print_test_result("Timetable", False, "Token expired or invalid")
                self.save_response_data("Timetable", response, False)
                return False
            else:
                self.print_test_result("Timetable", False, f"Status code: {response.status_code}")
                self.save_response_data("Timetable", response, False)
                return False
        except Exception as e:
            self.print_test_result("Timetable", False, f"Error: {str(e)}")
            return False
    
    def test_results(self, semester: int = 3) -> bool:
        """Test results endpoint"""
        if not self.token:
            self.print_test_result("Results", False, "No authentication token")
            return False
        
        try:
            response = self.make_request('GET', f'/api/results?semester={semester}')
            
            if response.status_code == 200:
                data = response.json()
                if 'sessional_exams' in data and 'module_tests' in data and 'class_projects' in data:
                    total_results = data.get('total_sessional_exams', 0) + data.get('total_module_tests', 0) + data.get('total_class_projects', 0)
                    self.print_test_result("Results", True, f"Results retrieved - {data.get('total_sessional_exams', 0)} sessional exams, {data.get('total_module_tests', 0)} module tests, {data.get('total_class_projects', 0)} class projects")
                    self.save_response_data("Results", response, True)
                    return True
                else:
                    self.print_test_result("Results", False, "Missing expected results fields")
                    self.save_response_data("Results", response, False)
                    return False
            elif response.status_code == 400:
                self.print_test_result("Results", False, "Invalid semester parameter")
                self.save_response_data("Results", response, False)
                return False
            elif response.status_code == 401:
                self.print_test_result("Results", False, "Token expired or invalid")
                self.save_response_data("Results", response, False)
                return False
            else:
                self.print_test_result("Results", False, f"Status code: {response.status_code}")
                self.save_response_data("Results", response, False)
                return False
        except Exception as e:
            self.print_test_result("Results", False, f"Error: {str(e)}")
            return False

    def test_present_absent(self, endpoint_name: str, endpoint: str) -> bool:
        """Test present or absent endpoint"""
        if not self.token:
            self.print_test_result(endpoint_name, False, "No authentication token")
            return False
        
        # Use current date parameters
        current_date = date.today()
        month = current_date.month
        year = current_date.year
        semester = 3  # Use semester 3 for testing
        
        try:
            response = self.make_request('GET', f'/api/{endpoint}?month={month}&year={year}&semester={semester}')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.print_test_result(endpoint_name, True, f"{len(data)} records found")
                    self.save_response_data(endpoint_name, response, True)
                    return True
                else:
                    self.print_test_result(endpoint_name, True, f"Data retrieved: {type(data)}")
                    self.save_response_data(endpoint_name, response, True)
                    return True
            elif response.status_code == 400:
                self.print_test_result(endpoint_name, False, "Invalid parameters")
                self.save_response_data(endpoint_name, response, False)
                return False
            elif response.status_code == 401:
                self.print_test_result(endpoint_name, False, "Token expired or invalid")
                self.save_response_data(endpoint_name, response, False)
                return False
            else:
                self.print_test_result(endpoint_name, False, f"Status code: {response.status_code}")
                self.save_response_data(endpoint_name, response, False)
                return False
        except Exception as e:
            self.print_test_result(endpoint_name, False, f"Error: {str(e)}")
            return False
    
    def test_logout(self) -> bool:
        """Test logout endpoint"""
        if not self.token:
            self.print_test_result("Logout", False, "No authentication token")
            return False
        
        try:
            response = self.make_request('GET', '/api/logout')
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'successfully' in data['message'].lower():
                    self.print_test_result("Logout", True, "Successfully logged out")
                    self.save_response_data("Logout", response, True)
                    self.token = None  # Clear token
                    return True
                else:
                    self.print_test_result("Logout", False, f"Unexpected response: {data}")
                    self.save_response_data("Logout", response, False)
                    return False
            elif response.status_code == 401:
                self.print_test_result("Logout", False, "Token expired or invalid")
                self.save_response_data("Logout", response, False)
                return False
            else:
                self.print_test_result("Logout", False, f"Status code: {response.status_code}")
                self.save_response_data("Logout", response, False)
                return False
        except Exception as e:
            self.print_test_result("Logout", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self, username: str, password: str):
        """Run all tests in sequence"""
        self.print_header("ETLAB API Comprehensive Test Suite")
        
        print(f"🔧 Testing API at: {self.base_url}")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test sequence
        tests = [
            ("Status Check", lambda: self.test_status()),
            ("Login", lambda: self.test_login(username, password)),
            ("Profile", lambda: self.test_profile()),
            ("Attendance", lambda: self.test_attendance()),
            ("Results", lambda: self.test_results()),
            ("Timetable", lambda: self.test_timetable()),
            ("Present Records", lambda: self.test_present_absent("Present", "present")),
            ("Absent Records", lambda: self.test_present_absent("Absent", "absent")),
            ("Logout", lambda: self.test_logout()),
        ]
        
        passed = 0
        total = len(tests)
        
        self.print_header("Running Tests")
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                success = test_func()
                if success:
                    passed += 1
            except Exception as e:
                self.print_test_result(test_name, False, f"Unexpected error: {str(e)}")
            
            time.sleep(0.5)  # Small delay between tests
        
        # Summary
        self.print_header("Test Summary")
        print(f"📊 Results: {passed}/{total} tests passed")
        print(f"✅ Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All tests passed! Your API is working perfectly!")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        # Save comprehensive results
        self.save_comprehensive_results()
        
        return self.test_results
    
    def save_comprehensive_results(self):
        """Save comprehensive test results and summaries"""
        try:
            # Save main test results
            results_file = os.path.join(self.output_dir, "test_results_summary.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            # Save all response data in one file
            all_responses_file = os.path.join(self.output_dir, "all_responses_data.json")
            with open(all_responses_file, 'w', encoding='utf-8') as f:
                json.dump(self.response_data, f, indent=2, ensure_ascii=False)
            
            # Create a detailed HTML report
            self.create_html_report()
            
            # Create a summary text file
            self.create_text_summary()
            
            print(f"\n📄 Comprehensive results saved to directory: {self.output_dir}")
            print(f"📋 Files created:")
            print(f"   - test_results_summary.json (Test pass/fail results)")
            print(f"   - all_responses_data.json (All API response data)")
            print(f"   - test_report.html (Visual HTML report)")
            print(f"   - test_summary.txt (Human-readable summary)")
            print(f"   - Individual response files for each endpoint")
            
        except Exception as e:
            print(f"❌ Error saving comprehensive results: {str(e)}")
    
    def create_html_report(self):
        """Create an HTML report of test results"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ETLAB API Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .summary {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .pass {{ background: #d4edda; border: 1px solid #c3e6cb; }}
        .fail {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
        .endpoint-data {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .json-data {{ background: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; font-family: monospace; font-size: 12px; }}
        .timestamp {{ color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 ETLAB API Test Report</h1>
            <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Test Summary</h2>
            <p><strong>Total Tests:</strong> {len(self.test_results)}</p>
            <p><strong>Passed:</strong> {sum(1 for r in self.test_results.values() if r['success'])}</p>
            <p><strong>Failed:</strong> {sum(1 for r in self.test_results.values() if not r['success'])}</p>
            <p><strong>Success Rate:</strong> {(sum(1 for r in self.test_results.values() if r['success'])/len(self.test_results)*100):.1f}%</p>
        </div>
        
        <h2>🔍 Test Details</h2>
"""
            
            for test_name, result in self.test_results.items():
                status_class = "pass" if result['success'] else "fail"
                status_icon = "✅" if result['success'] else "❌"
                
                html_content += f"""
        <div class="test-result {status_class}">
            <h3>{status_icon} {test_name}</h3>
            <p><strong>Status:</strong> {'PASSED' if result['success'] else 'FAILED'}</p>
            <p><strong>Details:</strong> {result['details']}</p>
            <p class="timestamp">Timestamp: {result['timestamp']}</p>
"""
                
                # Add response data if available
                if test_name in self.response_data:
                    response_info = self.response_data[test_name]
                    html_content += f"""
            <div class="endpoint-data">
                <h4>📡 Response Details</h4>
                <p><strong>URL:</strong> {response_info.get('url', 'N/A')}</p>
                <p><strong>Status Code:</strong> {response_info.get('status_code', 'N/A')}</p>
                <p><strong>Method:</strong> {response_info.get('request_method', 'N/A')}</p>
                <details>
                    <summary>View Response Data</summary>
                    <div class="json-data">
                        <pre>{json.dumps(response_info.get('data', {}), indent=2)}</pre>
                    </div>
                </details>
            </div>
"""
                
                html_content += "        </div>\n"
            
            html_content += """
    </div>
</body>
</html>
"""
            
            html_file = os.path.join(self.output_dir, "test_report.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"❌ Error creating HTML report: {str(e)}")
    
    def create_text_summary(self):
        """Create a human-readable text summary"""
        try:
            summary_content = f"""
ETLAB API Test Summary Report
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
--------
Total Tests: {len(self.test_results)}
Passed: {sum(1 for r in self.test_results.values() if r['success'])}
Failed: {sum(1 for r in self.test_results.values() if not r['success'])}
Success Rate: {(sum(1 for r in self.test_results.values() if r['success'])/len(self.test_results)*100):.1f}%

DETAILED RESULTS
---------------
"""
            
            for test_name, result in self.test_results.items():
                status = "PASSED" if result['success'] else "FAILED"
                summary_content += f"\n{test_name}: {status}\n"
                summary_content += f"  Details: {result['details']}\n"
                summary_content += f"  Time: {result['timestamp']}\n"
                
                if test_name in self.response_data:
                    response_info = self.response_data[test_name]
                    summary_content += f"  URL: {response_info.get('url', 'N/A')}\n"
                    summary_content += f"  Status Code: {response_info.get('status_code', 'N/A')}\n"
                
                summary_content += "\n" + "-" * 50 + "\n"
            
            summary_file = os.path.join(self.output_dir, "test_summary.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
                
        except Exception as e:
            print(f"❌ Error creating text summary: {str(e)}")
    
    def save_results(self, filename: str = "test_results.json"):
        """Save test results to a JSON file (legacy method)"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Test results saved to: {filepath}")

def main():
    """Main function to run the tests"""
    print("🚀 ETLAB API Test Suite")
    print("=" * 40)
    
    # Get user input
    base_url = input("Enter API base URL (default: http://localhost:5000): ").strip()
    if not base_url:
        base_url = "http://localhost:5000"
    
    print("\nEnter your etlab credentials:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required!")
        return
    
    # Create tester and run tests
    tester = EtlabAPITester(base_url)
    
    try:
        results = tester.run_comprehensive_test(username, password)
        
        print(f"\n📁 All results saved to: {tester.output_dir}")
        print("\n🎯 Next Steps:")
        print("1. Check the HTML report for visual results")
        print("2. Review individual endpoint response files")
        print("3. Use the JSON files for programmatic analysis")
        
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")

if __name__ == "__main__":
    main()