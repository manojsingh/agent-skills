#!/usr/bin/env python3
"""
.NET Application Assessment Tool
Analyzes .NET projects and generates a migration inventory for React + Python refactoring
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class DotNetAssessor:
    MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB — skip files larger than this

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.inventory = {
            "project_type": None,
            "controllers": [],
            "models": [],
            "views": [],
            "services": [],
            "dependencies": [],
            "routes": [],
            "database_contexts": [],
            "authentication": None,
            "third_party_packages": [],
            "recommendations": []
        }
    
    def assess(self) -> Dict:
        """Run complete assessment"""
        print(f"Assessing .NET project at: {self.project_path}")
        
        self._detect_project_type()
        self._scan_controllers()
        self._scan_models()
        self._scan_views()
        self._scan_services()
        self._scan_database_contexts()
        self._scan_dependencies()
        self._detect_authentication()
        self._generate_recommendations()
        
        return self.inventory
    
    def _read_file(self, file_path) -> str:
        """Read a file, returning empty string if it exceeds the size limit or cannot be read."""
        try:
            stat = file_path.stat()
            if stat.st_size > self.MAX_FILE_SIZE_BYTES:
                print(f"  Skipping large file: {file_path} ({stat.st_size} bytes)")
                return ""
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except (OSError, PermissionError) as e:
            print(f"  Skipping unreadable file: {file_path} ({e})")
            return ""

    def _detect_project_type(self):
        """Detect the type of .NET project"""
        csproj_files = list(self.project_path.glob("**/*.csproj"))
        
        if not csproj_files:
            self.inventory["project_type"] = "Unknown"
            return
        
        # Read first csproj to determine type
        content = self._read_file(csproj_files[0])
        
        if 'Microsoft.NET.Sdk.Web' in content:
            if 'Microsoft.AspNetCore.Mvc' in content:
                self.inventory["project_type"] = "ASP.NET MVC"
            elif 'Microsoft.AspNetCore.Components' in content:
                self.inventory["project_type"] = "Blazor"
            else:
                self.inventory["project_type"] = "ASP.NET Web API"
        elif 'Microsoft.NET.Sdk.WindowsDesktop' in content:
            self.inventory["project_type"] = "Windows Forms / WPF"
        else:
            self.inventory["project_type"] = "ASP.NET Core"
    
    def _scan_controllers(self):
        """Scan for controller files"""
        controller_files = list(self.project_path.glob("**/Controllers/**/*.cs"))
        
        for file_path in controller_files:
            content = self._read_file(file_path)
            if not content:
                continue
            
            # Extract controller name
            class_match = re.search(r'class\s+(\w+Controller)', content)
            if not class_match:
                continue
            
            controller_name = class_match.group(1)
            
            # Extract routes
            routes = self._extract_routes(content, controller_name)
            
            self.inventory["controllers"].append({
                "name": controller_name,
                "file": str(file_path.relative_to(self.project_path)),
                "routes": routes,
                "actions": len(routes)
            })
            
            self.inventory["routes"].extend(routes)
    
    def _extract_routes(self, content: str, controller_name: str) -> List[Dict]:
        """Extract route information from controller"""
        routes = []
        
        # Find route attributes
        route_patterns = [
            r'\[Route\("([^"]+)"\)\]',
            r'\[HttpGet\("([^"]+)"\)\]',
            r'\[HttpPost\("([^"]+)"\)\]',
            r'\[HttpPut\("([^"]+)"\)\]',
            r'\[HttpDelete\("([^"]+)"\)\]',
        ]
        
        # Find methods
        method_pattern = r'public\s+(?:async\s+)?(?:Task<)?(\w+)>?\s+(\w+)\s*\('
        methods = re.finditer(method_pattern, content)
        
        for method_match in methods:
            return_type = method_match.group(1)
            method_name = method_match.group(2)
            
            # Determine HTTP method
            http_method = "GET"  # default
            if re.search(rf'\[HttpPost.*?\]\s*public.*?{method_name}', content, re.DOTALL):
                http_method = "POST"
            elif re.search(rf'\[HttpPut.*?\]\s*public.*?{method_name}', content, re.DOTALL):
                http_method = "PUT"
            elif re.search(rf'\[HttpDelete.*?\]\s*public.*?{method_name}', content, re.DOTALL):
                http_method = "DELETE"
            
            routes.append({
                "controller": controller_name,
                "action": method_name,
                "http_method": http_method,
                "return_type": return_type
            })
        
        return routes
    
    def _scan_models(self):
        """Scan for model/entity files"""
        model_files = []
        
        # Common model directories
        for pattern in ["**/Models/**/*.cs", "**/Entities/**/*.cs", "**/Domain/**/*.cs"]:
            model_files.extend(self.project_path.glob(pattern))
        
        for file_path in model_files:
            content = self._read_file(file_path)
            if not content:
                continue
            
            # Extract class name
            class_matches = re.finditer(r'public\s+class\s+(\w+)', content)
            
            for class_match in class_matches:
                model_name = class_match.group(1)
                
                # Extract properties
                properties = re.findall(r'public\s+(\w+(?:<\w+>)?)\s+(\w+)\s*{', content)
                
                self.inventory["models"].append({
                    "name": model_name,
                    "file": str(file_path.relative_to(self.project_path)),
                    "properties": [
                        {"type": prop[0], "name": prop[1]} 
                        for prop in properties
                    ]
                })
    
    def _scan_views(self):
        """Scan for view files (Razor, etc.)"""
        view_files = list(self.project_path.glob("**/Views/**/*.cshtml"))
        
        for file_path in view_files:
            view_name = file_path.stem
            controller = file_path.parent.name
            
            self.inventory["views"].append({
                "name": view_name,
                "controller": controller,
                "file": str(file_path.relative_to(self.project_path))
            })
    
    def _scan_services(self):
        """Scan for service classes"""
        service_files = list(self.project_path.glob("**/Services/**/*.cs"))
        
        for file_path in service_files:
            content = self._read_file(file_path)
            if not content:
                continue
            
            # Extract interface and class names
            interfaces = re.findall(r'interface\s+(I\w+)', content)
            classes = re.findall(r'class\s+(\w+Service)', content)
            
            if classes:
                self.inventory["services"].append({
                    "name": classes[0],
                    "interfaces": interfaces,
                    "file": str(file_path.relative_to(self.project_path))
                })
    
    def _scan_database_contexts(self):
        """Scan for Entity Framework DbContext classes"""
        cs_files = list(self.project_path.glob("**/*.cs"))
        
        for file_path in cs_files:
            content = self._read_file(file_path)
            if not content:
                continue

            if 'DbContext' in content:
                context_match = re.search(r'class\s+(\w+)\s*:\s*DbContext', content)
                if context_match:
                    context_name = context_match.group(1)
                    
                    # Extract DbSet properties
                    dbsets = re.findall(r'DbSet<(\w+)>\s+(\w+)', content)
                    
                    self.inventory["database_contexts"].append({
                        "name": context_name,
                        "file": str(file_path.relative_to(self.project_path)),
                        "entities": [{"type": ds[0], "property": ds[1]} for ds in dbsets]
                    })
    
    def _scan_dependencies(self):
        """Scan NuGet packages from csproj files"""
        csproj_files = list(self.project_path.glob("**/*.csproj"))
        
        for file_path in csproj_files:
            content = self._read_file(file_path)
            if not content:
                continue
            
            # Extract PackageReference entries
            packages = re.findall(
                r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"',
                content
            )
            
            for package_name, version in packages:
                self.inventory["third_party_packages"].append({
                    "name": package_name,
                    "version": version,
                    "python_equivalent": self._suggest_python_equivalent(package_name)
                })
    
    def _suggest_python_equivalent(self, package_name: str) -> str:
        """Suggest Python equivalent for .NET package"""
        equivalents = {
            "Newtonsoft.Json": "json (built-in) or pydantic",
            "EntityFrameworkCore": "SQLAlchemy or Django ORM",
            "Serilog": "loguru or structlog",
            "AutoMapper": "pydantic or dataclasses",
            "FluentValidation": "pydantic validators",
            "MediatR": "python-mediator",
            "Swashbuckle": "FastAPI (automatic) or flask-swagger",
            "IdentityServer4": "python-jose or authlib",
            "Hangfire": "celery or rq",
            "SignalR": "python-socketio or channels",
            "Dapper": "psycopg2 or pymysql",
        }
        
        for dotnet_pkg, python_pkg in equivalents.items():
            if dotnet_pkg.lower() in package_name.lower():
                return python_pkg
        
        return "Research required"
    
    def _detect_authentication(self):
        """Detect authentication mechanism"""
        cs_files = list(self.project_path.glob("**/*.cs"))
        
        for file_path in cs_files:
            content = self._read_file(file_path)
            if not content:
                continue

            if 'AddIdentity' in content or 'IdentityUser' in content:
                self.inventory["authentication"] = "ASP.NET Identity"
                return
            elif 'AddJwtBearer' in content:
                self.inventory["authentication"] = "JWT Bearer"
                return
            elif 'AddCookie' in content:
                self.inventory["authentication"] = "Cookie Authentication"
                return
        
        self.inventory["authentication"] = "Not detected"
    
    def _generate_recommendations(self):
        """Generate migration recommendations"""
        recommendations = []
        
        # Backend framework recommendation
        if len(self.inventory["controllers"]) > 20:
            recommendations.append({
                "category": "Backend Framework",
                "recommendation": "Django REST Framework",
                "reason": "Large API with many endpoints - Django's batteries-included approach will speed development"
            })
        else:
            recommendations.append({
                "category": "Backend Framework",
                "recommendation": "FastAPI",
                "reason": "Modern async framework with automatic API docs and high performance"
            })
        
        # ORM recommendation
        if self.inventory["database_contexts"]:
            recommendations.append({
                "category": "ORM",
                "recommendation": "SQLAlchemy",
                "reason": f"Detected Entity Framework usage - SQLAlchemy provides similar ORM capabilities"
            })
        
        # Frontend state management
        if len(self.inventory["views"]) > 15:
            recommendations.append({
                "category": "State Management",
                "recommendation": "Redux Toolkit or Zustand",
                "reason": "Large application with many views - centralized state management recommended"
            })
        else:
            recommendations.append({
                "category": "State Management",
                "recommendation": "React Context + useReducer or Zustand",
                "reason": "Moderate sized application - lightweight state management sufficient"
            })
        
        # Authentication
        if self.inventory["authentication"] in ["ASP.NET Identity", "JWT Bearer"]:
            recommendations.append({
                "category": "Authentication",
                "recommendation": "JWT with FastAPI or Django JWT",
                "reason": f"Migrate {self.inventory['authentication']} to token-based auth"
            })
        
        self.inventory["recommendations"] = recommendations
    
    def generate_report(self, output_file: str = None):
        """Generate assessment report"""
        report = {
            "summary": {
                "project_type": self.inventory["project_type"],
                "total_controllers": len(self.inventory["controllers"]),
                "total_routes": len(self.inventory["routes"]),
                "total_models": len(self.inventory["models"]),
                "total_views": len(self.inventory["views"]),
                "total_services": len(self.inventory["services"]),
                "authentication": self.inventory["authentication"],
            },
            "details": self.inventory,
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to: {output_file}")
        else:
            print(json.dumps(report, indent=2))
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Assess .NET application for React + Python migration"
    )
    parser.add_argument(
        "project_path",
        help="Path to .NET project directory"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for assessment report (JSON)",
        default="dotnet_assessment.json"
    )
    
    args = parser.parse_args()
    
    assessor = DotNetAssessor(args.project_path)
    assessor.assess()
    assessor.generate_report(args.output)


if __name__ == "__main__":
    main()
