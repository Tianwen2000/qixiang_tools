from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    app_name: str = "琦湘工具集合"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    temp_dir: Path = Field(default=APP_ROOT / "temp", alias="TEMP_DIR")
    max_upload_size_mb: int = Field(default=50, alias="MAX_UPLOAD_SIZE_MB")
    allowed_image_types: list[str] = Field(
        default=["jpg", "jpeg", "png", "webp", "gif", "bmp", "ico", "tif", "tiff"],
        alias="ALLOWED_IMAGE_TYPES",
    )
    allowed_pdf_types: list[str] = Field(default=["pdf"], alias="ALLOWED_PDF_TYPES")
    file_ttl_minutes: int = Field(default=30, alias="FILE_TTL_MINUTES")
    cors_origins: list[str] = ["*"]

    # 登录/AI 模块用的数据库与会话配置（生产请在 .env 覆盖）。
    # 默认指向本地 MySQL；连不上时仅登录功能降级，其它工具不受影响。
    database_url: str = Field(
        default="mysql+pymysql://root:root@127.0.0.1:3306/qixiang_tools?charset=utf8mb4",
        alias="DATABASE_URL",
    )
    # 登录有效期 / Cookie 过期时间（天）——二者一致。
    session_expire_days: int = Field(default=30, alias="SESSION_EXPIRE_DAYS")
    session_cookie_name: str = Field(default="qx_session", alias="SESSION_COOKIE_NAME")
    # 生产 HTTPS 下建议设为 true（仅经 https 发送 Cookie）；本地 http 调试保持 false。
    session_cookie_secure: bool = Field(default=False, alias="SESSION_COOKIE_SECURE")
    # 管理员账号（11 位账号，逗号分隔）。登录后即 root，可看反馈系统。
    # 用 str 接收，避免 pydantic-settings 把纯数字当 JSON 解析；经 admin_accounts 暴露为列表。
    admin_accounts_raw: str = Field(default="", alias="ADMIN_ACCOUNTS")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def admin_accounts(self) -> list[str]:
        return [item.strip() for item in self.admin_accounts_raw.split(",") if item.strip()]

    @field_validator("allowed_image_types", "allowed_pdf_types", mode="before")
    @classmethod
    def parse_csv_values(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return [item.lower() for item in value]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    (settings.temp_dir / "input").mkdir(parents=True, exist_ok=True)
    (settings.temp_dir / "output").mkdir(parents=True, exist_ok=True)
    return settings
