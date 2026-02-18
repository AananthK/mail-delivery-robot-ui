# manual testing of persistence class for account

from src.persistence.account_dao import *
from src.services.security import hash_password

if __name__ == "__main__":
    p = hash_password("admin123")
    # Verify creation of accounts
    admin = create_account_dao(
        username="admin",
        password_hash= p,
        first_name="Test",
        last_name="Admin",
        user_role="admin",
        email="testadmin@torontomu.ca",
        phone_number="4165551234"
    )
    print(admin)

    #rec = create_account_dao("hello", "wewewere343", "bobby", "eric", "user", "hello@gmail.com", "3343440982")
    #print(rec)
    
    # Verify basic SQL queries
    #print(get_all_accounts_dao())

    #print(get_account_by_id_dao(2))
    #print(get_account_by_id_dao(65))

    #print(get_account_login_dao("dummy_admin", "dummy_pword_hash"))

    #print(get_account_by_name_dao("Doe"))

    # Verify update statements
    #print(update_account_contact_info_dao(1, "updated_dummy_email@notreal.ca", "3434343434"))
    #print(update_account_contact_info_dao(2, "jane_doe@notreal.ca"))
    #print(update_account_password(1, "ronaldINHO80"))

    # Verify delete state
    #print(delete_account(4))

    