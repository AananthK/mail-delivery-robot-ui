# DAO = data access object
# This file contains the code that executes sql commands on db

#**** RECIPIENT ONLY FUNCTIONS *****
# recipient can only read and update their own deliveries initially created by the admin

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .db_connection import get_connection

TORONTO = ZoneInfo("America/Toronto")

from typing import Optional

#----- READ -----
# recipient persistence functions to get deliveries; useful for recipient dashboard
def get_deliveries_for_recipient_dao(recipient_id: int):
    sql = "SELECT * FROM delivery WHERE recipient_user_id = %s"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id,))
            record = cur.fetchall()

    return record

# recipient persistence function to get a delivery by admin; recipient delivery admin filtering
def get_deliveries_by_admin_for_recipient_dao(recipient_id: int, admin_id: int):
    sql = "SELECT * FROM delivery WHERE admin_user_id = %s " \
            "AND recipient_user_id = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, recipient_id))
            record = cur.fetchall()

    return record

# recipient persistence function to get a delivery by ID; recipient delivery id filtering
def get_delivery_by_id_for_recipient_dao(recipient_id: int, delivery_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE recipient_user_id = %s " \
            "AND delivery_id = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id, delivery_id))
            record = cur.fetchone() 

    return record 

# recipient persistence method to get deliveries from sender; recipient delivery sender filtering
def get_deliveries_by_sender_for_recipient_dao(recipient_id: int, sender_name: str):
    sql = "SELECT * FROM delivery " \
            "WHERE recipient_user_id = %s " \
            "AND sender_name ILIKE %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id, sender_name))
            record = cur.fetchall()

    return record

# recipient persistence function to get deliveries for a day; recipient delivery date filtering
def get_deliveries_by_date_for_recipient_dao(recipient_id: int, day: datetime):

    # Normalize 'day' to Toronto time
    if day.tzinfo is None:
        day = day.replace(tzinfo=TORONTO)
    else:
        day = day.astimezone(TORONTO)

    start_of_day = datetime(day.year, day.month, day.day) # normalize to midnight (start) of day
    next_day = start_of_day + timedelta(days=1) # get midnight of next day

    sql = "SELECT * FROM delivery " \
            "WHERE recipient_user_id = %s " \
            "AND delivery_time >= %s " \
            "AND delivery_time < %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id, start_of_day, next_day))
            record = cur.fetchall()

    return record

# recipient persistence function to get a deliveries by rooms; recipient delivery room filtering
def get_deliveries_by_room_for_recipient_dao(recipient_id: int, room_number: str):
    sql = "SELECT * FROM delivery WHERE recipient_user_id = %s " \
            "AND room_number = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id, room_number))
            record = cur.fetchall()

    return record

# recipient persistence functions to get ready deliveries
def get_ready_deliveries_for_recipient_dao(recipient_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE recipient_user_id = %s " \
            "AND (delivery_time AT TIME ZONE 'America/Toronto')::date = (NOW() AT TIME ZONE 'America/Toronto')::date " \
            "AND status = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id, "ready"))
            record = cur.fetchall()

    return record

# recipient persistence functions to get unloading delivery
def get_unloadling_delivery_for_recipient_dao(recipient_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE recipient_user_id = %s " \
            "AND status = %s " \
            "AND recipient_confirmed = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id, "unloading", True))
            record = cur.fetchone()

    return record

# recipient persistence function get confirmation of recipient presence
def get_recipient_confirmed_status_dao(delivery_id: int, recipient_id: int):
    sql = "SELECT recipient_confirmed FROM delivery WHERE delivery_id = %s AND recipient_user_id = %s "

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (delivery_id, recipient_id))
            record = cur.fetchone()

    return record

# recipient persistence function to get delivery PIN
def get_delivery_pin_dao(recipient_id: int, delivery_id: int):
    sql = "SELECT pin FROM delivery WHERE delivery_id = %s AND recipient_user_id = %s "

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (delivery_id, recipient_id))
            record = cur.fetchone()

    return record

#----- UPADTE -----
# recipient persistence function to update room_number, status, or/and delivery_time of a single delivery
def update_delivery_by_recipient_dao(recipient_id: int,
                                 delivery_id: int, 
                                 room_number: Optional[str] = None,
                                 delivery_time: Optional[datetime] = None
                                ):
    
    set_clauses: list[str] = [] # list of attributes that are being updated
    values: list[object] = [] # list of inputted new values per attribute (in order as set_clauses)
    
    if room_number is not None:
        set_clauses.append("room_number = %s")
        values.append(room_number)

    if delivery_time is not None:
        set_clauses.append("delivery_time = %s")
        values.append(delivery_time)

    set_clauses.append("last_updated_at = NOW()")

    set_sql = ", ".join(set_clauses) # attributes of SET statement, seperated by commas

    sql = f"""UPDATE delivery
             SET {set_sql}
             WHERE delivery_id = %s AND recipient_user_id = %s
             RETURNING delivery_id, admin_user_id, status, room_number, created_at, last_updated_at, delivery_time
          """
    
    values.append(delivery_id)
    values.append(recipient_id)

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, tuple(values))
            record = cur.fetchone()
        conn.commit()

    return record

# recipient persistence function update confirmation of recipient presence
def update_recipient_confirmed_status_dao(delivery_id: int, recipient_id: int, confirmed: bool):
    sql = "UPDATE delivery SET recipient_confirmed = %s " \
    "WHERE delivery_id = %s " \
    "AND recipient_user_id = %s " \
    "RETURNING delivery_id, recipient_confirmed"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (confirmed, delivery_id, recipient_id))
            record = cur.fetchone()

    return record