from backend.app.database.connection import get_db_connection


try:
    connection = get_db_connection()

    print("Successfully connected to PostgreSQL!")

    connection.close()

except Exception as e:
    print("Database connection failed:")
    print(e)