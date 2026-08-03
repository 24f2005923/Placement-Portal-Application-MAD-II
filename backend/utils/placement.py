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


def sync_student_placement_status(student, new_application_status):
    """
    Update a student's overall placement_status based on a new application status.

    This helper is called whenever an application's status changes —
    whether triggered by a company, admin, or result publication.

    Rules:
    - 'selected'    → student is 'Placed' (highest priority; never downgraded)
    - 'interview'   → student moves to 'Interview' stage
    - 'shortlisted' → student moves to 'Applied' (unless already in Interview/Placed)
    - anything else → no change to student placement_status

    Args:
        student: The Student model instance whose status should be updated.
        new_application_status: The new application_status string (e.g. 'selected').
    """
    if student is None:
        return  # Safety guard — no student attached to this application

    status = str(new_application_status or '').lower()

    if status == 'selected':
        # Placing a student is the highest priority — always update
        student.placement_status = 'Placed'
    elif status == 'interview':
        # Moving to interview stage (allow override even if already 'Applied')
        student.placement_status = 'Interview'
    elif status == 'shortlisted':
        # Only update if not already at a higher stage
        if student.placement_status not in ('Placed', 'Interview'):
            student.placement_status = 'Applied'
    # 'rejected', 'applied', and other statuses do not affect placement_status
