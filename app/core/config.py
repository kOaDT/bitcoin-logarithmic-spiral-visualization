import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASS: str = os.getenv("DB_PASS", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "1234"))
    DB_NAME: str = os.getenv("DB_NAME", "db_name")
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings() 