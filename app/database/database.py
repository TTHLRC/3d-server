import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'railway'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Database connected successfully")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def check_tables_exist():
    """检查必要的表是否存在"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_exists = cursor.fetchone() is not None
        
        cursor.execute("SHOW TABLES LIKE 'user_data'")
        user_data_exists = cursor.fetchone() is not None
        
        return users_exists and user_data_exists
    except Error as e:
        print(f"Error checking tables: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def init_db():
    """初始化数据库表"""
    connection = get_db_connection()
    if not connection:
        return
        
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
                user_id INT NOT NULL,
                cube_data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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