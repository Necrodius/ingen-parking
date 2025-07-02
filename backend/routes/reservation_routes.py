from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
from models.reservation import ReservationStatus
from models.user import UserRole
from schemas.reservation_schema import reservation_schema, reservations_schema
from services.reservation_service import ReservationService
from datetime import datetime, timezone

reservation_bp = Blueprint("reservation_bp", __name__)

# ---------- CREATE ----------
@reservation_bp.post("/reservations")
@jwt_required()
def create_reservation():
    try:
        data = reservation_schema.load(request.get_json())
        data["user_id"] = int(get_jwt_identity())
        reservation = ReservationService.create(**data)
        return jsonify({"reservation": reservation_schema.dump(reservation)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception:
        return jsonify({"error": "Something went wrong"}), 500

# ---------- READ ----------
@reservation_bp.get("/reservations")
@jwt_required()
def list_reservations():
    claims  = get_jwt()
    user_id = int(get_jwt_identity())

    if claims.get("role") == UserRole.admin.value:
        reservations = ReservationService.list_all()
    else:
        reservations = ReservationService.list_by_user(user_id)

    return jsonify({"reservations": reservations_schema.dump(reservations)}), 200

@reservation_bp.get("/reservations/<int:reservation_id>")
@jwt_required()
def get_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        claims      = get_jwt()
        user_id     = int(get_jwt_identity())

        if claims.get("role") != UserRole.admin.value and reservation.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        return jsonify({"reservation": reservation_schema.dump(reservation)}), 200
    except NoResultFound:
        return jsonify({"error": "Reservation not found"}), 404

# ---------- UPDATE ----------
@reservation_bp.put("/reservations/<int:reservation_id>")
@jwt_required()
def update_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        user_id     = int(get_jwt_identity())
        claims      = get_jwt()

        if claims.get("role") != UserRole.admin.value and reservation.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        data    = reservation_schema.load(request.get_json(), partial=True)
        updated = ReservationService.update(reservation, **data)

        return jsonify({"reservation": reservation_schema.dump(updated)}), 200
    except NoResultFound:
        return jsonify({"error": "Reservation not found"}), 404
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- DELETE ----------
@reservation_bp.delete("/reservations/<int:reservation_id>")
@jwt_required()
def delete_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        user_id     = int(get_jwt_identity())
        claims      = get_jwt()

        if claims.get("role") != UserRole.admin.value and reservation.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        ReservationService.delete(reservation)
        return jsonify({}), 204
    except NoResultFound:
        return jsonify({"error": "Reservation not found"}), 404

# ---------- CANCEL ----------
@reservation_bp.post("/reservations/<int:reservation_id>/cancel")
@jwt_required()
def cancel_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        user_id     = int(get_jwt_identity())
        claims      = get_jwt()

        if claims.get("role") != UserRole.admin.value and reservation.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        cancelled = ReservationService.cancel(reservation)
        return jsonify({"reservation": reservation_schema.dump(cancelled)}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except NoResultFound:
        return jsonify({"error": "Reservation not found"}), 404

# ---------- FINISH ----------
@reservation_bp.post("/reservations/<int:reservation_id>/finish")
@jwt_required()
def finish_reservation(reservation_id):
    """
    Admins can finish any reservation; normal users can finish their own.
    All persistence is handled by ReservationService.finish().
    """
    try:
        res     = ReservationService.get(reservation_id)
        user_id = int(get_jwt_identity())
        claims  = get_jwt()

        # ── ACL check ──────────────────────────────────────────────
        if claims.get("role") != UserRole.admin.value and res.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        # ── Delegate business logic ───────────────────────────────
        finished = ReservationService.finish(res)
        return jsonify({"reservation": reservation_schema.dump(finished)}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except NoResultFound:
        return jsonify({"error": "Reservation not found"}), 404
