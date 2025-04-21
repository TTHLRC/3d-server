from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import mysql.connector
from mysql.connector import Error
import json
import os
from dotenv import load_dotenv

from app.database.database import get_db_connection, init_db
from app.api import auth
from app.schemas import schemas
from fastapi.middleware.cors import CORSMiddleware

# 加载环境变量
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://magicubes.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    init_db()
    print("Database initialization completed")

# 注册接口
@app.post("/register")
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
        
        return {"status": "success", "message": "User registered successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 登录接口
@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(login_data: schemas.Login):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 根据用户名或邮箱查询用户
        if login_data.username:
            cursor.execute("SELECT * FROM users WHERE username = %s", (login_data.username,))
        else:
            cursor.execute("SELECT * FROM users WHERE email = %s", (login_data.email,))
            
        user = cursor.fetchone()
        
        if not user or not auth.verify_password(login_data.password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
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
@app.post("/saveCubeData")
def save_cube_data(
    data: schemas.CubeData,
    current_user: dict = Depends(auth.get_current_user)
):
    try:
        # 将数据转换为JSON字符串
        json_data = json.dumps(data.dict())
    except Exception as e:
        print(f"Error serializing data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")

    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 检查用户是否已有数据
        cursor.execute("SELECT id FROM user_data WHERE user_id = %s", (current_user['id'],))
        existing_data = cursor.fetchone()
        
        if existing_data:
            # 更新现有数据
            cursor.execute(
                "UPDATE user_data SET cube_data = %s WHERE user_id = %s",
                (json_data, current_user['id'])
            )
        else:
            # 创建新数据
            cursor.execute(
                "INSERT INTO user_data (user_id, cube_data) VALUES (%s, %s)",
                (current_user['id'], json_data)
            )
        
        connection.commit()
        return {"status": "success", "message": "Cube data saved successfully"}
        
    except Error as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 获取数据接口
@app.get("/getCubeData", response_model=schemas.CubeData)
def get_cube_data(current_user: dict = Depends(auth.get_current_user)):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT cube_data FROM user_data WHERE user_id = %s", (current_user['id'],))
        user_data = cursor.fetchone()
        
        if not user_data or not user_data['cube_data']:
            # 如果用户没有数据，返回空的初始结构
            return schemas.CubeData()
        
        # 解析JSON数据
        cube_data = json.loads(user_data['cube_data'])
        return schemas.CubeData(**cube_data)
        
    except Error as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close() 