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

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

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
