import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dal.database import Base
from dal.po.requirement import Requirement  # noqa: F401
from settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 删除所有表
Base.metadata.drop_all(bind=engine)
# 创建所有表
Base.metadata.create_all(bind=engine)
