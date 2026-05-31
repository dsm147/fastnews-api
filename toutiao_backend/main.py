import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config.limiter import limiter
from routers import news, users, favorite, history
from utils.exception_handlers import register_exception_handlers
from config.logging_conf import setup_logging
from config.settings import settings

# 启动时配置日志
setup_logging()

app = FastAPI(title="AI 掘金头条 API", version="v1.0.0")

# 应用启动时间
_start_time = time.time()

# ── Rate Limiting ──────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ───────────────────────────────────────────────────
origins_str = settings.cors_origins
cors_origins_list = [o.strip() for o in origins_str.split(",")] if origins_str != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=(origins_str != "*"),
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
register_exception_handlers(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "uptime": time.time() - _start_time,
        "timestamp": time.time()
    }


# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)

logger.info("应用启动完成")
