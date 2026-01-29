#!/usr/bin/env python3
"""Quick test for participants_general relationship loading"""

import sys
from pathlib import Path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Import models early
import app.models.participants_general
import app.models.participants
import app.models.project
import app.models.survey

from sqlalchemy.orm import joinedload
from app.core.database import SessionLocal
from app.models.participants_general import ParticipantsGeneral
from app.models.participants import Participants

db = SessionLocal()

try:
    # Test 1: Load without joinedload
    print("\n=== Test 1: Load without joinedload ===")
    pg1 = db.query(ParticipantsGeneral).filter(ParticipantsGeneral.project_id == 1).first()
    if pg1:
        print(f"ParticipantsGeneral ID: {pg1.id}")
        print(f"participants (without joinedload): {pg1.participants}")
        print(f"Length: {len(pg1.participants) if pg1.participants else 0}")
    
    # Test 2: Load with joinedload
    print("\n=== Test 2: Load with joinedload ===")
    pg2 = db.query(ParticipantsGeneral).filter(
        ParticipantsGeneral.project_id == 1
    ).options(
        joinedload(ParticipantsGeneral.participants)
    ).first()
    if pg2:
        print(f"ParticipantsGeneral ID: {pg2.id}")
        print(f"participants (with joinedload): {pg2.participants}")
        print(f"Length: {len(pg2.participants) if pg2.participants else 0}")
        
        if pg2.participants:
            for i, p in enumerate(pg2.participants):
                print(f"  {i+1}. {p.participant_actor} ({p.id})")
    
    # Test 3: Check relationship attribute
    print("\n=== Test 3: Check relationship attribute ===")
    from sqlalchemy import inspect
    mapper = inspect(ParticipantsGeneral)
    print(f"Relationships in ParticipantsGeneral: {[rel.key for rel in mapper.relationships]}")
    
    # Test 4: Direct query
    print("\n=== Test 4: Direct Participants query ===")
    participants = db.query(Participants).filter(Participants.participants_general_id == 1).all()
    print(f"Direct query found {len(participants)} participants")
    for p in participants[:3]:
        print(f"  - {p.participant_actor} ({p.id})")

finally:
    db.close()

print("\n✅ Test completed\n")
