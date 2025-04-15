import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', '3d')
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
    # 如果表已存在，则不需要初始化
    if check_tables_exist():
        print("Database tables already exist")
        return
        
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
                    id INT NOT NULL AUTO_INCREMENT,
                    user_id INT NOT NULL COMMENT '用户id',
                    initial_content VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '初始数据',
                    target_content VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '目标数据',
                    created_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    real_time_content VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '实时数据',
                    PRIMARY KEY (id) USING BTREE,
                    INDEX user_id (user_id ASC) USING BTREE,
                    CONSTRAINT user_data_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT ON UPDATE RESTRICT
                ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic
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