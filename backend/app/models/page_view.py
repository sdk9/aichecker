from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from app.database import Base


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False, index=True)
    ip_hash = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
