# DAO = data access object
# This file contains the code that executes sql commands on db

from datetime import datetime
from .db_connection import get_connection

from typing import Optional

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
             RETURNING delivery_id, admin_user_id, status, created_at, last_updated_at, delivery_time;
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

