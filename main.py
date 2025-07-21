# main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import uuid
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Arun G - Portfolio API",
    description="Backend API for Arun G's Portfolio Website built with FastAPI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic Models
class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=1000)

class ContactResponse(BaseModel):
    success: bool
    message: str
    id: Optional[str] = None

class Project(BaseModel):
    id: str
    title: str
    category: str
    description: str
    tech: List[str]
    github: str
    demo: str
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class ContactForm(BaseModel):
    name: str
    email: str
    message: str

# Contact endpoint
@app.post("/contact")
async def contact(form: ContactForm):
    print("Form received:", form)
    return {"message": "Message received successfully"}

class ProjectCreate(BaseModel):
    title: str
    category: str
    description: str
    tech: List[str]
    github: str
    demo: str
    featured: bool = False

class Skill(BaseModel):
    name: str
    level: int = Field(..., ge=0, le=100)
    category: str

class Experience(BaseModel):
    id: str
    title: str
    company: str
    location: str
    period: str
    description: str
    type: str
    achievements: List[str]

class Service(BaseModel):
    title: str
    description: str
    features: List[str]

class FAQ(BaseModel):
    question: str
    answer: str

class Stats(BaseModel):
    years_experience: str
    projects_completed: str
    technologies: str
    client_satisfaction: str

class PersonalInfo(BaseModel):
    name: str
    title: str
    email: str
    phone: str
    location: str
    github: str
    linkedin: str
    bio: str

# Data Storage (In production, use a database like PostgreSQL)
PROJECTS_DATA = [
    {
        "id": "1",
        "title": "Amazon Clone",
        "category": "E-commerce Platform",
        "description": "Full-featured e-commerce platform with shopping cart, payment integration, and user authentication. Built with modern JavaScript and responsive design principles.",
        "tech": ["JavaScript", "HTML5", "CSS3", "LocalStorage", "Responsive Design"],
        "github": "https://github.com/ArunDev-07",
        "demo": "https://arun-amazon-clone.netlify.app",
        "featured": True,
        "created_at": datetime.now()
    },
    {
        "id": "2",
        "title": "Movie Discovery App",
        "category": "Entertainment Platform",
        "description": "Interactive movie discovery application with TMDB API integration, search functionality, and detailed movie information with trailers.",
        "tech": ["React JS", "TMDB API", "Tailwind CSS", "React Router", "Axios"],
        "github": "https://github.com/ArunDev-07/Movie-App.git",
        "demo": "https://arun-movie-app.netlify.app",
        "featured": True,
        "created_at": datetime.now()
    },
    {
        "id": "3",
        "title": "Weather Forecast App",
        "category": "Weather Service",
        "description": "Real-time weather application with location-based forecasting, 5-day predictions, and interactive weather maps.",
        "tech": ["React JS", "OpenWeather API", "Geolocation API", "Chart.js"],
        "github": "https://github.com/ArunDev-07/Weather-App",
        "demo": "https://arun-weather-app.netlify.app",
        "featured": False,
        "created_at": datetime.now()
    },
    {
        "id": "4",
        "title": "Currency Converter",
        "category": "Financial Tool",
        "description": "Real-time currency conversion application with historical data, multiple currencies, and exchange rate trends.",
        "tech": ["React JS", "Exchange Rate API", "Chart.js", "Material-UI"],
        "github": "https://github.com/ArunDev-07/Currency-Converter",
        "demo": "https://arun-currency-converter.netlify.app",
        "featured": False,
        "created_at": datetime.now()
    },
    {
        "id": "5",
        "title": "CRUD Task Manager",
        "category": "Data Management",
        "description": "Complete task management application with CRUD operations, filtering, sorting, and data persistence.",
        "tech": ["React JS", "Context API", "LocalStorage", "React Hooks"],
        "github": "https://github.com/ArunDev-07/CRUD-App",
        "demo": "https://arun-task-manager.netlify.app",
        "featured": False,
        "created_at": datetime.now()
    }
]

SKILLS_DATA = [
    {"name": "React JS", "level": 90, "category": "Frontend"},
    {"name": "JavaScript", "level": 85, "category": "Frontend"},
    {"name": "HTML", "level": 95, "category": "Frontend"},
    {"name": "CSS", "level": 92, "category": "Frontend"},
    {"name": "TypeScript", "level": 75, "category": "Frontend"},
    {"name": "Tailwind CSS", "level": 88, "category": "Frontend"},
    {"name": "Python", "level": 82, "category": "Backend"},
    {"name": "FastAPI", "level": 78, "category": "Backend"},
    {"name": "MySQL", "level": 80, "category": "Database"},
    {"name": "Git/GitHub", "level": 85, "category": "Tools"}
]

EXPERIENCES_DATA = [
    {
        "id": "1",
        "title": "Full Stack Developer Intern",
        "company": "VDart",
        "location": "Trichy, Tamil Nadu",
        "period": "2024 - Present",
        "description": "Working as a Full Stack Developer, building scalable web applications using React.js and modern web technologies. Collaborating with cross-functional teams to deliver high-quality solutions.",
        "type": "internship",
        "achievements": [
            "Developed responsive web applications using React JS",
            "Implemented RESTful APIs with Python backend",
            "Collaborated with design team for UI/UX improvements",
            "Participated in code reviews and agile development"
        ]
    },
    {
        "id": "2",
        "title": "Web Development Intern",
        "company": "Learnflu",
        "location": "Online",
        "period": "2024",
        "description": "Worked with React JS and API integrations. Assisted in developing cross-platform websites and gained hands-on experience with modern web development practices.",
        "type": "internship",
        "achievements": [
            "Built cross-platform websites using React JS",
            "Integrated third-party APIs for enhanced functionality",
            "Optimized website performance and user experience",
            "Collaborated with remote development team"
        ]
    },
    {
        "id": "3",
        "title": "Generative AI Workshop",
        "company": "Tech Conference",
        "location": "Bangalore",
        "period": "2025",
        "description": "Participated in intensive workshop on Generative AI, learning to create chatbots using cutting-edge AI technologies and machine learning frameworks.",
        "type": "workshop",
        "achievements": [
            "Learned chatbot development using Generative AI",
            "Implemented AI-powered conversation systems",
            "Studied machine learning frameworks",
            "Networked with AI professionals"
        ]
    }
]

SERVICES_DATA = [
    {
        "title": "Frontend Development",
        "description": "Building responsive and interactive user interfaces with React, JavaScript, and modern CSS frameworks.",
        "features": ["React JS Development", "HTML5 & CSS3", "Interactive UI/UX", "Performance Optimization"]
    },
    {
        "title": "Backend Development",
        "description": "Developing robust server-side applications with Python, FastAPI, and database management.",
        "features": ["Python & FastAPI", "RESTful APIs", "Database Design", "Server Configuration"]
    },
    {
        "title": "Full Stack Solutions",
        "description": "End-to-end web application development from concept to deployment.",
        "features": ["Complete Web Apps", "API Integration", "Database Management", "Deployment & Hosting"]
    }
]

FAQ_DATA = [
    {
        "question": "What technologies do you specialize in?",
        "answer": "I specialize in React JS, JavaScript, TypeScript, Python, FastAPI, and modern web technologies. I'm passionate about building responsive, user-friendly applications with clean, maintainable code."
    },
    {
        "question": "How do you approach new projects?",
        "answer": "I start by understanding the requirements thoroughly, then plan the architecture, choose appropriate technologies, and follow agile development practices with regular testing and client feedback."
    },
    {
        "question": "What's your experience with full-stack development?",
        "answer": "I have hands-on experience with both frontend (React, JavaScript) and backend (Python, FastAPI) development, working on complete web applications from database design to user interface."
    },
    {
        "question": "Do you work with teams or independently?",
        "answer": "I'm comfortable working both independently and as part of a team. I've collaborated with cross-functional teams during my internships and have experience with version control and agile methodologies."
    }
]

PERSONAL_INFO = {
    "name": "Arun G",
    "title": "Python Full Stack Developer",
    "email": "arunaakash675@gmail.com",
    "phone": "+91 7305096778",
    "location": "Coimbatore, Tamil Nadu",
    "github": "https://github.com/ArunDev-07",
    "linkedin": "https://www.linkedin.com/in/arun-g-87515a36b",
    "bio": "Passionate Developer with expertise in React.js, JavaScript, and modern web development. Skilled in building responsive, user-friendly, and high-performance web applications. Currently pursuing B.E. in Computer Science and Engineering at Hindusthan College of Engineering and Technology."
}

STATS_DATA = {
    "years_experience": "2+",
    "projects_completed": "15+",
    "technologies": "8+",
    "client_satisfaction": "100%"
}

# Email configuration (use environment variables in production)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": os.getenv("EMAIL_USER", "your-email@gmail.com"),
    "password": os.getenv("EMAIL_PASSWORD", "your-app-password")
}

# Utility Functions
def send_email(contact_data: ContactMessage):
    """Send email notification when contact form is submitted"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["email"]
        msg['To'] = PERSONAL_INFO["email"]
        msg['Subject'] = f"Portfolio Contact: {contact_data.subject}"
        
        body = f"""
        New contact form submission:
        
        Name: {contact_data.name}
        Email: {contact_data.email}
        Subject: {contact_data.subject}
        
        Message:
        {contact_data.message}
        
        ---
        Sent from Portfolio API
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["email"], EMAIL_CONFIG["password"])
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully for contact from {contact_data.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def save_contact_message(contact_data: ContactMessage):
    """Save contact message to file (in production, use database)"""
    try:
        messages_file = Path("contact_messages.json")
        messages = []
        
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages = json.load(f)
        
        message_data = {
            "id": str(uuid.uuid4()),
            "name": contact_data.name,
            "email": contact_data.email,
            "subject": contact_data.subject,
            "message": contact_data.message,
            "timestamp": datetime.now().isoformat()
        }
        
        messages.append(message_data)
        
        with open(messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        return message_data["id"]
    except Exception as e:
        logger.error(f"Failed to save contact message: {str(e)}")
        return None

# API Routes

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Arun G's Portfolio API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Personal Information
@app.get("/api/personal-info", response_model=PersonalInfo, tags=["Personal"])
async def get_personal_info():
    """Get personal information"""
    return PERSONAL_INFO

@app.get("/api/stats", response_model=Stats, tags=["Personal"])
async def get_stats():
    """Get portfolio statistics"""
    return STATS_DATA

# Projects
@app.get("/api/projects", response_model=List[Project], tags=["Projects"])
async def get_projects(featured: Optional[bool] = None):
    """Get all projects or filter by featured status"""
    projects = PROJECTS_DATA
    
    if featured is not None:
        projects = [p for p in projects if p.get("featured") == featured]
    
    return projects

@app.get("/api/projects/{project_id}", response_model=Project, tags=["Projects"])
async def get_project(project_id: str):
    """Get a specific project by ID"""
    project = next((p for p in PROJECTS_DATA if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects", response_model=Project, tags=["Projects"])
async def create_project(project: ProjectCreate):
    """Create a new project (for future updates)"""
    new_project = {
        "id": str(uuid.uuid4()),
        "title": project.title,
        "category": project.category,
        "description": project.description,
        "tech": project.tech,
        "github": project.github,
        "demo": project.demo,
        "featured": project.featured,
        "created_at": datetime.now()
    }
    
    PROJECTS_DATA.append(new_project)
    return new_project

# Skills
@app.get("/api/skills", response_model=List[Skill], tags=["Skills"])
async def get_skills(category: Optional[str] = None):
    """Get skills, optionally filtered by category"""
    skills = SKILLS_DATA
    
    if category:
        skills = [s for s in skills if s["category"].lower() == category.lower()]
    
    return skills

@app.get("/api/skills/categories", tags=["Skills"])
async def get_skill_categories():
    """Get all skill categories"""
    categories = list(set(skill["category"] for skill in SKILLS_DATA))
    return {"categories": categories}

# Experience
@app.get("/api/experiences", response_model=List[Experience], tags=["Experience"])
async def get_experiences(type: Optional[str] = None):
    """Get experiences, optionally filtered by type"""
    experiences = EXPERIENCES_DATA
    
    if type:
        experiences = [e for e in experiences if e["type"].lower() == type.lower()]
    
    return experiences

@app.get("/api/experiences/{experience_id}", response_model=Experience, tags=["Experience"])
async def get_experience(experience_id: str):
    """Get a specific experience by ID"""
    experience = next((e for e in EXPERIENCES_DATA if e["id"] == experience_id), None)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    return experience

# Services
@app.get("/api/services", response_model=List[Service], tags=["Services"])
async def get_services():
    """Get all services"""
    return SERVICES_DATA

# FAQ
@app.get("/api/faq", response_model=List[FAQ], tags=["FAQ"])
async def get_faq():
    """Get frequently asked questions"""
    return FAQ_DATA

# Contact
@app.post("/api/contact", response_model=ContactResponse, tags=["Contact"])
async def submit_contact(contact: ContactMessage, background_tasks: BackgroundTasks):
    """Submit contact form"""
    try:
        # Save message
        message_id = save_contact_message(contact)
        
        # Send email in background
        background_tasks.add_task(send_email, contact)
        
        return ContactResponse(
            success=True,
            message="Thank you for your message! I'll get back to you soon.",
            id=message_id
        )
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process contact form. Please try again."
        )

# Resume
@app.get("/api/resume/download", tags=["Resume"])
async def download_resume():
    """Download resume file"""
    resume_path = Path("resume.pdf")
    
    if not resume_path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    return FileResponse(
        path=resume_path,
        media_type="application/pdf",
        filename="Arun_G_Resume.pdf"
    )

# Analytics (for future use)
@app.get("/api/analytics/views", tags=["Analytics"])
async def get_page_views():
    """Get page view analytics"""
    # In production, integrate with analytics service
    return {
        "total_views": 1234,
        "unique_visitors": 567,
        "popular_projects": [
            {"title": "Amazon Clone", "views": 234},
            {"title": "Movie Discovery App", "views": 189},
            {"title": "Weather Forecast App", "views": 145}
        ]
    }

# Search
@app.get("/api/search", tags=["Search"])
async def search_content(q: str, category: Optional[str] = None):
    """Search through portfolio content"""
    results = []
    
    # Search projects
    for project in PROJECTS_DATA:
        if (q.lower() in project["title"].lower() or 
            q.lower() in project["description"].lower() or
            any(q.lower() in tech.lower() for tech in project["tech"])):
            results.append({
                "type": "project",
                "title": project["title"],
                "description": project["description"],
                "url": f"/api/projects/{project['id']}"
            })
    
    # Search skills
    for skill in SKILLS_DATA:
        if q.lower() in skill["name"].lower():
            results.append({
                "type": "skill",
                "title": skill["name"],
                "description": f"{skill['category']} - {skill['level']}%",
                "url": "/api/skills"
            })
    
    return {"query": q, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
