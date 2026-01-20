from persistence.db_connection import get_connection

def main():
    print("Starting backend for Mail Delivery Robot")

    try:
        conn = get_connection()
        print("Success")
    except Exception as e:
        print("Connection error")

#main file can only be directly executed, not as an imported module
if __name__ == "__main__":
    main()