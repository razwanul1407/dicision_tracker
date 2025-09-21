#!/usr/bin/env python3
"""
Template syntax validation script.
Checks if all templates can be parsed without syntax errors.
"""

import os
import sys
import django
from django.conf import settings
from django.template import Engine, Template, TemplateSyntaxError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dicision_tracker.settings')
django.setup()

def test_template_syntax():
    """Test all templates for syntax errors"""
    print("🔍 Testing template syntax...")
    
    template_dir = "/Volumes/SSD/dicision_tracker/templates"
    templates_to_test = [
        "core/project_detail.html",
        "core/project_list.html", 
        "core/project_form.html",
        "core/event_detail.html",
        "core/event_list.html",
        "core/event_form.html", 
        "core/decision_detail.html",
        "core/decision_list.html",
        "core/decision_form.html",
        "core/deliverable_detail.html",
        "core/deliverable_list.html",
        "core/deliverable_form.html",
    ]
    
    errors = []
    successes = []
    
    for template_name in templates_to_test:
        template_path = os.path.join(template_dir, template_name)
        
        if not os.path.exists(template_path):
            errors.append(f"❌ {template_name}: File not found")
            continue
            
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Try to parse the template
            template = Template(template_content)
            successes.append(f"✅ {template_name}: OK")
            
        except TemplateSyntaxError as e:
            errors.append(f"❌ {template_name}: {str(e)}")
        except Exception as e:
            errors.append(f"❌ {template_name}: Unexpected error - {str(e)}")
    
    # Print results
    print(f"\n📊 Template Syntax Test Results:")
    print(f"   ✅ Passed: {len(successes)}")
    print(f"   ❌ Failed: {len(errors)}")
    
    if successes:
        print("\n✅ Successful templates:")
        for success in successes:
            print(f"   {success}")
    
    if errors:
        print("\n❌ Templates with errors:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n🎉 All templates passed syntax validation!")
        return True

def check_extends_usage():
    """Check that templates use proper extends"""
    print("\n🔍 Checking extends usage...")
    
    template_dir = "/Volumes/SSD/dicision_tracker/templates"
    core_templates = []
    
    # Find all core templates
    for root, dirs, files in os.walk(os.path.join(template_dir, "core")):
        for file in files:
            if file.endswith('.html'):
                core_templates.append(os.path.join(root, file))
    
    problematic_templates = []
    fixed_templates = []
    
    for template_path in core_templates:
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            if '{% elif user.is_' in content:
                problematic_templates.append(template_path)
            elif '{% extends "base.html" %}' in content:
                fixed_templates.append(template_path)
                
        except Exception as e:
            print(f"   ⚠️  Could not read {template_path}: {e}")
    
    print(f"\n📊 Extends Usage Results:")
    print(f"   ✅ Fixed templates: {len(fixed_templates)}")
    print(f"   ❌ Still problematic: {len(problematic_templates)}")
    
    if problematic_templates:
        print("\n❌ Templates still using conditional extends:")
        for template in problematic_templates:
            rel_path = os.path.relpath(template, template_dir)
            print(f"   {rel_path}")
        return False
    else:
        print("\n🎉 All core templates use proper extends!")
        return True

def main():
    print("🚀 Django Template Validation Suite")
    print("=" * 50)
    
    syntax_ok = test_template_syntax()
    extends_ok = check_extends_usage()
    
    print("\n" + "=" * 50)
    
    if syntax_ok and extends_ok:
        print("✨ All template validations passed!")
        print("\nThe templates should now work without syntax errors.")
        print("You can test by visiting /core/projects/1/ in your browser.")
        return 0
    else:
        print("⚠️  Some issues were found. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())