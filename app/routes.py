"""Web and REST routes for QualityHub."""

from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app import get_database


bp = Blueprint("qualityhub", __name__)
VALID_STATUSES = {"active", "discontinued"}


def serialize_item(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "quantity": row["quantity"],
        "status": row["status"],
    }


def validate_item(payload: dict) -> dict[str, str]:
    errors: dict[str, str] = {}
    name = payload.get("name")
    quantity = payload.get("quantity")
    status = payload.get("status", "active")

    if not isinstance(name, str) or not name.strip():
        errors["name"] = "Name is required."
    elif len(name.strip()) > 120:
        errors["name"] = "Name must be 120 characters or fewer."

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        errors["quantity"] = "Quantity must be an integer."
    elif quantity < 0:
        errors["quantity"] = "Quantity must be zero or greater."

    if status not in VALID_STATUSES:
        errors["status"] = "Status must be active or discontinued."

    return errors


def insert_item(payload: dict) -> dict:
    database = get_database()
    cursor = database.execute(
        "INSERT INTO items (name, quantity, status) VALUES (?, ?, ?)",
        (
            payload["name"].strip(),
            payload["quantity"],
            payload.get("status", "active"),
        ),
    )
    database.commit()
    row = database.execute(
        "SELECT id, name, quantity, status FROM items WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return serialize_item(row)


@bp.get("/health")
def health():
    return jsonify({"service": "qualityhub", "status": "healthy"}), 200


@bp.get("/")
def inventory():
    rows = get_database().execute(
        "SELECT id, name, quantity, status FROM items ORDER BY id DESC"
    ).fetchall()
    return render_template("inventory.html", items=[serialize_item(row) for row in rows])


@bp.post("/items")
def create_item_from_form():
    raw_quantity = request.form.get("quantity", "")
    try:
        quantity: int | str = int(raw_quantity)
    except ValueError:
        quantity = raw_quantity

    payload = {
        "name": request.form.get("name", ""),
        "quantity": quantity,
        "status": request.form.get("status", "active"),
    }
    errors = validate_item(payload)
    if errors:
        for message in errors.values():
            flash(message, "error")
        return redirect(url_for("qualityhub.inventory")), 303

    insert_item(payload)
    flash("Inventory item added.", "success")
    return redirect(url_for("qualityhub.inventory")), 303


@bp.get("/api/items")
def list_items():
    rows = get_database().execute(
        "SELECT id, name, quantity, status FROM items ORDER BY id"
    ).fetchall()
    return jsonify({"items": [serialize_item(row) for row in rows]}), 200


@bp.post("/api/items")
def create_item():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    errors = validate_item(payload)
    if errors:
        return jsonify({"errors": errors}), 422

    return jsonify(insert_item(payload)), 201


@bp.get("/api/items/<int:item_id>")
def get_item(item_id: int):
    row = get_database().execute(
        "SELECT id, name, quantity, status FROM items WHERE id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        return jsonify({"error": "Item not found."}), 404
    return jsonify(serialize_item(row)), 200


@bp.delete("/api/items/<int:item_id>")
def delete_item(item_id: int):
    database = get_database()
    cursor = database.execute("DELETE FROM items WHERE id = ?", (item_id,))
    database.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "Item not found."}), 404
    return "", 204

