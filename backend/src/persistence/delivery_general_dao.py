# DAO = data access object
# This file contains the code that executes sql commands on db

# general persistence functions to be used throughout entire system: not just one end user

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .db_connection import get_connection

from typing import Optional

TORONTO = ZoneInfo("America/Toronto")

# persistence function to get all deliveries
def get_all_deliveries_dao():
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute("SELECT * FROM delivery ORDER BY delivery_time DESC")
            deliveries = cur.fetchall() # cursor fetches all rows from query
    return deliveries

# persistence function to get all deliveries by room number
def get_all_deliveries_by_room_dao(room_number: str):

    sql = """SELECT * FROM delivery
                WHERE room_number = %s
                ORDER BY delivery_time DESC"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (room_number,))
            deliveries = cur.fetchall() # cursor fetches all rows from query
    return deliveries

# persistence function to get all deliveries
def get_all_deliveries_by_robot_dao(robot_id: int):

    sql = """SELECT * FROM delivery
                WHERE assigned_robot = %s
                ORDER BY delivery_time DESC"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id,))
            deliveries = cur.fetchall() # cursor fetches all rows from query
    return deliveries

def update_delivery_status_dao(status: str, d_id: int):
    sql = """UPDATE delivery
             SET status = %s
             WHERE delivery_id = %s
             AND status != 'complete'
             RETURNING delivery_id, admin_user_id, status, room_number, created_at, last_updated_at, delivery_time
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (status, d_id))
            delivery = cur.fetchone() 
    return delivery