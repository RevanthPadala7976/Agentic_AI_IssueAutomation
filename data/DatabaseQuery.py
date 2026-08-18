"""
* This is testing script to check for the duplicate records.
* You can directly check this using a Database query.
* QUERY: SELECT number, count(*) FROM issues GROUP BY number HAVING count(*) > 1;
"""

from src.db.models import IssueModel, SessionLocal

db = SessionLocal()
try:
    ids = db.query(IssueModel.number).all()
    unique_id = set()
    for number in ids:
        if number[0] in unique_id:
            print("Duplicate found")
            break
        unique_id.add(number[0])
    print(f"Number of unique issues: {len(unique_id)}")

except Exception as e:
    db.rollback()
    print(f"Something went wrong: {e}")
finally:
    db.close()
