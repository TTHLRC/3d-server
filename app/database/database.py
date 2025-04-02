import mysql.connector
from mysql.connector import Error

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': '3d'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Database connected successfully")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def init_db():
    """初始化数据库表"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建用户数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    user_id INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            connection.commit()
            print("Database tables created successfully")
            
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == "__main__":
    init_db()