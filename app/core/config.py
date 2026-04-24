from os import getenv


DB_USER = getenv("DB_USER", "postgres")
DB_PASSWORD = getenv("DB_PASSWORD", "postgres")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = getenv("DB_PORT", "5432")
DB_NAME = getenv("DB_NAME", "together_redactor")
JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(getenv("JWT_EXPIRE_MINUTES", "60"))

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
