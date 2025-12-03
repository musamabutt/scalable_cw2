# models/comment.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base, SessionLocal
from .video import Video

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)

    user = relationship("User")
    video = relationship("Video")

    @staticmethod
    def create_comment(video_id, user_id, content):
        if not content.strip():
            return None  # Prevent empty comments
        db = SessionLocal()
        comment = Comment(video_id=video_id, user_id=user_id, content=content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        db.close()
        return comment

    @staticmethod
    def get_comments_for_video(video_id):
        db = SessionLocal()
        comments = db.query(Comment).filter_by(video_id=video_id).all()
        db.close()
        return comments
