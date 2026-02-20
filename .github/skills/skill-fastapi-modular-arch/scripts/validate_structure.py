#!/usr/bin/env python3
"""
validate_structure.py - Validate FastAPI modular architecture structure
"""

import sys
from pathlib import Path
from typing import List, Tuple

REQUIRED_MODULE_FILES = ["__init__.py", "routes.py", "schemas.py", "crud.py"]
REQUIRED_ROOT_FILES = ["main.py", "db.py", "security.py"]

class ArchitectureValidator:
    def __init__(self, app_dir: str = "app"):
        self.app_dir = Path(app_dir)
        self.errors = []
        self.warnings = []
    
    def validate(self) -> int:
        """Run all validations"""
        print(f"🔍 Validating FastAPI architecture in {self.app_dir}")
        print("=" * 60)
        
        self.check_root_structure()
        self.check_modules()
        self.check_imports()
        
        return self.report()
    
    def check_root_structure(self):
        """Check essential root files"""
        print("\n📁 Root structure check:")
        
        for filename in REQUIRED_ROOT_FILES:
            filepath = self.app_dir / filename
            if filepath.exists():
                print(f"   ✅ {filename}")
            else:
                self.errors.append(f"Missing {filename}")
                print(f"   ❌ {filename} (MISSING)")
    
    def check_modules(self):
        """Check module structure"""
        print("\n📦 Module structure check:")
        
        modules = [d for d in self.app_dir.iterdir() 
                  if d.is_dir() and not d.name.startswith("_")]
        
        if not modules:
            self.warnings.append("No modules found")
            print("   ⓘ No modules found")
            return
        
        print(f"   Found {len(modules)} module(s)")
        
        for module in sorted(modules):
            self._check_module(module)
    
    def _check_module(self, module_path: Path):
        """Check individual module structure"""
        print(f"\n   📂 {module_path.name}:")
        
        for filename in REQUIRED_MODULE_FILES:
            filepath = module_path / filename
            if filepath.exists():
                print(f"      ✅ {filename}")
            else:
                self.warnings.append(f"{module_path.name}/{filename} missing")
                print(f"      ⚠️  {filename}")
    
    def check_imports(self):
        """Check import patterns"""
        print("\n🔗 Import pattern check:")
        
        routes_files = list(self.app_dir.glob("*/routes.py"))
        
        if not routes_files:
            self.warnings.append("No routes.py found")
            return
        
        print(f"   Checking {len(routes_files)} routes file(s)...")
        
        for routes_file in routes_files:
            self._check_route_imports(routes_file)
    
    def _check_route_imports(self, routes_file: Path):
        """Validate imports in routes file"""
        try:
            content = routes_file.read_text()
            module_name = routes_file.parent.name
            
            # Check for APIRouter
            if "APIRouter" not in content:
                self.warnings.append(f"{module_name}/routes.py: APIRouter not imported")
            elif "router =" not in content:
                self.warnings.append(f"{module_name}/routes.py: router not defined")
            else:
                print(f"      ✅ {module_name}/routes.py: Proper router setup")
            
            # Check for schema imports
            if "from . import schemas" not in content and "from . schemas import" not in content:
                self.warnings.append(f"{module_name}/routes.py: schemas not imported")
            
            # Check for CRUD imports
            if "from . import crud" not in content and "from . crud import" not in content:
                self.warnings.append(f"{module_name}/routes.py: crud not imported")
        
        except Exception as e:
            self.errors.append(f"Error reading {routes_file}: {e}")
    
    def report(self) -> int:
        """Print validation report"""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        
        if not self.errors and not self.warnings:
            print("✅ Architecture is valid!")
            return 0
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("=" * 60)
        return 1 if self.errors else 0


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Validate FastAPI modular architecture"
    )
    parser.add_argument(
        "--app-dir",
        default="app",
        help="App directory to validate (default: app)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (not just errors)"
    )
    
    args = parser.parse_args()
    
    validator = ArchitectureValidator(args.app_dir)
    exit_code = validator.validate()
    
    if args.strict and validator.warnings:
        exit_code = 1
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
