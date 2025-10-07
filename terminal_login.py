#!/usr/bin/env python3
"""
ETLab Terminal Login Interface
Interactive command-line interface for ETLab API
"""

import requests
import json
import getpass
import os
from datetime import datetime

class ETLabTerminal:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:5000/api'
        self.token = None
        self.username = None
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the application header"""
        print("=" * 60)
        print("🎓 ETLab API Terminal Interface")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.token:
            print(f"👤 Logged in as: {self.username}")
            print("🟢 Status: Connected")
        else:
            print("🔴 Status: Not logged in")
        print("=" * 60)
        print()

    def print_menu(self):
        """Print the main menu"""
        if not self.token:
            print("🔐 LOGIN REQUIRED")
            print("1. Login to ETLab")
            print("2. Check API Status")
            print("0. Exit")
        else:
            print("📋 MAIN MENU")
            print("1. 👤 View Profile")
            print("2. 📊 Get Results by Semester")
            print("3. 📅 View Attendance")
            print("4. 🕐 View Timetable")
            print("5. ✅ Mark Present")
            print("6. ❌ Mark Absent")
            print("7. 🔍 Check API Status")
            print("8. 🔐 Logout")
            print("0. Exit")
        print()

    def make_request(self, endpoint, method='GET', data=None):
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            
            return response.status_code, response.json()
        except requests.exceptions.ConnectionError:
            return None, {"error": "Cannot connect to server. Make sure Flask server is running."}
        except Exception as e:
            return None, {"error": str(e)}

    def login(self):
        """Handle user login"""
        print("🔐 LOGIN TO ETLAB")
        print("-" * 20)
        
        username = input("👤 Username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            return False
        
        password = getpass.getpass("🔑 Password: ")
        if not password:
            print("❌ Password cannot be empty!")
            return False
        
        print("\n🔄 Logging in...")
        status, response = self.make_request('/login', 'POST', {
            'username': username,
            'password': password
        })
        
        if status == 200 and 'token' in response:
            self.token = response['token']
            self.username = username
            print(f"✅ {response['message']}")
            print(f"🎉 Welcome, {username}!")
            return True
        else:
            print(f"❌ Login failed: {response.get('message', 'Unknown error')}")
            return False

    def logout(self):
        """Handle user logout"""
        print("🔄 Logging out...")
        status, response = self.make_request('/logout', 'POST')
        
        self.token = None
        self.username = None
        print("✅ Logged out successfully!")

    def view_profile(self):
        """View user profile"""
        print("👤 PROFILE INFORMATION")
        print("-" * 25)
        
        status, response = self.make_request('/profile')
        
        if status == 200:
            print("✅ Profile retrieved successfully!")
            print("\n📋 Details:")
            for key, value in response.items():
                if key != 'message':
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"❌ Failed to get profile: {response.get('message', 'Unknown error')}")

    def get_results(self):
        """Get exam results by semester"""
        print("📊 EXAM RESULTS")
        print("-" * 15)
        
        try:
            semester = int(input("📚 Enter semester (1-8): ").strip())
            if semester < 1 or semester > 8:
                print("❌ Invalid semester! Please enter 1-8.")
                return
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
            return
        
        print(f"\n🔄 Fetching results for semester {semester}...")
        status, response = self.make_request(f'/results?semester={semester}')
        
        if status == 200:
            print(f"✅ Results for Semester {semester}:")
            print(f"📈 Sessional Exams: {response.get('total_sessional_exams', 0)}")
            print(f"📝 Module Tests: {response.get('total_module_tests', 0)}")
            print(f"🎯 Class Projects: {response.get('total_class_projects', 0)}")
            print(f"📋 Assignments: {response.get('total_assignments', 0)}")
            print(f"📚 Tutorials: {response.get('total_tutorials', 0)}")
            
            # Show sessional exam details
            if response.get('sessional_exams'):
                print(f"\n📈 SESSIONAL EXAM DETAILS:")
                for exam in response['sessional_exams']:
                    subject = exam.get('subject_code', exam.get('subject', 'Unknown'))
                    marks = exam.get('marks_obtained', 'N/A')
                    max_marks = exam.get('maximum_marks', 'N/A')
                    print(f"  • {subject}: {marks}/{max_marks}")
            
            # Show assignments if any
            if response.get('assignments'):
                print(f"\n📋 ASSIGNMENTS:")
                for assignment in response['assignments']:
                    subject = assignment.get('subject', 'Unknown')
                    marks = assignment.get('marks_obtained', 'N/A')
                    max_marks = assignment.get('maximum_marks', 'N/A')
                    print(f"  • {subject}: {marks}/{max_marks}")
        else:
            print(f"❌ Failed to get results: {response.get('message', 'Unknown error')}")

    def view_attendance(self):
        """View attendance records"""
        print("📅 ATTENDANCE RECORDS")
        print("-" * 20)
        
        status, response = self.make_request('/attendance')
        
        if status == 200:
            print("✅ Attendance retrieved successfully!")
            print(json.dumps(response, indent=2))
        else:
            print(f"❌ Failed to get attendance: {response.get('message', 'Unknown error')}")

    def view_timetable(self):
        """View class timetable"""
        print("🕐 CLASS TIMETABLE")
        print("-" * 17)
        
        status, response = self.make_request('/timetable')
        
        if status == 200:
            print("✅ Timetable retrieved successfully!")
            print(json.dumps(response, indent=2))
        else:
            print(f"❌ Failed to get timetable: {response.get('message', 'Unknown error')}")

    def mark_present(self):
        """Mark attendance as present"""
        print("✅ MARK PRESENT")
        print("-" * 14)
        
        subject = input("📚 Subject code (e.g., 24CST303): ").strip()
        date = input("📅 Date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if not subject:
            print("❌ Subject code cannot be empty!")
            return
        
        status, response = self.make_request('/present', 'POST', {
            'subject': subject,
            'date': date
        })
        
        if status == 200:
            print(f"✅ {response.get('message', 'Marked present successfully!')}")
        else:
            print(f"❌ Failed to mark present: {response.get('message', 'Unknown error')}")

    def mark_absent(self):
        """Mark attendance as absent"""
        print("❌ MARK ABSENT")
        print("-" * 13)
        
        subject = input("📚 Subject code (e.g., 24CST303): ").strip()
        date = input("📅 Date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if not subject:
            print("❌ Subject code cannot be empty!")
            return
        
        status, response = self.make_request('/absent', 'POST', {
            'subject': subject,
            'date': date
        })
        
        if status == 200:
            print(f"✅ {response.get('message', 'Marked absent successfully!')}")
        else:
            print(f"❌ Failed to mark absent: {response.get('message', 'Unknown error')}")

    def check_status(self):
        """Check API status"""
        print("🔍 API STATUS")
        print("-" * 12)
        
        status, response = self.make_request('/status')
        
        if status == 200:
            print("✅ API is running successfully!")
            print(f"📊 Status: {response}")
        else:
            print(f"❌ API check failed: {response.get('message', 'Unknown error')}")

    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\nPress Enter to continue...")

    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            try:
                choice = input("🎯 Select an option: ").strip()
                print()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    if not self.token:
                        if self.login():
                            self.wait_for_enter()
                    else:
                        self.view_profile()
                        self.wait_for_enter()
                elif choice == '2':
                    if not self.token:
                        self.check_status()
                        self.wait_for_enter()
                    else:
                        self.get_results()
                        self.wait_for_enter()
                elif choice == '3' and self.token:
                    self.view_attendance()
                    self.wait_for_enter()
                elif choice == '4' and self.token:
                    self.view_timetable()
                    self.wait_for_enter()
                elif choice == '5' and self.token:
                    self.mark_present()
                    self.wait_for_enter()
                elif choice == '6' and self.token:
                    self.mark_absent()
                    self.wait_for_enter()
                elif choice == '7' and self.token:
                    self.check_status()
                    self.wait_for_enter()
                elif choice == '8' and self.token:
                    self.logout()
                    self.wait_for_enter()
                else:
                    print("❌ Invalid option! Please try again.")
                    self.wait_for_enter()
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                self.wait_for_enter()

if __name__ == "__main__":
    app = ETLabTerminal()
    app.run()