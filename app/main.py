from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import mysql.connector
from mysql.connector import Error

from app.database.database import get_db_connection, init_db
from app.api import auth
from app.schemas import schemas

# 初始化数据库
init_db()

app = FastAPI()

# 注册接口
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # 创建新用户
        hashed_password = auth.get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
            (user.username, user.email, hashed_password)
        )
        connection.commit()
        
        # 获取新创建的用户
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        new_user = cursor.fetchone()
        
        return new_user
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 登录接口
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
        user = cursor.fetchone()
        
        if not user or not auth.verify_password(form_data.password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user['username']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 保存数据接口
@app.post("/data", response_model=schemas.UserData)
def create_user_data(
    data: schemas.UserDataCreate,
    current_user: dict = Depends(auth.get_current_user)
):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO user_data (title, content, user_id) VALUES (%s, %s, %s)",
            (data.title, data.content, current_user['id'])
        )
        connection.commit()
        
        # 获取新创建的数据
        cursor.execute("SELECT * FROM user_data WHERE id = LAST_INSERT_ID()")
        new_data = cursor.fetchone()
        
        return new_data
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 获取数据接口
@app.get("/data", response_model=List[schemas.UserData])
def read_user_data(current_user: dict = Depends(auth.get_current_user)):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (current_user['id'],))
        user_data = cursor.fetchall()
        
        return user_data
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close() 