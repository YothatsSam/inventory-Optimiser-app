def test_password_hashing_roundtrip():
    from passlib.hash import bcrypt
    h = bcrypt.hash("abc123!XYZ")
    assert bcrypt.verify("abc123!XYZ", h)
    assert not bcrypt.verify("wrong", h)

def test_reorder_math_helpers():
    from inventory_app_lib import compute_reorder_point, compute_reorder_qty
    rp = compute_reorder_point(avg_daily_demand=6, lead_time_days=2, safety_stock=5)
    assert rp == 17.0
    rq = compute_reorder_qty(qty_on_hand=10, reorder_point=rp)
    assert rq == 7.0

def test_sql_inventory_item_exists():
    from inventory_app_lib import sql_exec
    cur, conn = sql_exec("SELECT COUNT(*) AS c FROM inventory_items")
    row = cur.fetchone()
    conn.close()
    assert row["c"] >= 1

def test_stock_change_updates_quantity():
    from inventory_app_lib import sql_exec, record_stock_change

    cur, conn = sql_exec("SELECT id, qty_on_hand FROM inventory_items LIMIT 1")
    item_row = cur.fetchone()
    conn.close()

    item_id = item_row["id"]
    before = float(item_row["qty_on_hand"])

    out = record_stock_change(item_id, change_qty=-1, reason="sale")
    assert out["ok"] is True

    cur2, conn2 = sql_exec("SELECT qty_on_hand FROM inventory_items WHERE id = ?", (item_id,))
    after_row = cur2.fetchone()
    conn2.close()

    after = float(after_row["qty_on_hand"])
    assert after == before - 1
