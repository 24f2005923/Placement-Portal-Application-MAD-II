import sqlite3, os

db_path = os.path.join('backend', 'database', 'placement.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()



print("=== Applications referencing dummy/test students (student_id 5 or 6) ===")
cur.execute("SELECT * FROM applications WHERE student_id IN (5, 6)")
print(cur.fetchall())

print("\n=== Applications referencing Test Reminder Drive (drive_id=5) ===")
cur.execute("SELECT * FROM applications WHERE drive_id = 5")
print(cur.fetchall())

print("\n=== Placement drives for Test Company (company_id=3) ===")
cur.execute("SELECT * FROM placement_drives WHERE company_id = 3")
print(cur.fetchall())

print("\n=== Interview reminder history for student_ids 5 or 6 ===")
cur.execute("SELECT * FROM interview_reminder_history WHERE student_id IN (5, 6)")
print(cur.fetchall())

conn.close()
print("\nAll done.")
