# DAO = data access object
# This file contains the code that executes sql commands on db

from datetime import datetime
from .db_connection import get_connection

from typing import Optional

#----- CREATE -----
# persistence method to create a delivery
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
# persistence method to get all deliveries: mainly for internal use
def get_all_deliveries_dao():
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute("SELECT * FROM delivery")
            deliveries = cur.fetchall() # cursor fetches all rows from query
    return deliveries

# persistence method to get a delivery by ID; delivery_id is unique, should return one delivery
def get_delivery_by_id_dao(delivery_id: int):
    sql = "SELECT * FROM delivery WHERE delivery_id = %s"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (delivery_id,)) # function expects a tuple, even for single values, hence: (delivery_id,)
            record = cur.fetchone() 

    return record 

# persistence method to get a deliveries by admin; useful for admin dashboard
def get_delivery_by_admin_dao(admin_id: int):
    sql = "SELECT * FROM delivery WHERE admin_user_id = %s"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (admin_id,))
            record = cur.fetchall()

    return record

# persistence method to get deliveries to recipient; useful for recipient dashboard
def get_delivery_by_recipient_dao(recipient_id: int):
    sql = "SELECT * FROM delivery WHERE recipient_user_id = %s"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (recipient_id,))
            record = cur.fetchall()

    return record

# persistence method to get deliveries from sender; useful for dashboard filtering
def get_delivery_by_sender_dao(sender_name: str):
    sql = "SELECT * FROM delivery WHERE sender_name = %s"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (sender_name,))
            record = cur.fetchall()

    return record

# persistence method to get deliveries by date; useful for dashboard sorting
def get_delivery_by_date_dao(date: datetime):
    sql = "SELECT * FROM delivery WHERE delivery_time = %s ORDER BY delivery_time DESC"

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (date,))
            record = cur.fetchall()

    return record

#----- UPADTE -----
# persistence method to update room_number, status, or/and delivery_time of a single delivery
def update_delivery_dao(delivery_id: int, 
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
             WHERE delivery_id = %s
             RETURNING delivery_id, admin_user_id, status, room_number, created_at, last_updated_at, delivery_time
          """
    
    values.append(delivery_id)

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, tuple(values))
            record = cur.fetchone()
        conn.commit()

    return record

#----- DELETE -----
# persistence method to delete a delivery with delivery_id; only by admin
def delete_delivery_dao(delivery_id):
    sql = """DELETE FROM delivery WHERE delivery_id = %s
             RETURNING delivery_id, admin_user_id, status, created_at, last_updated_at, delivery_time
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (delivery_id,))
            deleted_record = cur.fetchone()
        conn.commit()

    return deleted_record

