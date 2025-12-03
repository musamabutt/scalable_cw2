# models/video.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base, SessionLocal

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    filename = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    likes = Column(Integer, default=0)
    
    user = relationship("User")

    @staticmethod
    def create_video(title, filename, user_id):
        db = SessionLocal()
        video = Video(title=title, filename=filename, user_id=user_id)
        db.add(video)
        db.commit()
        db.refresh(video)
        db.close()
        return video

    @staticmethod
    def get_all_videos():
        db = SessionLocal()
        videos = db.query(Video).all()
        db.close()
        return videos
