#!/usr/bin/env python3
"""
ETLAB API Response Data Analyzer
Utility script to analyze and extract specific information from saved API test results.
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, Any, List

class EtlabDataAnalyzer:
    def __init__(self, test_output_dir: str):
        self.test_dir = test_output_dir
        self.data = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all saved response data"""
        try:
            # Load main response data file
            all_responses_file = os.path.join(self.test_dir, "all_responses_data.json")
            if os.path.exists(all_responses_file):
                with open(all_responses_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"✅ Loaded data from {len(self.data)} endpoints")
            else:
                print("❌ No response data file found")
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
    
    def extract_profile_info(self) -> Dict[str, Any]:
        """Extract and format profile information"""
        if 'Profile' not in self.data:
            return {"error": "No profile data found"}
        
        profile_data = self.data['Profile'].get('data', {})
        
        extracted = {
            "name": profile_data.get('name', 'N/A'),
            "university_reg_no": profile_data.get('university_reg_no', 'N/A'),
            "roll_no": profile_data.get('roll_no', 'N/A'),
            "semester": profile_data.get('semester', 'N/A'),
            "department": profile_data.get('department', 'N/A'),
            "batch": profile_data.get('batch', 'N/A'),
            "phone": profile_data.get('phone', 'N/A'),
            "email": profile_data.get('email', 'N/A')
        }
        
        return extracted
    
    def extract_attendance_summary(self) -> Dict[str, Any]:
        """Extract and analyze attendance data"""
        if 'Attendance' not in self.data:
            return {"error": "No attendance data found"}
        
        attendance_data = self.data['Attendance'].get('data', {})
        
        # Remove student info fields to get just subjects
        excluded_fields = ['university_reg_no', 'roll_no', 'name']
        subjects = {k: v for k, v in attendance_data.items() if k not in excluded_fields}
        
        summary = {
            "student_info": {
                "name": attendance_data.get('name', 'N/A'),
                "reg_no": attendance_data.get('university_reg_no', 'N/A'),
                "roll_no": attendance_data.get('roll_no', 'N/A')
            },
            "subjects": subjects,
            "total_subjects": len(subjects),
            "attendance_analysis": self.analyze_attendance_percentages(subjects)
        }
        
        return summary
    
    def analyze_attendance_percentages(self, subjects: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze attendance percentages"""
        percentages = []
        subject_analysis = {}
        
        for subject, data in subjects.items():
            if isinstance(data, dict) and 'percentage' in data:
                try:
                    percentage = float(data['percentage'].replace('%', ''))
                    percentages.append(percentage)
                    
                    # Determine status
                    if percentage >= 75:
                        status = "Safe"
                    elif percentage >= 65:
                        status = "Warning"
                    else:
                        status = "Critical"
                    
                    subject_analysis[subject] = {
                        "percentage": percentage,
                        "status": status,
                        "present": data.get('present', 'N/A'),
                        "total": data.get('total', 'N/A')
                    }
                except (ValueError, AttributeError):
                    subject_analysis[subject] = {"error": "Could not parse percentage"}
        
        analysis = {
            "subjects_detail": subject_analysis,
            "overall_stats": {}
        }
        
        if percentages:
            analysis["overall_stats"] = {
                "average_attendance": round(sum(percentages) / len(percentages), 2),
                "highest_attendance": max(percentages),
                "lowest_attendance": min(percentages),
                "subjects_above_75": sum(1 for p in percentages if p >= 75),
                "subjects_below_75": sum(1 for p in percentages if p < 75),
                "critical_subjects": sum(1 for p in percentages if p < 65)
            }
        
        return analysis
    
    def extract_timetable_summary(self) -> Dict[str, Any]:
        """Extract and format timetable information"""
        if 'Timetable' not in self.data:
            return {"error": "No timetable data found"}
        
        timetable_data = self.data['Timetable'].get('data', [])
        
        if not isinstance(timetable_data, list):
            return {"error": "Unexpected timetable data format"}
        
        # Analyze timetable structure
        days = {}
        total_classes = len(timetable_data)
        
        for entry in timetable_data:
            if isinstance(entry, dict):
                day = entry.get('day', 'Unknown')
                if day not in days:
                    days[day] = []
                days[day].append({
                    "time": entry.get('time', 'N/A'),
                    "subject": entry.get('subject', 'N/A'),
                    "room": entry.get('room', 'N/A'),
                    "faculty": entry.get('faculty', 'N/A')
                })
        
        summary = {
            "total_classes": total_classes,
            "days_with_classes": len(days),
            "schedule_by_day": days,
            "daily_class_count": {day: len(classes) for day, classes in days.items()}
        }
        
        return summary
    
    def extract_present_absent_summary(self) -> Dict[str, Any]:
        """Extract present and absent records summary"""
        summary = {}
        
        for endpoint in ['Present', 'Absent']:
            if endpoint not in self.data:
                summary[endpoint.lower()] = {"error": f"No {endpoint.lower()} data found"}
                continue
            
            data = self.data[endpoint].get('data', [])
            
            if isinstance(data, list):
                summary[endpoint.lower()] = {
                    "total_records": len(data),
                    "records": data[:5] if len(data) > 5 else data,  # Show first 5 records
                    "note": f"Showing first 5 of {len(data)} records" if len(data) > 5 else "All records shown"
                }
            else:
                summary[endpoint.lower()] = {"error": "Unexpected data format"}
        
        return summary
    
    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of all data"""
        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": self.test_dir,
            "available_endpoints": list(self.data.keys()),
            "profile": self.extract_profile_info(),
            "attendance": self.extract_attendance_summary(),
            "timetable": self.extract_timetable_summary(),
            "records": self.extract_present_absent_summary()
        }
        
        return analysis
    
    def save_analysis(self, filename: str = "comprehensive_analysis.json"):
        """Save comprehensive analysis to file"""
        analysis = self.generate_comprehensive_analysis()
        
        output_path = os.path.join(self.test_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Comprehensive analysis saved to: {output_path}")
        return analysis
    
    def print_summary_report(self):
        """Print a formatted summary report to console"""
        print("\n" + "="*60)
        print(" 📊 ETLAB API DATA ANALYSIS REPORT")
        print("="*60)
        
        # Profile Summary
        profile = self.extract_profile_info()
        if 'error' not in profile:
            print(f"\n👤 STUDENT PROFILE:")
            print(f"   Name: {profile['name']}")
            print(f"   Reg No: {profile['university_reg_no']}")
            print(f"   Roll No: {profile['roll_no']}")
            print(f"   Department: {profile['department']}")
            print(f"   Semester: {profile['semester']}")
        
        # Attendance Summary
        attendance = self.extract_attendance_summary()
        if 'error' not in attendance and 'attendance_analysis' in attendance:
            stats = attendance['attendance_analysis'].get('overall_stats', {})
            print(f"\n📊 ATTENDANCE SUMMARY:")
            print(f"   Total Subjects: {attendance['total_subjects']}")
            if stats:
                print(f"   Average Attendance: {stats.get('average_attendance', 'N/A')}%")
                print(f"   Subjects Above 75%: {stats.get('subjects_above_75', 'N/A')}")
                print(f"   Critical Subjects (<65%): {stats.get('critical_subjects', 'N/A')}")
        
        # Timetable Summary
        timetable = self.extract_timetable_summary()
        if 'error' not in timetable:
            print(f"\n📅 TIMETABLE SUMMARY:")
            print(f"   Total Classes: {timetable['total_classes']}")
            print(f"   Days with Classes: {timetable['days_with_classes']}")
        
        # Records Summary
        records = self.extract_present_absent_summary()
        for record_type in ['present', 'absent']:
            if record_type in records and 'error' not in records[record_type]:
                count = records[record_type]['total_records']
                print(f"   {record_type.title()} Records: {count}")
        
        print("\n" + "="*60)

def main():
    """Main function to run the analyzer"""
    print("🔍 ETLAB API Data Analyzer")
    print("="*40)
    
    # Find available test output directories
    test_dirs = glob.glob("test_output_*")
    
    if not test_dirs:
        print("❌ No test output directories found!")
        print("Run the test_all_endpoints.py script first to generate data.")
        return
    
    print("📁 Available test directories:")
    for i, dir_name in enumerate(test_dirs, 1):
        print(f"   {i}. {dir_name}")
    
    # Get user selection
    try:
        if len(test_dirs) == 1:
            selected_dir = test_dirs[0]
            print(f"Using: {selected_dir}")
        else:
            choice = int(input("\nSelect directory (number): ")) - 1
            selected_dir = test_dirs[choice]
    except (ValueError, IndexError):
        print("❌ Invalid selection!")
        return
    
    # Create analyzer and run analysis
    analyzer = EtlabDataAnalyzer(selected_dir)
    
    if not analyzer.data:
        print("❌ No data found in selected directory!")
        return
    
    # Show options
    print(f"\n🔍 Analyzing data from: {selected_dir}")
    print("Options:")
    print("1. Show summary report")
    print("2. Save comprehensive analysis")
    print("3. Both")
    
    choice = input("Choose option (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        analyzer.print_summary_report()
    
    if choice in ['2', '3']:
        analyzer.save_analysis()
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()