from database import Base
from sqlalchemy import Column, String, Integer

class CourseReview(Base):
    __tablename__ = "coursereview"
    
    course_id = Column(Integer, autoincrement=True, primary_key=True)
    studentname = Column(String)
    course_name = Column(String)
    course_professor = Column(String)
    course_review = Column(String)