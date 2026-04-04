from models import *
from database import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)


    
def get_course_reviews():
    db = SessionLocal()
    try:
        coursedetails = db.query(CourseReview).all()
        
        list_coursedetails = []
        dict_coursedetails = {
            "course name": "",
            "course professor": "",
            "course review": ""
        }
        
        for i in range(len(coursedetails)):
            dict_coursedetails["course name"] = coursedetails[i].course_name
            dict_coursedetails["course professor"] = coursedetails[i].course_professor
            dict_coursedetails["course review"] = coursedetails[i].course_review
            list_coursedetails.append(dict_coursedetails)
            
        return list_coursedetails
    except Exception as e:
        return f"cannot extract reviews {e}"

list_coursedetails = get_course_reviews()
output_detail = []
for index, coursedetail in enumerate(list_coursedetails, start=1):
    output_detail.append(f"""
                         {index}.
                         course name: {coursedetail['course name']}\n
                         """)
    
print(output_detail)

#print(f"""Course reviews:\n\n             {list_coursedetails}""")