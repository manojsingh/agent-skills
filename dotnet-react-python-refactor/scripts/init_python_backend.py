#!/usr/bin/env python3
"""
Python Backend Initialization Script
Scaffolds a Python backend project with selected framework (FastAPI, Flask, or Django)
"""

import os
import argparse
from pathlib import Path
from typing import Dict


class BackendInitializer:
    def __init__(self, framework: str, db_type: str, project_name: str):
        self.framework = framework.lower()
        self.db_type = db_type.lower()
        self.project_name = project_name
        self.project_path = Path(project_name)
    
    def initialize(self):
        """Initialize the backend project"""
        print(f"Initializing {self.framework.upper()} project: {self.project_name}")
        
        if self.framework == "fastapi":
            self._init_fastapi()
        elif self.framework == "flask":
            self._init_flask()
        elif self.framework == "django":
            self._init_django()
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
        
        self._create_requirements()
        self._create_gitignore()
        self._create_readme()
        self._create_docker_files()
        
        print(f"\n✅ Project initialized successfully!")
        print(f"\nNext steps:")
        print(f"  cd {self.project_name}")
        print(f"  python -m venv venv")
        print(f"  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print(f"  pip install -r requirements.txt")
    
    def _init_fastapi(self):
        """Initialize FastAPI project structure"""
        dirs = [
            "app",
            "app/api",
            "app/api/routes",
            "app/core",
            "app/models",
            "app/schemas",
            "app/services",
            "app/db",
            "tests",
        ]
        
        for dir_path in dirs:
            (self.project_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create main.py
        main_content = '''"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import products, auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(products.router, prefix="/api/products", tags=["products"])

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
'''
        self._write_file("app/main.py", main_content)
        
        # Create config.py
        config_content = f'''"""Application Configuration"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "{self.project_name}"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "{self._get_db_url()}"
    
    # Auth
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
        self._write_file("app/core/config.py", config_content)
        self._write_file("app/core/__init__.py", "")
        
        # Create database.py
        db_content = f'''"""Database Configuration"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        self._write_file("app/db/database.py", db_content)
        self._write_file("app/db/__init__.py", "")
        
        # Create sample model
        model_content = '''"""Data Models"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
'''
        self._write_file("app/models/product.py", model_content)
        self._write_file("app/models/__init__.py", "")
        
        # Create sample schema
        schema_content = '''"""Pydantic Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
'''
        self._write_file("app/schemas/product.py", schema_content)
        self._write_file("app/schemas/__init__.py", "")
        
        # Create sample route
        route_content = '''"""Product Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
'''
        self._write_file("app/api/routes/products.py", route_content)
        
        # Create auth route placeholder
        auth_content = '''"""Authentication Routes"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"message": "Login endpoint - implement authentication"}
'''
        self._write_file("app/api/routes/auth.py", auth_content)
        self._write_file("app/api/routes/__init__.py", "")
        self._write_file("app/api/__init__.py", "")
        self._write_file("app/__init__.py", "")
    
    def _init_flask(self):
        """Initialize Flask project structure"""
        dirs = [
            "app",
            "app/api",
            "app/models",
            "app/services",
            "tests",
        ]
        
        for dir_path in dirs:
            (self.project_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create app.py
        app_content = '''"""Flask Application Factory"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)
    
    from app.api import products_bp, auth_bp
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    @app.route('/')
    def index():
        return {'message': 'Welcome to the API'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    return app
'''
        self._write_file("app/__init__.py", app_content)
        
        # Create config.py
        config_content = f'''"""Flask Configuration"""
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or '{self._get_db_url()}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
'''
        self._write_file("config.py", config_content)
        
        # Create run.py
        run_content = '''"""Application Entry Point"""
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
'''
        self._write_file("run.py", run_content)
    
    def _init_django(self):
        """Initialize Django project structure"""
        print("Note: For Django, use: django-admin startproject {self.project_name}")
        print("Then run: python manage.py startapp api")
        return
    
    def _get_db_url(self) -> str:
        """Get database URL based on db_type"""
        urls = {
            "postgresql": "postgresql://user:password@localhost/dbname",
            "mysql": "mysql://user:password@localhost/dbname",
            "sqlite": "sqlite:///./app.db",
        }
        return urls.get(self.db_type, urls["sqlite"])
    
    def _create_requirements(self):
        """Create requirements.txt"""
        if self.framework == "fastapi":
            requirements = [
                "fastapi[all]==0.109.0",
                "uvicorn[standard]==0.27.0",
                "sqlalchemy==2.0.25",
                "pydantic==2.5.3",
                "pydantic-settings==2.1.0",
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-multipart==0.0.6",
                "alembic==1.13.1",
            ]
            
            if self.db_type == "postgresql":
                requirements.append("psycopg2-binary==2.9.9")
            elif self.db_type == "mysql":
                requirements.append("pymysql==1.1.0")
            
            requirements.extend([
                "pytest==7.4.4",
                "pytest-cov==4.1.0",
                "httpx==0.26.0",
            ])
        
        elif self.framework == "flask":
            requirements = [
                "Flask==3.0.0",
                "Flask-SQLAlchemy==3.1.1",
                "Flask-CORS==4.0.0",
                "Flask-JWT-Extended==4.5.3",
                "Flask-Migrate==4.0.5",
            ]
            
            if self.db_type == "postgresql":
                requirements.append("psycopg2-binary==2.9.9")
            elif self.db_type == "mysql":
                requirements.append("pymysql==1.1.0")
            
            requirements.extend([
                "pytest==7.4.4",
                "pytest-flask==1.3.0",
            ])
        
        else:  # django
            requirements = [
                "Django==5.0",
                "djangorestframework==3.14.0",
                "djangorestframework-simplejwt==5.3.1",
                "django-cors-headers==4.3.1",
                "psycopg2-binary==2.9.9" if self.db_type == "postgresql" else "",
                "pytest==7.4.4",
                "pytest-django==4.7.0",
            ]
        
        content = "\n".join(r for r in requirements if r)
        self._write_file("requirements.txt", content)
    
    def _create_gitignore(self):
        """Create .gitignore"""
        gitignore = '''
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite3

# Environment
.env
.env.local

# Testing
.coverage
htmlcov/
.pytest_cache/

# Logs
*.log
'''
        self._write_file(".gitignore", gitignore)
    
    def _create_readme(self):
        """Create README.md"""
        readme = f'''# {self.project_name}

{self.framework.upper()} backend API

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   DATABASE_URL={self._get_db_url()}
   SECRET_KEY=your-secret-key
   ```

4. Run migrations:
   ```bash
   alembic upgrade head  # For FastAPI/SQLAlchemy
   ```

5. Run the application:
   ```bash
   {"uvicorn app.main:app --reload" if self.framework == "fastapi" else "python run.py"}
   ```

## API Documentation

- Swagger UI: http://localhost:8000/api/docs (FastAPI only)
- ReDoc: http://localhost:8000/api/redoc (FastAPI only)

## Testing

```bash
pytest
```
'''
        self._write_file("README.md", readme)
    
    def _create_docker_files(self):
        """Create Dockerfile and docker-compose.yml"""
        dockerfile = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["{"uvicorn" if self.framework == "fastapi" else "python"}", "{"app.main:app" if self.framework == "fastapi" else "run.py"}", "--host", "0.0.0.0", "--port", "8000"]
'''
        self._write_file("Dockerfile", dockerfile)
        
        docker_compose = f'''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL={self._get_db_url().replace("localhost", "db")}
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: {"postgres:15" if self.db_type == "postgresql" else "mysql:8" if self.db_type == "mysql" else "alpine"}
    environment:
      {"POSTGRES_USER: user" if self.db_type == "postgresql" else "MYSQL_ROOT_PASSWORD: password"}
      {"POSTGRES_PASSWORD: password" if self.db_type == "postgresql" else "MYSQL_DATABASE: dbname"}
      {"POSTGRES_DB: dbname" if self.db_type == "postgresql" else ""}
    ports:
      - "{"5432:5432" if self.db_type == "postgresql" else "3306:3306"}"
    volumes:
      - db_data:/var/lib/{"postgresql/data" if self.db_type == "postgresql" else "mysql"}

volumes:
  db_data:
'''
        self._write_file("docker-compose.yml", docker_compose)
    
    def _write_file(self, path: str, content: str):
        """Write content to file"""
        file_path = self.project_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Initialize Python backend project"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project"
    )
    parser.add_argument(
        "--framework",
        choices=["fastapi", "flask", "django"],
        default="fastapi",
        help="Backend framework (default: fastapi)"
    )
    parser.add_argument(
        "--db-type",
        choices=["postgresql", "mysql", "sqlite"],
        default="postgresql",
        help="Database type (default: postgresql)"
    )
    
    args = parser.parse_args()
    
    initializer = BackendInitializer(
        args.framework,
        args.db_type,
        args.project_name
    )
    initializer.initialize()


if __name__ == "__main__":
    main()
