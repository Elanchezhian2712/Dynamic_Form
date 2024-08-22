from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from schemas import FormField, FormData

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Set up Jinja2Templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test")
def test_endpoint():
    return {"message": "This is a test endpoint"}

# Endpoint to render the form builder HTML
@app.get("/", response_class=HTMLResponse)
def get_form_builder(request: Request):
    return templates.TemplateResponse("form_builder.html", {"request": request})

# Endpoint to retrieve submitted form data
@app.get("/submissions")
def get_submissions(db: Session = Depends(get_db)):
    submissions = db.query(models.FormSubmission).all()
    return [{"id": submission.id, "form_id": submission.form_structure_id, "data": submission.submitted_data} for submission in submissions]

# Endpoint to delete a specific submission by ID
@app.delete("/submissions/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = db.query(models.FormSubmission).filter(models.FormSubmission.id == submission_id).first()
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    db.delete(submission)
    db.commit()
    return {"message": f"Submission with ID {submission_id} deleted"}

# Endpoint to delete all submitted data
@app.delete("/submissions")
def delete_submissions(db: Session = Depends(get_db)):
    db.query(models.FormSubmission).delete()
    db.commit()
    return {"message": "All submissions deleted"}

# Endpoint to handle form submission
@app.post("/submit-form/")
async def submit_form(fields: FormData, db: Session = Depends(get_db)):
    # Ensure the form name is provided
    if not fields.form_name:
        raise HTTPException(status_code=400, detail="Form name is required")

    # Save the form structure
    form_structure = models.FormStructure(
        form_name=fields.form_name,
        fields=[{"related_name": field.related_name, "value": field.value} for field in fields.fields]
    )
    db.add(form_structure)
    db.commit()
    db.refresh(form_structure)

    # Now save the submitted data
    submitted_data = {field.related_name: field.value for field in fields.fields}
    form_submission = models.FormSubmission(
        form_structure_id=form_structure.id,
        submitted_data=submitted_data
    )

    # Add the new submission to the database
    db.add(form_submission)
    db.commit()
    db.refresh(form_submission)

    return {"status": "Form submitted", "form_id": form_structure.id, "data": submitted_data}