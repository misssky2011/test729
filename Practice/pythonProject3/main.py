# main.py
import traceback
import pymysql
import uvicorn
from fastapi import FastAPI
from app.routers.user import user
import fun
from app.utils.logger import Log

# 配置数据库连接参数
try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='figo1234',
        database='artest',
        port=3306,
        charset='utf8mb4'
    )
    print("数据库连接成功！")
except pymysql.MySQLError as e:
    print(f"数据库连接错误: {e}")
    traceback.print_exc()

# 创建 FastAPI 应用
app = FastAPI()

# 定义日志
logger = Log('测试模块')


@app.get("/")
async def root():
    logger.info('欢迎来到方总的数据工厂~')
    return {"message": "Hello World"}

fun.include_router(user.router, prefix='/api/user', tags=["用户模块"])

# 包含子路由，确保在函数内部执行时不会引起循环导入
fun.include_router(prefixtags="api/v1")

if __name__ == '__main__':
    uvicorn.run(app="main:app", host="127.0.0.1", port=8080, reload=True)
