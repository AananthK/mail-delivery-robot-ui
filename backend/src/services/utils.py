
# Helper functions used throughout services

# This method checks if a DB query returns a record
# Only for single-record DAO functions, those that return lists are handled in the API-layer
def db_return(db_query_result):
    if db_query_result is None:
        raise LookupError("Not found in database")
    return db_query_result


