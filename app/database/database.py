import mysql.connector
from mysql.connector import Error, pooling
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'railway'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'pool_name': 'mypool',
    'pool_size': 20,  # 增加连接池大小
    'pool_reset_session': True,
    'connect_timeout': 180,
    'autocommit': True,
    'max_allowed_packet': 67108864,  # 64MB
    'consume_timeout': 180,  # 连接获取超时时间
}

# 创建连接池
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
    print("Connection pool created successfully")
except Error as e:
    print(f"Error creating connection pool: {e}")
    connection_pool = None

@contextmanager
def get_db_connection():
    """使用上下文管理器来确保连接正确关闭"""
    connection = None
    try:
        if connection_pool:
            connection = connection_pool.get_connection()
            if not connection.is_connected():
                connection.reconnect()
            yield connection
        else:
            # 如果连接池不可用，创建新连接
            connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                connect_timeout=DB_CONFIG['connect_timeout']
            )
            yield connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        yield None
    finally:
        if connection:
            try:
                if connection.is_connected():
                    connection.close()
                    print("Database connection closed successfully")
            except Error as e:
                print(f"Error closing connection: {e}")

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
        
        # 删除现有的表（注意顺序，因为有外键约束）
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS user_data")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # 创建用户表
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建用户数据表
        print("Creating user_data table...")
        cursor.execute("""
            CREATE TABLE user_data (
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
        raise e
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_db()