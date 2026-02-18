# DAO = data access object
# This file contains the code that executes sql commands on db

from .db_connection import get_connection

from typing import Optional

#----- CREATE -----
# persistence method to create a user account
def create_account_dao(username: str,
                       password_hash: str,
                       first_name: str,
                       last_name: str,
                       user_role: str, 
                       email: str, 
                       phone_number: Optional[str] = None,
                    ):

    sql = """INSERT INTO account (username, 
                                    password_hash, 
                                    first_name, 
                                    last_name, 
                                    user_role, 
                                    email, 
                                    phone_number 
                                    ) 
             VALUES (%s, %s, %s, %s, %s, %s, %s)
             RETURNING user_id, username, first_name, last_name, user_role, email, phone_number
            """
    # to order attributes for delivery table insertion
    attribute_tuple = (username, 
                       password_hash, 
                       first_name, 
                       last_name, 
                       user_role, 
                       email, 
                       phone_number)
    
    with get_connection() as conn:
        with conn.cursor() as cur: # cursor: required to execute sql statements
            cur.execute(sql, attribute_tuple)
            record = cur.fetchone() # fetches resulting row from delivery creation at a dict
        conn.commit() # if connection and insertion is successfull, commit changes

    return record # returns row as a dict

#----- READ -----
# persistence method to get all accounts, except password
def get_all_accounts_dao():

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute("SELECT user_id, username, first_name, last_name, user_role, email, phone_number FROM account")
            accounts = cur.fetchall() # cursor fetches all rows from query
    return accounts

# persistence method to get an account with an id
def get_account_by_id_dao(id: int):

    sql = "SELECT user_id, username, first_name, last_name, user_role, email, phone_number " \
          "FROM account " \
          "WHERE user_id = %s"
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (id,))
            accounts = cur.fetchone()
    return accounts

# persistence method to get user by username
def get_account_by_username_dao(username: str):

    sql = "SELECT user_id, username, password_hash, first_name, last_name, user_role, email, phone_number" \
         " FROM account WHERE username = %s"
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (username,))
            account = cur.fetchone()
    return account

# persistence function to get a user using name 
def search_accounts_by_name_dao(term: str):
    sql = """
        SELECT user_id, username, first_name, last_name, user_role, email, phone_number
        FROM account
        WHERE first_name ILIKE %s OR last_name ILIKE %s
        ORDER BY last_name, first_name
    """
    # ILIKE in SQL is used for case-insensitive pattern matching
    # no need to worry about capitalization in name search

    pattern = f"%{term}%"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pattern, pattern))
            return cur.fetchall()

#----- UPDATE -----
# persistence function to update account contact information
def update_account_contact_info_dao(user_id: int, email: Optional[str] = None, phone_number: Optional[str] = None):
    set_clauses: list[str] = [] # list of attributes that are being updated
    values: list[object] = [] # list of inputted new values per attribute (in order as set_clauses)
    
    if email is not None:
        set_clauses.append("email = %s")
        values.append(email)

    if phone_number is not None:
        set_clauses.append("phone_number = %s")
        values.append(phone_number)

    set_sql = ", ".join(set_clauses) # attributes of SET statement, seperated by commas

    sql = f"""UPDATE account
             SET {set_sql}
             WHERE user_id = %s
             RETURNING user_id, username, email, phone_number
          """
    
    values.append(user_id)

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, tuple(values))
            record = cur.fetchone()
        conn.commit()

    return record

def update_account_password(user_id: int, new_password_hash: str):
    sql = f"""UPDATE account
             SET password_hash = %s
             WHERE user_id = %s
             RETURNING user_id
          """
    
    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (new_password_hash, user_id))
            record = cur.fetchone()
        conn.commit()

    return record

#----- DELETE -----
# persistence function to delete an account
def delete_account(user_id):
    sql = """DELETE FROM account WHERE user_id = %s
             RETURNING user_id, username
          """

    with get_connection() as conn:
        with conn.cursor() as cur: 
            cur.execute(sql, (user_id,))
            deleted_record = cur.fetchone()
        conn.commit()

    return deleted_record