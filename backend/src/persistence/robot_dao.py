# DAO = data access object
# This file contains the code that executes sql commands on db

from .db_connection import get_connection

#----- CREATE -----

# persistence function to create a robot 
def create_robot_dao(current_room: str):
    sql = """INSERT INTO robot (robot_status, current_room) 
             VALUES (%s, %s)
             RETURNING robot_id, robot_status, current_room
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur: # cursor: required to execute sql statements
            cur.execute(sql, ("off", current_room))
            record = cur.fetchone() # fetches resulting row from room creation at a dict
        conn.commit() # if connection and insertion is successfull, commit changes

    return record # returns row as a dict

#----- READ -----

# persistence function to get all robots
def get_all_robots_dao():
    sql = """SELECT * FROM robot"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql)
            record = cur.fetchall()
    
    return record

# persistence function to get robot by room number
def get_robot_by_id_dao(robot_id: int):
    sql = """SELECT * FROM robot WHERE robot_id = %s"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id,))
            record = cur.fetchone()
    
    return record

# persistence function to get robot by status
def get_robots_by_status_dao(status: str):
    sql = """SELECT * FROM robot WHERE robot_status = %s"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (status,))
            record = cur.fetchall()
    
    return record

# persistence function to get robot by current_room
def get_robots_by_current_room_dao(current_room: str):
    sql = """SELECT * FROM robot WHERE current_room = %s"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (current_room,))
            record = cur.fetchall()
    
    return record

# persistence function to get robot by next_room
def get_robots_by_next_room_dao(next_room: str):
    sql = """SELECT * FROM robot WHERE next_room = %s"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (next_room,))
            record = cur.fetchall()
    
    return record

# persistence function to get the door status
def get_robot_door_dao(robot_id: int):
    sql = """SELECT robot_id, door_status FROM robot WHERE robot_id = %s"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id,))
            record = cur.fetchone()
    
    return record

#----- UPDATE -----

# persistence function to update robot status
def update_robot_status_dao(robot_id: int, robot_new_status: str):
    sql = f"""UPDATE robot
             SET robot_status = %s
             WHERE robot_id = %s
             RETURNING robot_id, robot_status, current_room
          """
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_new_status, robot_id))
            record = cur.fetchone()
        conn.commit()

    return record

# persistence function to update robot current room
def update_robot_current_room_dao(robot_id: int, new_current_room: str):
    sql = f"""UPDATE robot
             SET current_room = %s
             WHERE robot_id = %s
             RETURNING robot_id, robot_status, current_room
          """
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (new_current_room, robot_id))
            record = cur.fetchone()
        conn.commit()

    return record

# persistence function to update robot next room
def update_robot_next_room_dao(robot_id: int, new_next_room: str):
    sql = f"""UPDATE robot
             SET next_room = %s
             WHERE robot_id = %s
             RETURNING robot_id, robot_status, current_room, next_room
          """
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (new_next_room, robot_id))
            record = cur.fetchone()
        conn.commit()

    return record

# persistence function to set current room to null: when robot is in motion
def robot_current_room_null_dao(robot_id: int):
    sql = f"""UPDATE robot
             SET current_room = NULL
             WHERE robot_id = %s
          """
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id,))
        conn.commit()

# persistence function to set next room to null: when robot is turned off
def robot_next_room_null_dao(robot_id: int):
    sql = f"""UPDATE robot
             SET next_room = NULL
             WHERE robot_id = %s
          """
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id,))
        conn.commit()

# persistence function to update the door status
def update_robot_door_dao(robot_id: int, door_status: str):
    sql = f"""UPDATE robot 
            SET door_status = %s 
            WHERE robot_id = %s
            RETURNING robot_id, door_status"""

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (door_status, robot_id))
            record = cur.fetchone()
    
    return record

#----- DELETE -----

# persistence function to delete robot by robot_id
def delete_robot_dao(robot_id: int):
    sql = """DELETE FROM robot WHERE robot_id = %s
             RETURNING robot_id
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (robot_id,))
            deleted_record = cur.fetchone()
        conn.commit()

    return deleted_record
