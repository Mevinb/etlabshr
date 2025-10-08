#!/usr/bin/env python3
"""
ETLab Terminal Login Interface - Direct Mode
Interactive command-line interface for ETLab API using direct app calls
"""

import json
import getpass
import os
from datetime import datetime
from app import create_app

class ETLabTerminalDirect:
    def __init__(self):
        self.app = create_app()
        self.token = None
        self.username = None
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the application header"""
        print("=" * 60)
        print("🎓 ETLab API Terminal Interface (Direct Mode)")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.token:
            print(f"👤 Logged in as: {self.username}")
            print(f"🔴 Status: ✅ Authenticated")
        else:
            print("🔴 Status: Not logged in")
        print("=" * 60)
        print()

    def login(self):
        """Handle user login"""
        print("🔐 LOGIN TO ETLAB")
        print("-" * 20)
        
        username = input("👤 Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            return False
            
        password = getpass.getpass("🔒 Password: ")
        if not password:
            print("❌ Password cannot be empty")
            return False
        
        print("\n🔄 Authenticating...")
        
        try:
            with self.app.test_client() as client:
                login_data = {
                    "username": username,
                    "password": password
                }
                
                response = client.post('/api/login', 
                                     data=json.dumps(login_data),
                                     content_type='application/json')
                
                if response.status_code == 200:
                    data = response.get_json()
                    self.token = data.get('token')
                    self.username = username
                    print("✅ Login successful!")
                    print(f"🔑 Token: {self.token[:20]}...")
                    return True
                else:
                    error_data = response.get_json()
                    print(f"❌ Login failed: {error_data.get('message', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False

    def check_status(self):
        """Check API status"""
        print("🔍 CHECKING API STATUS")
        print("-" * 25)
        
        try:
            with self.app.test_client() as client:
                response = client.get('/api/status')
                
                if response.status_code == 200:
                    print("✅ API is running and healthy")
                    print(f"📊 Status Code: {response.status_code}")
                    print(f"📝 Response: {response.get_data(as_text=True)}")
                else:
                    print(f"❌ API returned error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ API check failed: {e}")

    def get_profile(self):
        """Get user profile"""
        if not self.token:
            print("❌ Please login first")
            return
            
        print("👤 USER PROFILE")
        print("-" * 15)
        
        try:
            with self.app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = client.get('/api/profile', headers=headers)
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Profile retrieved successfully!")
                    print(json.dumps(data, indent=2))
                else:
                    error_data = response.get_json()
                    print(f"❌ Failed to get profile: {error_data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error getting profile: {e}")

    def get_results(self):
        """Get exam results"""
        if not self.token:
            print("❌ Please login first")
            return
            
        print("📊 EXAM RESULTS")
        print("-" * 15)
        
        semester = input("🎓 Enter semester (or press Enter for all): ").strip()
        
        try:
            with self.app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.token}'}
                url = '/api/results'
                if semester:
                    url += f'?semester={semester}'
                    
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Results retrieved successfully!")
                    
                    # Display results summary
                    print(f"\n📊 Results Summary:")
                    print(f"   📝 Sessional Exams: {data.get('total_sessional_exams', 0)}")
                    print(f"   🧪 Module Tests: {data.get('total_module_tests', 0)}")
                    print(f"   📋 Class Projects: {data.get('total_class_projects', 0)}")
                    print(f"   📄 Assignments: {data.get('total_assignments', 0)}")
                    print(f"   📚 Tutorials: {data.get('total_tutorials', 0)}")
                    
                    print(f"\n   💡 For end semester results, use option 3 from the main menu")
                    
                    # Display Sessional Exams
                    sessional_exams = data.get('sessional_exams', [])
                    if sessional_exams:
                        print(f"📝 Sessional Examination Results:")
                        print("   " + "─" * 35)
                        for i, exam in enumerate(sessional_exams[:5]):  # Show first 5
                            subject_code = exam.get('subject_code', 'N/A')
                            marks = exam.get('marks_obtained', 'N/A')
                            max_marks = exam.get('maximum_marks', 'N/A')
                            semester_text = exam.get('semester', 'N/A')
                            
                            print(f"   📖 {subject_code} (Sem {semester_text}): {marks}/{max_marks}")
                        
                        if len(sessional_exams) > 5:
                            print(f"   ... and {len(sessional_exams) - 5} more sessional exams")
                        print()
                    
                    # Display Module Tests
                    module_tests = data.get('module_tests', [])
                    if module_tests:
                        print(f"🧪 Module Test Results:")
                        print("   " + "─" * 22)
                        for i, test in enumerate(module_tests[:5]):  # Show first 5
                            subject = test.get('subject', 'N/A')
                            marks = test.get('marks_obtained', 'N/A')
                            max_marks = test.get('maximum_marks', 'N/A')
                            semester_text = test.get('semester', 'N/A')
                            
                            print(f"   📖 {subject} (Sem {semester_text}): {marks}/{max_marks}")
                        
                        if len(module_tests) > 5:
                            print(f"   ... and {len(module_tests) - 5} more module tests")
                        print()
                    
                    # Display other categories if they have data
                    other_categories = [
                        ('class_projects', '📋 Class Projects'),
                        ('assignments', '📄 Assignments'),
                        ('tutorials', '📚 Tutorials')
                    ]
                    
                    for category_key, category_title in other_categories:
                        category_data = data.get(category_key, [])
                        if category_data:
                            print(f"{category_title}: {len(category_data)} items")
                    
                    # Show if no results found
                    total_results = sum([
                        len(data.get('sessional_exams', [])),
                        len(data.get('module_tests', [])),
                        len(data.get('class_projects', [])),
                        len(data.get('assignments', [])),
                        len(data.get('tutorials', []))
                    ])
                    
                    if total_results == 0:
                        print("ℹ️ No examination results found for the specified criteria")
                        
                else:
                    error_data = response.get_json()
                    print(f"❌ Failed to get results: {error_data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error getting results: {e}")

    def get_end_semester_results(self):
        """Get end semester examination results"""
        if not self.token:
            print("❌ Please login first")
            return
            
        print("🎓 END SEMESTER RESULTS")
        print("-" * 23)
        
        semester = input("🎓 Enter semester (or press Enter for all): ").strip()
        
        try:
            with self.app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.token}'}
                url = '/api/end-semester-results'
                if semester:
                    url += f'?semester={semester}'
                    
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ End semester results retrieved successfully!")
                    
                    # Display end semester results
                    end_semester_exams = data.get('end_semester_exams', [])
                    
                    if end_semester_exams:
                        print(f"\n🎓 End Semester Examination Results ({len(end_semester_exams)} exams):")
                        print("   " + "═" * 50)
                        
                        for i, exam in enumerate(end_semester_exams, 1):
                            subject_code = exam.get('subject_code', 'N/A')
                            subject_name = exam.get('subject_name', 'N/A')
                            semester_text = exam.get('semester', 'N/A')
                            exam_type = exam.get('exam', 'N/A')
                            marks = exam.get('marks_obtained', 'N/A')
                            max_marks = exam.get('maximum_marks', 'N/A')
                            
                            print(f"\n   📖 {i}. {subject_code}")
                            if subject_name != subject_code and subject_name.strip():
                                print(f"       📝 {subject_name}")
                            print(f"       🎯 Semester: {semester_text}")
                            print(f"       📊 Marks: {marks}/{max_marks}")
                            print(f"       📋 Examination: {exam_type}")
                        
                        # Calculate percentage if possible
                        total_marks = 0
                        total_max = 0
                        valid_exams = 0
                        
                        for exam in end_semester_exams:
                            try:
                                marks = float(exam.get('marks_obtained', 0))
                                max_marks = float(exam.get('maximum_marks', 0))
                                if marks > 0 and max_marks > 0:
                                    total_marks += marks
                                    total_max += max_marks
                                    valid_exams += 1
                            except (ValueError, TypeError):
                                continue
                        
                        if valid_exams > 0 and total_max > 0:
                            percentage = (total_marks / total_max) * 100
                            print(f"\n   📊 Overall Performance:")
                            print(f"       ✅ Total Marks: {total_marks}/{total_max}")
                            print(f"       📈 Percentage: {percentage:.2f}%")
                            print(f"       📚 Valid Exams: {valid_exams}")
                    
                    # Check for available links to semester results with detailed results
                    available_links = data.get('available_links', [])
                    if available_links:
                        print(f"\n🔗 End Semester Result Details Found ({len(available_links)} exams):")
                        
                        for i, link in enumerate(available_links, 1):
                            text = link.get('text', 'N/A')
                            results = link.get('results', {})
                            
                            print(f"\n   📋 {i}. {text}")
                            print("   " + "="*50)
                            
                            # Display exam details
                            exam_details = results.get('examDetails', {})
                            if exam_details:
                                print(f"   📚 Exam: {exam_details.get('nameOfExam', 'N/A')}")
                                print(f"   🎓 Degree: {exam_details.get('degree', 'N/A')}")
                                print(f"   📅 Semester: {exam_details.get('semester', 'N/A')}")
                                print(f"   📆 Academic Year: {exam_details.get('academicYear', 'N/A')}")
                                print(f"   🗓️ Month/Year: {exam_details.get('month', 'N/A')} {exam_details.get('year', 'N/A')}")
                            
                            # Display subject results
                            subjects = results.get('results', [])
                            if subjects:
                                print(f"\n   📊 Subject Results ({len(subjects)} subjects):")
                                print("   " + "-"*70)
                                
                                for j, subject in enumerate(subjects, 1):
                                    course_code = subject.get('Course Code', 'N/A')
                                    course_name = subject.get('Course Name', 'N/A')
                                    grade = subject.get('Grade', 'N/A')
                                    credit = subject.get('Credit', 'N/A')
                                    marks = subject.get('Marks', 'N/A')
                                    
                                    print(f"   {j:2d}. {course_code}: {course_name}")
                                    print(f"       Grade: {grade} | Credit: {credit} | Marks: {marks}")
                            
                            # Display summary
                            summary = results.get('summary', {})
                            if summary:
                                print(f"\n   📈 Summary:")
                                if summary.get('sgpa'):
                                    print(f"       SGPA: {summary.get('sgpa')}")
                                if summary.get('cgpa'):
                                    print(f"       CGPA: {summary.get('cgpa')}")
                                if summary.get('earnedCredit'):
                                    print(f"       Earned Credits: {summary.get('earnedCredit')}")
                            
                            # Handle errors in results
                            if results.get('error'):
                                print(f"   ❌ Error: {results.get('error')}")
                                print(f"   🔗 URL: {results.get('url', 'N/A')}")
                            
                            if i < len(available_links):
                                print()  # Extra spacing between exams
                    
                    if not end_semester_exams and not available_links:
                        print("ℹ️ No end semester examination results found for the specified criteria")
                        print("   This could mean:")
                        print("   • End semester exams haven't been conducted yet")
                        print("   • Results haven't been published")
                        print("   • Results are on a different page/format")
                        
                else:
                    error_data = response.get_json()
                    print(f"❌ Failed to get end semester results: {error_data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error getting end semester results: {e}")

    def get_academic_analysis(self):
        """Get comprehensive academic analysis with semester-wise data"""
        if not self.token:
            print("❌ Please login first")
            return
        
        try:
            print("📊 ACADEMIC ANALYSIS")
            print("-" * 50)
            
            with self.app.test_client() as client:
                response = client.get('/api/academic-analysis', headers={
                    'Authorization': f'Bearer {self.token}'
                })
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Academic analysis retrieved successfully!")
                    
                    analysis_data = data.get('academic_analysis', {})
                    semesters = analysis_data.get('semesters', [])
                    overall_stats = analysis_data.get('overall_stats', {})
                    backlogs_info = analysis_data.get('backlogs_info', {})
                    
                    if semesters:
                        print(f"\n📚 Semester-wise Academic Performance ({len(semesters)} semesters):")
                        print("=" * 80)
                        
                        for semester in semesters:
                            print(f"\n🎓 {semester.get('semester_name', 'Unknown Semester')}")
                            print("-" * 60)
                            
                            # Attendance information
                            attendance = semester.get('attendance', {})
                            if attendance.get('total', 0) > 0:
                                print(f"   📅 Attendance: {attendance.get('present', 0)}/{attendance.get('total', 0)} ({attendance.get('percentage', 0)}%)")
                            
                            # Academic performance
                            print(f"   📈 SGPA: {semester.get('sgpa', 'N/A')}")
                            print(f"   🎯 CGPA: {semester.get('cgpa', 'N/A')}")
                            print(f"   📚 Earned Credits: {semester.get('earned_credit', 'N/A')}")
                            print(f"   🔢 Cumulative Credits: {semester.get('cumulative_credit', 'N/A')}")
                            print(f"   ✅ Result: {semester.get('result', 'N/A')}")
                        
                        # Overall statistics
                        if overall_stats:
                            print(f"\n🏆 OVERALL ACADEMIC SUMMARY")
                            print("=" * 50)
                            if overall_stats.get('overall_cgpa'):
                                print(f"   🎯 Overall CGPA: {overall_stats.get('overall_cgpa')}")
                            if overall_stats.get('overall_cumulative_credit'):
                                print(f"   📚 Total Credits: {overall_stats.get('overall_cumulative_credit')}")
                        
                        # Backlogs information
                        if backlogs_info:
                            print(f"\n📋 BACKLOGS INFORMATION")
                            print("=" * 40)
                            print(f"   📊 Total Backlogs: {backlogs_info.get('total_backlogs', 0)}")
                            print(f"   🔴 Current Backlogs: {backlogs_info.get('current_backlogs', 0)}")
                        
                        # Calculate some statistics
                        if len(semesters) > 0:
                            print(f"\n📊 QUICK STATISTICS")
                            print("=" * 40)
                            
                            # Calculate average SGPA
                            valid_sgpas = [s.get('sgpa', 0) for s in semesters if isinstance(s.get('sgpa'), (int, float)) and s.get('sgpa') > 0]
                            if valid_sgpas:
                                avg_sgpa = sum(valid_sgpas) / len(valid_sgpas)
                                print(f"   📈 Average SGPA: {avg_sgpa:.2f}")
                            
                            # Calculate total attendance percentage
                            total_present = sum(s.get('attendance', {}).get('present', 0) for s in semesters)
                            total_classes = sum(s.get('attendance', {}).get('total', 0) for s in semesters)
                            if total_classes > 0:
                                overall_attendance = (total_present / total_classes) * 100
                                print(f"   📅 Overall Attendance: {overall_attendance:.1f}%")
                            
                            # Show progression
                            latest_cgpa = None
                            for semester in reversed(semesters):
                                if isinstance(semester.get('cgpa'), (int, float)) and semester.get('cgpa') > 0:
                                    latest_cgpa = semester.get('cgpa')
                                    break
                            
                            if latest_cgpa:
                                print(f"   🎯 Latest CGPA: {latest_cgpa}")
                    
                    else:
                        print("ℹ️ No semester data found in academic analysis")
                        print("   This could mean:")
                        print("   • Academic analysis data is not available")
                        print("   • The page structure has changed")
                        print("   • Access permissions may be required")
                
                else:
                    error_data = response.get_json()
                    print(f"❌ Failed to get academic analysis: {error_data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error getting academic analysis: {e}")

    def get_attendance(self):
        """Get attendance information"""
        if not self.token:
            print("❌ Please login first")
            return
            
        print("📅 ATTENDANCE")
        print("-" * 12)
        
        semester = input("🎓 Enter semester (required): ").strip()
        
        if not semester:
            print("❌ Semester is required for attendance")
            return
        
        try:
            with self.app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.token}'}
                url = f'/api/attendance?semester={semester}'
                    
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Attendance retrieved successfully!")
                    
                    # Display basic info
                    print(f"\n👤 Student Info:")
                    print(f"   📋 University Reg No: {data.get('university_reg_no', 'N/A')}")
                    print(f"   🎯 Roll No: {data.get('roll_no', 'N/A')}")
                    print(f"   📛 Name: {data.get('name', 'N/A')}")
                    
                    # Display subject-wise attendance
                    print(f"\n📚 Subject-wise Attendance:")
                    subject_count = 0
                    for key, value in data.items():
                        if isinstance(value, dict) and 'present_hours' in value:
                            subject_count += 1
                            print(f"   📖 {key}:")
                            print(f"      ✅ Present: {value.get('present_hours', 'N/A')} hours")
                            print(f"      📊 Total: {value.get('total_hours', 'N/A')} hours")
                            print(f"      📈 Percentage: {value.get('attendance_percentage', 'N/A')}")
                            print()
                    
                    # Display totals
                    print(f"📊 Overall Attendance:")
                    print(f"   ✅ Total Present Hours: {data.get('total_present_hours', 'N/A')}")
                    print(f"   📊 Total Hours: {data.get('total_hours', 'N/A')}")
                    print(f"   📈 Overall Percentage: {data.get('total_perecentage', 'N/A')}")
                    
                    if subject_count == 0:
                        print("   ℹ️ No subject-specific attendance data found")
                        
                else:
                    error_data = response.get_json()
                    print(f"❌ Failed to get attendance: {error_data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error getting attendance: {e}")

    def get_timetable(self):
        """Get weekly timetable"""
        if not self.token:
            print("❌ Please login first")
            return
            
        print("📅 WEEKLY TIMETABLE")
        print("-" * 18)
        
        try:
            with self.app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = client.get('/api/timetable', headers=headers)
                
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Timetable retrieved successfully!")
                    
                    # Define day order for proper display
                    day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    
                    for day in day_order:
                        if day in data:
                            periods = data[day]
                            print(f"\n📅 {day.upper()}")
                            print("   " + "─" * (len(day) + 2))
                            
                            period_count = 0
                            for period_num in range(1, 8):  # periods 1-7
                                period_key = f"period-{period_num}"
                                if period_key in periods:
                                    period_data = periods[period_key]
                                    name = period_data.get('name', '').strip()
                                    teacher = period_data.get('teacher', '').strip()
                                    
                                    if name and name != 'Free Period':
                                        period_count += 1
                                        if teacher:
                                            # Clean up teacher names (remove extra spaces and HTML)
                                            teacher = teacher.replace('</br>', ', ').replace('<br/>', ', ')
                                            teacher = ' '.join(teacher.split())  # normalize whitespace
                                            print(f"   🕐 Period {period_num}: {name}")
                                            print(f"      👨‍🏫 {teacher}")
                                        else:
                                            print(f"   🕐 Period {period_num}: {name}")
                                    elif name == 'Free Period':
                                        print(f"   🕐 Period {period_num}: 🆓 Free Period")
                            
                            if period_count == 0:
                                print("   ℹ️ No classes scheduled for this day")
                        
                else:
                    error_data = response.get_json()
                    print(f"❌ Failed to get timetable: {error_data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error getting timetable: {e}")

    def logout(self):
        """Handle user logout"""
        if not self.token:
            print("❌ You are not logged in")
            return
            
        print("👋 LOGOUT")
        print("-" * 10)
        
        try:
            with self.app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = client.post('/api/logout', headers=headers)
                
                self.token = None
                self.username = None
                print("✅ Logged out successfully!")
                
        except Exception as e:
            print(f"❌ Error during logout: {e}")
            self.token = None
            self.username = None

    def show_menu(self):
        """Display the main menu"""
        if self.token:
            print("🔐 AUTHENTICATED MENU")
            print("1. Get Profile")
            print("2. Get Exam Results") 
            print("3. Get End Semester Results")
            print("4. Get Academic Analysis")
            print("5. Get Attendance")
            print("6. Get Timetable")
            print("7. Check API Status")
            print("8. Logout")
        else:
            print("🔐 LOGIN REQUIRED")
            print("1. Login to ETLab")
            print("2. Check API Status")
        
        print("0. Exit")
        print()

    def run(self):
        """Main application loop"""
        self.clear_screen()
        
        while True:
            self.print_header()
            self.show_menu()
            
            try:
                choice = input("🎯 Select an option: ").strip()
                print()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    if self.token:
                        self.get_profile()
                    else:
                        self.login()
                elif choice == "2":
                    if self.token:
                        self.get_results()
                    else:
                        self.check_status()
                elif choice == "3" and self.token:
                    self.get_end_semester_results()
                elif choice == "4" and self.token:
                    self.get_academic_analysis()
                elif choice == "5" and self.token:
                    self.get_attendance()
                elif choice == "6" and self.token:
                    self.get_timetable()
                elif choice == "7" and self.token:
                    self.check_status()
                elif choice == "8" and self.token:
                    self.logout()
                else:
                    print("❌ Invalid option. Please try again.")
                
                input("\n⏸️  Press Enter to continue...")
                self.clear_screen()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                input("\n⏸️  Press Enter to continue...")
                self.clear_screen()

if __name__ == "__main__":
    terminal = ETLabTerminalDirect()
    terminal.run()