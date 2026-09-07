from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file


class EnvironmentVariablesConstants:

    _mandatory_env_vars = [
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "OPENCODE_API_KEY",
        "OPENCODE_API_URL",
        "BREVO_API_KEY",
        "BREVO_BASE_API_URL",
        "DATABASE_ADMIN_USERNAME",
        "DATABASE_ADMIN_PASSWORD",
        "DATABASE_ADMIN_EMAIL",
        "DEFAULT_TEACHER_PASSWORD",
        "DEFAULT_STUDENT_PASSWORD",
        "ASSESSMENT_QUALIFICATION_CHUNK_SIZE",
        "ASSESSMENT_MAX_QUESTIONS_NUMBER",
        "REVIEW_URL_BASE",
        "EMAIL_DEFAULT_SENDER",
        "DEFAULT_USER_PASSWORD",
        "RECOVERY_URL_BASE",
        "LOGIN_URL_BASE",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "AWS_ENDPOINT_URL",
        "AWS_SQS_QUALIFICATION_QUEUE_URL",
        "AWS_SQS_CLASSIFICATION_QUEUE_URL",
        "OPENCODE_DEFAULT_MODEL",
        "VALKEY_HOST",
        "VALKEY_PORT",
        "VALKEY_PASSWORD",
        "VALKEY_DB",
    ]

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "")
    JWT_EXPIRATION_DELTA_SECONDS = os.getenv(
        "JWT_EXPIRATION_DELTA_SECONDS", "300"
    )  # Default to 5 minutes if not set
    RANDOM_TOKEN_EXPIRATION_DELTA_SECONDS = os.getenv(
        "RANDOM_TOKEN_EXPIRATION_DELTA_SECONDS", "180"
    )  # Default to 3 minutes if not set
    REFRESH_TOKEN_EXPIRATION_DELTA_SECONDS = os.getenv(
        "REFRESH_TOKEN_EXPIRATION_DELTA_SECONDS", "604800"
    )  # Default to 7 days if not set

    DATABASE_URL = os.getenv("DATABASE_URL", "")
    DB_POOL_SIZE = os.getenv("DB_POOL_SIZE", "5")
    DB_MAX_OVERFLOW = os.getenv("DB_MAX_OVERFLOW", "10")
    DB_POOL_TIMEOUT = os.getenv("DB_POOL_TIMEOUT", "30")
    DB_POOL_RECYCLE = os.getenv("DB_POOL_RECYCLE", "3600")

    ADMIN_USERNAME = os.getenv("DATABASE_ADMIN_USERNAME", "")
    ADMIN_PASSWORD = os.getenv("DATABASE_ADMIN_PASSWORD", "")
    ADMIN_EMAIL = os.getenv("DATABASE_ADMIN_EMAIL", "")
    TEACHER_PASSWORD = os.getenv("DEFAULT_TEACHER_PASSWORD", "")
    STUDENT_PASSWORD = os.getenv("DEFAULT_STUDENT_PASSWORD", "")
    DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "")

    EVALUATION_MODE = os.getenv("EVALUATION_MODE", "normal")
    ASSESSMENT_QUALIFICATION_CHUNK_SIZE = os.getenv(
        "ASSESSMENT_QUALIFICATION_CHUNK_SIZE", ""
    )
    ASSESSMENT_MAX_QUESTIONS_NUMBER = os.getenv("ASSESSMENT_MAX_QUESTIONS_NUMBER", "")

    REVIEW_URL_BASE = os.getenv("REVIEW_URL_BASE", "")
    RECOVERY_URL_BASE = os.getenv("RECOVERY_URL_BASE", "")
    LOGIN_URL_BASE = os.getenv("LOGIN_URL_BASE", "")
    EMAIL_DEFAULT_SENDER = os.getenv("EMAIL_DEFAULT_SENDER", "")

    OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "")
    OPENCODE_API_URL = os.getenv("OPENCODE_API_URL", "")
    OPENCODE_DEFAULT_MODEL = os.getenv("OPENCODE_DEFAULT_MODEL", "")

    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
    BREVO_BASE_API_URL = os.getenv("BREVO_BASE_API_URL", "")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "")
    AWS_SQS_QUALIFICATION_QUEUE_URL = os.getenv("AWS_SQS_QUALIFICATION_QUEUE_URL", "")
    AWS_SQS_CLASSIFICATION_QUEUE_URL = os.getenv("AWS_SQS_CLASSIFICATION_QUEUE_URL", "")

    VALKEY_HOST = os.getenv("VALKEY_HOST", "")
    VALKEY_PORT = os.getenv("VALKEY_PORT", "")
    VALKEY_PASSWORD = os.getenv("VALKEY_PASSWORD", "")
    VALKEY_DB = os.getenv("VALKEY_DB", "")

    USER_ACCESS_TRY_LIMIT = os.getenv("USER_ACCESS_TRY_LIMIT", "3")
    USER_ACCESS_LOCK_TIME_SECONDS = os.getenv("USER_ACCESS_LOCK_TIME_SECONDS", "600")
    USER_ACCESS_LOCK_LIMIT = os.getenv("USER_ACCESS_LOCK_LIMIT", "3")
    USER_OTP_EXPIRED_TIME_SECONDS = os.getenv("USER_OTP_EXPIRED_TIME_SECONDS", "120")

    @staticmethod
    def validate_mandatory_env_vars():
        for var in EnvironmentVariablesConstants._mandatory_env_vars:
            if not os.getenv(var):
                raise EnvironmentError(
                    f"Mandatory environment variable '{var}' is not set."
                )
