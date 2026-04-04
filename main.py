from telethon import TelegramClient, events
import asyncio
from fastapi import FastAPI
from env import *
from database import *
import models

app = FastAPI()

client = TelegramClient('session_coursereviewerbot', API_ID, API_HASH)

user_states = {}

@app.on_event("startup")
async def startup_event():
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        return f"Database error: {e}"
    
    await client.start(bot_token=BOT_TOKEN)
    asyncio.create_task(client.run_until_disconnected())
    
@app.on_event("shutdown")
async def shutdown_event():
    await client.disconnect()
    
@app.get("/health")
async def ping():
    return {"status": "ok"}

def add_course_review(username, coursename, courseprofessor, coursereview):
    db = SessionLocal()
    try:
        db.add(models.CourseReview(
            studentname = username,
            course_name = coursename,
            course_professor = courseprofessor,
            course_review = coursereview
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        return f"add course review error: {e}"
    finally:
        db.close()
        
def get_course_reviews():
    db = SessionLocal()
    try:
        coursedetails = db.query(models.CourseReview).all()
        
        list_coursedetails = []
        
        for i in range(len(coursedetails)):
            dict_coursedetails = {"course name": coursedetails[i].course_name,
                                "course professor": coursedetails[i].course_professor,
                                "course review": coursedetails[i].course_review}
            list_coursedetails.append(dict_coursedetails)
            
        return list_coursedetails
    except Exception as e:
        return f"cannot extract reviews {e}"
        
@client.on(events.NewMessage(pattern='/start'))
async def starthandler(event):
    await event.respond("""
                        Hi, I can help you with saving reviews about some courses.\n
                        tap /help to see what I can do!""")
    
@client.on(events.NewMessage(pattern='/help'))
async def helphandler(event):
    await event.respond("""
                        /review_add - add review about courses
                        /review_list - see all reviews about courses""")
        
@client.on(events.NewMessage(pattern='/review_add'))
async def review_add_message(event):
    user_id = event.sender_id
    user_states[user_id] = "waiting_for_review_add"
    await event.respond(
        """Send the '!'/course name/course professor name/your review about course to me, and I will save it into the database\n\n
example:\n
!Introduction To Programming/Kisub Kim/I liked it very much because the professor explained the python very well.
        """
    )
    
@client.on(events.NewMessage(pattern='/review_list'))
async def review_list_message(event):
    try:
        list_coursedetails = get_course_reviews()
        output_list = []
        sumdetails = ''
        for index, coursedetail in enumerate(list_coursedetails, start=1):
            eachdetail = f"""
{index}. Course Name: {coursedetail["course name"]}
Course Professor: {coursedetail["course professor"]}
Course Review: {coursedetail["course review"]}
                            """
            sumdetails += eachdetail
        
        await event.respond(f"""
                            Course reviews:
{sumdetails}""")
    except Exception as e:
        return e
    
@client.on(events.NewMessage)
async def necessary_task_handler(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    
    if event.text.startswith("/"):
        return
    elif event.text.startswith("!"):
        if user_id in user_states:
            if user_states[user_id] == "waiting_for_review_add":
                coursereview = event.text.split("/")
                try:
                    add_course_review(sender.username, coursereview[0][1:], coursereview[1], coursereview[2])
                    await event.respond("Successfully added your review")
                except Exception as e:
                    await event.respond(f"Could not save your review: {e}") 