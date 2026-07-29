import re
from datetime import date

def cgpa_band(cgpa):
    """Classifies CGPA into standard academic performance bands."""
    if cgpa >= 9.0:
        return 'Outstanding'
    elif cgpa >= 8.0:
        return 'First Class with Distinction'
    elif cgpa >= 6.5:
        return 'First Class'
    elif cgpa >= 5.0:
        return 'Second Class'
    else:
        return 'Pass'

def profile_completeness(student):
    """Calculates student profile completion percentage."""
    fields = [
        student.phone,
        student.address,
        student.resume_path,
        student.marks_10th,
        student.marks_12th,
        student.preferred_role
    ]
    filled_fields = sum(1 for f in fields if f is not None and str(f).strip() != '')
    return int((filled_fields / len(fields)) * 100)

def eligibility_verdict(student, drive):
    """Determines eligibility based on CGPA and backlogs heuristics."""
    reasons = []
    eligible = True
    
    eligibility_str = (drive.eligibility or '').lower()
    
    # Heuristic for minimum CGPA requirement (e.g. "8.0 cgpa", "cgpa > 7.5")
    cgpa_matches = re.findall(r'\b([0-9]\.[0-9]+)\b', eligibility_str)
    if cgpa_matches:
        min_cgpa = float(cgpa_matches[0])
        if student.cgpa < min_cgpa:
            eligible = False
            reasons.append(f"Required minimum CGPA is {min_cgpa} (Student has {student.cgpa})")
            
    # Heuristic for backlogs
    if student.backlogs > 0 and ('no backlog' in eligibility_str or '0 backlog' in eligibility_str):
        eligible = False
        reasons.append("Drive requires zero active backlogs")
        
    return {
        'eligible': eligible,
        'reasons': reasons
    }
