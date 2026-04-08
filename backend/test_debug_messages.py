#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor, Appointment

db = SessionLocal()

print("=== Debug Database ===\n")

# Get user info
user = db.query(User).filter(User.id == 5).first()
if user:
    print(f"User: ID={user.id}, Email={user.email}, Role={user.role}")

    # Get counselor record
    counselor = db.query(Counselor).filter(Counselor.user_id == user.id).first()
    if counselor:
        print(f"Counselor: ID={counselor.id}, User_ID={counselor.user_id}")
    else:
        print("No counselor record found for user_id=5")

# Get appointment
appointment = db.query(Appointment).filter(Appointment.id == 4).first()
if appointment:
    print(f"\nAppointment ID=4:")
    print(f"  user_id: {appointment.user_id}")
    print(f"  counselor_id: {appointment.counselor_id}")
    print(f"  status: {appointment.status}")

    # Check permission
    if counselor:
        print(f"\nPermission check:")
        print(f"  counselor.id ({counselor.id}) == appointment.counselor_id ({appointment.counselor_id}): {counselor.id == appointment.counselor_id}")
else:
    print("Appointment ID=4 not found")

db.close()
