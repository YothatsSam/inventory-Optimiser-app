import sqlite3
import uuid
import datetime

SQLITE_PATH = "inventory_sqlite.db"

def sql_exec(query: str, params: tuple = ()):
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    return cur, conn

def compute_reorder_point(avg_daily_demand: float, lead_time_days: float, safety_stock: float) -> float:
    return float(avg_daily_demand) * float(lead_time_days) + float(safety_stock)

def compute_reorder_qty(qty_on_hand: float, reorder_point: float) -> float:
    return max(0.0, float(reorder_point) - float(qty_on_hand))

def record_stock_change(item_id: str, change_qty: float, reason: str):
    now = datetime.datetime.utcnow().isoformat()

    cur, conn = sql_exec(
        "SELECT qty_on_hand FROM inventory_items WHERE id = ?",
        (item_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"ok": False, "error": "Item not found"}

    new_qty = float(row["qty_on_hand"]) + float(change_qty)

    cur.execute("UPDATE inventory_items SET qty_on_hand = ?, updated_at = ? WHERE id = ?", (new_qty, now, item_id))
    cur.execute(
        "INSERT INTO stock_movements (id, item_id, change_qty, reason, created_at) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), item_id, float(change_qty), reason, now)
    )
    conn.commit()
    conn.close()
    return {"ok": True, "new_qty": new_qty}
