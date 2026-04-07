# DAO = data access object
# This file contains the code that executes sql commands on db

#**** ADMIN ONLY FUNCTUONS *****
# admin can do all CRUD operations regarding deliveries they initially created

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .db_connection import get_connection

from typing import Optional

TORONTO = ZoneInfo("America/Toronto")

#----- CREATE -----
# admin persistence function to create a delivery
def create_delivery_dao(admin_id: int, 
                    recipient_id: int,
                    room_number: str,
                    delivery_time: datetime,
                    sender_name: str, 
                    sender_address: str, 
                    sender_email: str,
                    delivery_status: str,
                    sender_phone: Optional[str]=None,
                    assigned_robot: Optional[int]=None,):

    sql = """INSERT INTO delivery (admin_user_id, 
                                    sender_name, 
                                    sender_address, 
                                    sender_phone, 
                                    sender_email, 
                                    recipient_user_id, 
                                    assigned_robot, 
                                    room_number, 
                                    delivery_time, 
                                    status) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
             RETURNING delivery_id, admin_user_id, status, created_at, last_updated_at, delivery_time
            """
    # to order attributes for delivery table insertion
    attribute_tuple = (admin_id, 
                       sender_name, 
                       sender_address, 
                       sender_phone, 
                       sender_email, 
                       recipient_id, 
                       assigned_robot,
                       room_number, 
                       delivery_time,
                       delivery_status)
    
    with get_connection() as conn:
        with conn.cursor() as cur: # cursor: required to execute sql statements
            cur.execute(sql, attribute_tuple)
            record = cur.fetchone() # fetches resulting row from delivery creation at a dict
        conn.commit() # if connection and insertion is successfull, commit changes

    return record # returns row as a dict

#----- READ -----

# admin persistence function to get deliveries; useful for admin dashboard
def get_deliveries_for_admin_dao(admin_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id,))
            record = cur.fetchall()

    return record

# admin persistence function to get a delivery by ID; admin delivery id filtering
def get_delivery_by_id_for_admin_dao(admin_id: int, delivery_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "AND delivery_id = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, delivery_id))
            record = cur.fetchone() 

    return record 

# admin persistence function to get deliveries by recipient; admin delivery recipient filtering
def get_deliveries_by_recipient_for_admin_dao(admin_id: int, recipient_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "AND recipient_user_id = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, recipient_id))
            record = cur.fetchall()

    return record

# admin persistence method to get deliveries from sender; admin delivery sender filtering
def get_deliveries_by_sender_for_admin_dao(admin_id: int, sender_name: str):
    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "AND sender_name ILIKE %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, sender_name))
            record = cur.fetchall()

    return record

# admin persistence function to get deliveries for a day; admin delivery date filtering
def get_deliveries_by_date_for_admin_dao(admin_id: int, day: datetime):

    # Normalize 'day' to Toronto time
    if day.tzinfo is None:
        day = day.replace(tzinfo=TORONTO)
    else:
        day = day.astimezone(TORONTO)


    start_of_day = datetime(day.year, day.month, day.day) # normalize to midnight (start) of day
    next_day = start_of_day + timedelta(days=1) # get midnight of next day

    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "AND delivery_time >= %s " \
            "AND delivery_time < %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, start_of_day, next_day))
            record = cur.fetchall()

    return record

# admin persistence function to get a deliveries by rooms; admin delivery room filtering
def get_deliveries_by_room_for_admin_dao(admin_id: int, room_number: str):
    sql = "SELECT * FROM delivery WHERE admin_user_id = %s " \
            "AND room_number = %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, room_number))
            record = cur.fetchall()

    return record

# admin persistence function to get deliveries ready to be delivered today
def get_ready_deliveries_dao(admin_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "AND delivery_time :: DATE = CURRENT_DATE " \
            "AND status = %s" \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, "ready"))
            record = cur.fetchall()

    return record

# admin persistence function to get deliveries to be delivered today, but are not "ready"
def get_action_required_deliveries_dao(admin_id: int):
    sql = "SELECT * FROM delivery " \
            "WHERE admin_user_id = %s " \
            "AND delivery_time :: DATE = CURRENT_DATE " \
            "AND status != %s " \
            "AND status != %s " \
            "AND status != %s " \
            "ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id, "ready", "in_progress", "complete"))
            record = cur.fetchall()

    return record

#----- UPADTE -----
# admin persistence method to update room_number, status, or/and delivery_time of a single delivery
def update_delivery_by_admin_dao(admin_id: int,
                                 delivery_id: int, 
                                 room_number: Optional[str] = None,
                                 delivery_time: Optional[datetime] = None,
                                 status: Optional[str] = None
                                ):
    
    set_clauses: list[str] = [] # list of attributes that are being updated
    values: list[object] = [] # list of inputted new values per attribute (in order as set_clauses)
    
    if room_number is not None:
        set_clauses.append("room_number = %s")
        values.append(room_number)

    if delivery_time is not None:
        set_clauses.append("delivery_time = %s")
        values.append(delivery_time)

    if status is not None:
        set_clauses.append("status = %s")
        values.append(status)

    set_clauses.append("last_updated_at = NOW()")

    set_sql = ", ".join(set_clauses) # attributes of SET statement, seperated by commas

    sql = f"""UPDATE delivery
             SET {set_sql}
             WHERE delivery_id = %s AND admin_user_id = %s
             RETURNING delivery_id, admin_user_id, status, room_number, created_at, last_updated_at, delivery_time
          """
    
    values.append(delivery_id)
    values.append(admin_id)

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, tuple(values))
            record = cur.fetchone()
        conn.commit()

    return record

def update_delivery_robot_dao(admin_id: int, delivery_id: int, robot_id: int):
    sql = """UPDATE delivery
             SET assigned_robot = %s, status = %s, last_updated_at = NOW()
             WHERE delivery_id = %s AND admin_user_id = %s
             RETURNING delivery_id, admin_user_id, status, assigned_robot, room_number, created_at, last_updated_at, delivery_time
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id, "ready", delivery_id, admin_id))
            record = cur.fetchone()
        conn.commit()

    return record

#----- DELETE -----
# admin persistence function to delete a delivery with delivery_id; only by admin
def delete_delivery_dao(admin_id: int, delivery_id: int):
    sql = """DELETE FROM delivery WHERE delivery_id = %s AND admin_user_id = %s
             RETURNING delivery_id, admin_user_id, status, created_at, last_updated_at, delivery_time
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (delivery_id, admin_id))
            deleted_record = cur.fetchone()
        conn.commit()

    return deleted_record

