from app.database.database import get_db_connection
from mysql.connector import Error

def execute_migration():
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # 检查列是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_schema = DATABASE()
            AND table_name = 'user_data' 
            AND column_name = 'cube_data'
        """)
        
        if cursor.fetchone()[0] == 0:
            # 添加新的 JSON 列
            cursor.execute("""
                ALTER TABLE user_data
                ADD COLUMN cube_data JSON
            """)
            print("Added cube_data column")
        else:
            print("cube_data column already exists")
        
        connection.commit()
        print("Migration completed successfully")
        return True
        
    except Error as e:
        print(f"Error executing migration: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    execute_migration() 