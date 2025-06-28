from typing import List, Optional
from extensions import db
from models.parking_slot import ParkingSlot

class ParkingSlotService:

    # ---------- Create ----------
    @staticmethod
    def create_slot(**slot_dict) -> ParkingSlot:
        slot = ParkingSlot(**slot_dict)
        db.session.add(slot)
        db.session.commit()
        return slot
    
    # ---------- Read ----------
    @staticmethod
    def list_slots() -> List[ParkingSlot]:
        return ParkingSlot.query.all()

    @staticmethod
    def get_slot(slot_id: int) -> Optional[ParkingSlot]:
        return ParkingSlot.query.get(slot_id)

    # ---------- Update ----------
    @staticmethod
    def update_slot(slot: ParkingSlot, **changes) -> ParkingSlot:
        for field, value in changes.items():
            setattr(slot, field, value)
        db.session.commit()
        return slot

    # ---------- Delete ----------
    @staticmethod
    def delete_slot(slot: ParkingSlot) -> None:
        db.session.delete(slot)
        db.session.commit()