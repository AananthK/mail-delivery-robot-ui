# DAO = data access object
# This file contains the code that executes sql commands on db

from .db_connection import get_connection

#----- CREATE -----

# persistence function to create a room 
# most likely will not be needed, unless room detection is automated -- otherwise, rooms are pre-set
def create_room_dao(room_number: str, floor_number: str):
    sql = """INSERT INTO room (room_number, floor_number) 
             VALUES (%s, %s)
             RETURNING room_number, floor_number
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur: # cursor: required to execute sql statements
            cur.execute(sql, (room_number, floor_number))
            record = cur.fetchone() # fetches resulting row from room creation at a dict
        conn.commit() # if connection and insertion is successfull, commit changes

    return record # returns row as a dict

#----- READ -----

# persistence function to get room by room number
def get_room_by_number_dao(room_number: str):
    sql = """SELECT * FROM room WHERE room_number = %s"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (room_number,))
            record = cur.fetchone()
    
    return record

# persistence function to get rooms by floor number
def get_rooms_by_floor_dao(floor_number: str):
    sql = """SELECT * FROM room WHERE floor_number = %s ORDER BY room_number"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (floor_number,))
            records = cur.fetchall()
    
    return records

#----- DELETE -----

# persistence function to delete room by room number and floor number
def delete_room_dao(room_number: str):
    sql = """DELETE FROM room WHERE room_number = %s
             RETURNING room_number, floor_number
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (room_number,))
            deleted_record = cur.fetchone()
        conn.commit()

    return deleted_record
