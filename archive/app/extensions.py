"""
Flask 擴展初始化
統一管理所有 Flask 擴展
"""

from flask_cors import CORS
from flask_restx import Api

# 初始化擴展（稍後綁定到 app）
cors = CORS()

# API 文件配置
api = Api(
    version='1.0',
    title='台股 ETF API',
    description='提供台股 ETF 持股資訊、個股價格查詢等功能',
    doc='/docs/',
    prefix='/api/v1'
)
