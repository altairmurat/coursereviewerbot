from telethon import TelegramClient, events
import asyncio
from fastapi import FastAPI
from env import *
from database import *
import models

app = FastAPI()

client = TelegramClient('session_coursereviewerbot', API_ID, API_HASH)

user_states = {}
#user_states = {  }
review = {
    "professorname": "",
    "coursename": "",
    "review": ""
}

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
                        /review_add - add review about courses\n
/review_list - see all reviews about courses""")
        
@client.on(events.NewMessage(pattern='/review_add'))
async def review_add_message(event):
    user_id = event.sender_id
    user_states[user_id] = "waiting_for_professorname"
    await event.respond(
        """
        Professor Name (whose course you want to review)
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
            if user_states[user_id] == "waiting_for_":
                usermessage = event.text.split("/")
                
    if user_id in user_states:                
        if user_states[user_id] == "waiting_for_professorname":
            user_states[f"{user_id}review"] = {"professorname": event.text,
                                                "coursename": "",
                                                "review": ""}
            user_states[user_id] = "waiting_for_coursename"
            await event.respond(f"Course Name (taught by professor - {event.text})")
        elif user_states[user_id] == "waiting_for_coursename":
            user_states[f"{user_id}review"]["coursename"] = event.text
            user_states[user_id] = "waiting_for_review"
            await event.respond(f"Write review about {event.text} course. Grading; Workloadness; Your final grade; and etc that would help future students to choose courses. Your review is absolutely anonymous. However, it is kindly requested to follow the basic ethics!")
        elif user_states[user_id] == "waiting_for_review":
            user_states[f"{user_id}review"]["review"] = event.text
            user_states[user_id] = ""
            coursereview = user_states[f"{user_id}review"]
            try:
                add_course_review(sender.username, coursereview["professorname"], coursereview["coursename"], coursereview["review"])
                await event.respond("Successfully added your review. Check it here /review_list")
            except Exception as e:
                await event.respond(f"Could not save your review: {e}")
            