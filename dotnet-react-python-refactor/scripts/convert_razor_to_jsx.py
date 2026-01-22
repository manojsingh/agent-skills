#!/usr/bin/env python3
"""
Razor to JSX Converter
Assists in converting ASP.NET Razor views to React JSX components
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class RazorToJSXConverter:
    """Converts Razor syntax to JSX"""
    
    def __init__(self, input_path: str, output_dir: str = './converted'):
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def convert_file(self, file_path: Path) -> str:
        """Convert a single Razor file to JSX"""
        print(f"Converting: {file_path.name}")
        
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Extract component name from filename
        component_name = self._get_component_name(file_path)
        
        # Convert Razor to JSX
        jsx_content = self._convert_razor_to_jsx(content)
        
        # Extract props from Razor @model or parameters
        props = self._extract_props(content)
        
        # Generate React component
        component = self._generate_react_component(component_name, jsx_content, props)
        
        return component
    
    def convert_directory(self):
        """Convert all Razor views in a directory"""
        razor_files = list(self.input_path.rglob('*.cshtml'))
        
        if not razor_files:
            print(f"No .cshtml files found in {self.input_path}")
            return
        
        print(f"Found {len(razor_files)} Razor files to convert\n")
        
        for razor_file in razor_files:
            try:
                component = self.convert_file(razor_file)
                
                # Generate output filename
                relative_path = razor_file.relative_to(self.input_path)
                output_file = self.output_dir / relative_path.with_suffix('.jsx')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write component
                output_file.write_text(component, encoding='utf-8')
                print(f"  ✓ Saved to: {output_file}\n")
                
            except Exception as e:
                print(f"  ✗ Error converting {razor_file.name}: {e}\n")
        
        # Generate conversion report
        self._generate_report(razor_files)
    
    def _get_component_name(self, file_path: Path) -> str:
        """Generate React component name from file path"""
        name = file_path.stem
        # Convert to PascalCase
        name = ''.join(word.capitalize() for word in re.split(r'[_\-\s]', name))
        return name
    
    def _convert_razor_to_jsx(self, content: str) -> str:
        """Convert Razor syntax to JSX"""
        jsx = content
        
        # Remove @page directive
        jsx = re.sub(r'@page\s+"[^"]*"', '', jsx)
        
        # Remove @model directive
        jsx = re.sub(r'@model\s+[\w\.]+', '', jsx)
        
        # Remove @using directives
        jsx = re.sub(r'@using\s+[\w\.]+', '', jsx)
        
        # Remove @inject directives
        jsx = re.sub(r'@inject\s+[\w\.]+\s+\w+', '', jsx)
        
        # Convert @section to comments (need manual handling)
        jsx = re.sub(r'@section\s+(\w+)\s*{', r'/* TODO: Handle section \1 */', jsx)
        
        # Convert Razor comments @* *@ to JSX comments
        jsx = re.sub(r'@\*(.+?)\*@', r'{/* \1 */}', jsx, flags=re.DOTALL)
        
        # Convert @if statements
        jsx = self._convert_conditionals(jsx)
        
        # Convert @foreach and @for loops
        jsx = self._convert_loops(jsx)
        
        # Convert @{} code blocks to comments (require manual conversion)
        jsx = re.sub(r'@{([^}]+)}', self._convert_code_block, jsx)
        
        # Convert Razor expressions @variable to {variable}
        jsx = re.sub(r'@(\w+)(?![{(])', r'{\1}', jsx)
        
        # Convert @Model.Property to {props.property}
        jsx = re.sub(r'@Model\.(\w+)', r'{props.\1}', jsx)
        
        # Convert HTML helpers to JSX equivalents
        jsx = self._convert_html_helpers(jsx)
        
        # Convert tag helpers to JSX
        jsx = self._convert_tag_helpers(jsx)
        
        # Fix attribute names (class -> className, for -> htmlFor)
        jsx = self._fix_jsx_attributes(jsx)
        
        # Clean up whitespace
        jsx = self._clean_whitespace(jsx)
        
        return jsx
    
    def _convert_conditionals(self, content: str) -> str:
        """Convert @if/@else to JSX conditional rendering"""
        # Simple @if without else
        pattern = r'@if\s*\(([^)]+)\)\s*{([^}]+)}'
        
        def replace_if(match):
            condition = match.group(1).strip()
            body = match.group(2).strip()
            # Convert C# operators to JavaScript
            condition = condition.replace('&&', '&&').replace('||', '||')
            condition = condition.replace('==', '===').replace('!=', '!==')
            return f'{{({condition}) && (\n  {body}\n)}}'
        
        content = re.sub(pattern, replace_if, content, flags=re.DOTALL)
        
        # @if...@else
        if_else_pattern = r'@if\s*\(([^)]+)\)\s*{([^}]+)}\s*@?else\s*{([^}]+)}'
        
        def replace_if_else(match):
            condition = match.group(1).strip()
            if_body = match.group(2).strip()
            else_body = match.group(3).strip()
            condition = condition.replace('==', '===').replace('!=', '!==')
            return f'{{({condition}) ? (\n  {if_body}\n) : (\n  {else_body}\n)}}'
        
        content = re.sub(if_else_pattern, replace_if_else, content, flags=re.DOTALL)
        
        return content
    
    def _convert_loops(self, content: str) -> str:
        """Convert @foreach and @for to JSX map/array methods"""
        # @foreach loops
        foreach_pattern = r'@foreach\s*\((?:var\s+)?(\w+)\s+in\s+([^)]+)\)\s*{([^}]+)}'
        
        def replace_foreach(match):
            item_var = match.group(1)
            collection = match.group(2).strip()
            body = match.group(3).strip()
            
            # Replace item variable references with parameter
            body_with_refs = re.sub(rf'\b{item_var}\b', item_var, body)
            
            return f'{{({collection} || []).map(({item_var}, index) => (\n  <div key={{index}}>\n    {body_with_refs}\n  </div>\n))}}'
        
        content = re.sub(foreach_pattern, replace_foreach, content, flags=re.DOTALL)
        
        # @for loops (convert to comment - requires manual conversion)
        for_pattern = r'@for\s*\([^)]+\)\s*{[^}]+}'
        content = re.sub(for_pattern, '/* TODO: Convert @for loop to JSX */', content, flags=re.DOTALL)
        
        return content
    
    def _convert_code_block(self, match) -> str:
        """Convert @{} code blocks"""
        code = match.group(1).strip()
        # Convert simple variable declarations
        if 'var ' in code or 'string ' in code or 'int ' in code:
            # Extract variable assignments
            assignments = re.findall(r'(?:var|string|int)\s+(\w+)\s*=\s*([^;]+);', code)
            if assignments:
                converted = []
                for var_name, value in assignments:
                    converted.append(f'const {var_name} = {value};')
                return '{\n  ' + '\n  '.join(converted) + '\n}'
        
        # For complex code blocks, add TODO comment
        return f'{{/* TODO: Convert code block:\n{code}\n*/}}'
    
    def _convert_html_helpers(self, content: str) -> str:
        """Convert ASP.NET HTML helpers to JSX equivalents"""
        # @Html.ActionLink
        content = re.sub(
            r'@Html\.ActionLink\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)',
            r'<a href="/\3/\2">\1</a>',
            content
        )
        
        # @Html.BeginForm -> <form>
        content = re.sub(r'@using\s*\(Html\.BeginForm\([^)]*\)\)\s*{', '<form>', content)
        
        # @Html.LabelFor
        content = re.sub(
            r'@Html\.LabelFor\(m\s*=>\s*m\.(\w+)\)',
            r'<label htmlFor="\1">\1</label>',
            content
        )
        
        # @Html.TextBoxFor
        content = re.sub(
            r'@Html\.TextBoxFor\(m\s*=>\s*m\.(\w+)\)',
            r'<input type="text" name="\1" value={props.\1 || ""} onChange={handleChange} />',
            content
        )
        
        # @Html.PasswordFor
        content = re.sub(
            r'@Html\.PasswordFor\(m\s*=>\s*m\.(\w+)\)',
            r'<input type="password" name="\1" value={props.\1 || ""} onChange={handleChange} />',
            content
        )
        
        # @Html.TextAreaFor
        content = re.sub(
            r'@Html\.TextAreaFor\(m\s*=>\s*m\.(\w+)\)',
            r'<textarea name="\1" value={props.\1 || ""} onChange={handleChange}></textarea>',
            content
        )
        
        # @Html.CheckBoxFor
        content = re.sub(
            r'@Html\.CheckBoxFor\(m\s*=>\s*m\.(\w+)\)',
            r'<input type="checkbox" name="\1" checked={props.\1} onChange={handleChange} />',
            content
        )
        
        # @Html.DropDownListFor
        content = re.sub(
            r'@Html\.DropDownListFor\(m\s*=>\s*m\.(\w+),\s*([^)]+)\)',
            r'<select name="\1" value={props.\1} onChange={handleChange}>\n  {/* TODO: Add options from \2 */}\n</select>',
            content
        )
        
        # @Html.ValidationMessageFor
        content = re.sub(
            r'@Html\.ValidationMessageFor\(m\s*=>\s*m\.(\w+)\)',
            r'{errors.\1 && <span className="error">{errors.\1}</span>}',
            content
        )
        
        # @Html.AntiForgeryToken
        content = re.sub(r'@Html\.AntiForgeryToken\(\)', '/* TODO: Add CSRF token */', content)
        
        # @Html.Partial
        content = re.sub(
            r'@Html\.Partial\("([^"]*)"(?:,\s*([^)]+))?\)',
            r'<\1Component {...(\2 || {})} />',
            content
        )
        
        # @Html.Raw
        content = re.sub(r'@Html\.Raw\(([^)]+)\)', r'<div dangerouslySetInnerHTML={{__html: \1}} />', content)
        
        return content
    
    def _convert_tag_helpers(self, content: str) -> str:
        """Convert ASP.NET Core Tag Helpers to JSX"""
        # <a asp-action="" asp-controller="">
        content = re.sub(
            r'<a\s+asp-action="([^"]*)"\s+asp-controller="([^"]*)">',
            r'<a href="/\2/\1">',
            content
        )
        
        # <form asp-action="" asp-controller="">
        content = re.sub(
            r'<form\s+asp-action="([^"]*)"\s+asp-controller="([^"]*)">',
            r'<form onSubmit={handleSubmit}>',
            content
        )
        
        # <input asp-for="">
        content = re.sub(
            r'<input\s+asp-for="(\w+)"',
            r'<input name="\1" value={props.\1 || ""} onChange={handleChange}',
            content
        )
        
        # <label asp-for="">
        content = re.sub(
            r'<label\s+asp-for="(\w+)">',
            r'<label htmlFor="\1">',
            content
        )
        
        # <span asp-validation-for="">
        content = re.sub(
            r'<span\s+asp-validation-for="(\w+)"></span>',
            r'{errors.\1 && <span className="error">{errors.\1}</span>}',
            content
        )
        
        return content
    
    def _fix_jsx_attributes(self, content: str) -> str:
        """Convert HTML attributes to JSX equivalents"""
        # class -> className
        content = re.sub(r'\bclass="', 'className="', content)
        
        # for -> htmlFor
        content = re.sub(r'\bfor="', 'htmlFor="', content)
        
        # Convert boolean attributes
        content = re.sub(r'\bchecked="checked"', 'checked={true}', content)
        content = re.sub(r'\bdisabled="disabled"', 'disabled={true}', content)
        content = re.sub(r'\breadonly="readonly"', 'readOnly={true}', content)
        
        # Convert inline styles (simplified)
        content = re.sub(r'style="([^"]*)"', self._convert_inline_style, content)
        
        return content
    
    def _convert_inline_style(self, match) -> str:
        """Convert inline CSS to JSX style object"""
        style_str = match.group(1)
        styles = []
        
        for prop in style_str.split(';'):
            if ':' in prop:
                key, value = prop.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert to camelCase
                key_parts = key.split('-')
                camel_key = key_parts[0] + ''.join(word.capitalize() for word in key_parts[1:])
                
                styles.append(f'{camel_key}: "{value}"')
        
        if styles:
            return f'style={{{{{", ".join(styles)}}}}}'
        return ''
    
    def _clean_whitespace(self, content: str) -> str:
        """Clean up whitespace and formatting"""
        # Remove multiple blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        return content.strip()
    
    def _extract_props(self, content: str) -> List[str]:
        """Extract props from Razor @model or inferred from usage"""
        props = set()
        
        # Extract from @model directive
        model_match = re.search(r'@model\s+([\w\.]+)', content)
        if model_match:
            # This is the model type, we'd need to infer properties
            # For now, just note that model exists
            props.add('/* TODO: Define props based on model */')
        
        # Extract from Model.Property references
        for match in re.finditer(r'@Model\.(\w+)', content):
            props.add(match.group(1))
        
        # Extract from ViewBag references
        for match in re.finditer(r'@ViewBag\.(\w+)', content):
            props.add(f'{match.group(1)} /* from ViewBag */')
        
        return sorted(props)
    
    def _generate_react_component(self, component_name: str, jsx_content: str, props: List[str]) -> str:
        """Generate complete React component from JSX content"""
        # Determine if component needs state or handlers
        needs_form_handling = 'handleChange' in jsx_content or 'handleSubmit' in jsx_content
        needs_errors = 'errors.' in jsx_content
        
        component = f"""import React from 'react';

const {component_name} = (props) => {{
"""
        
        # Add state hooks if needed
        if needs_form_handling:
            component += """  const [formData, setFormData] = React.useState({});
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Handle form submission
    console.log('Form data:', formData);
  };
  
"""
        
        if needs_errors:
            component += """  const [errors, setErrors] = React.useState({});
  
"""
        
        # Add component JSX
        component += f"""  return (
    {jsx_content}
  );
}};

export default {component_name};
"""
        
        return component
    
    def _generate_report(self, files: List[Path]):
        """Generate conversion report"""
        report_file = self.output_dir / 'CONVERSION_REPORT.md'
        
        with open(report_file, 'w') as f:
            f.write('# Razor to JSX Conversion Report\n\n')
            f.write(f'Total files converted: {len(files)}\n\n')
            f.write('## Manual Review Required\n\n')
            f.write('The following items require manual review and adjustment:\n\n')
            f.write('1. **Complex code blocks** - Check for `TODO: Convert code block` comments\n')
            f.write('2. **Form handling** - Implement `handleSubmit` functions with proper API calls\n')
            f.write('3. **Validation** - Implement client-side validation to match server-side rules\n')
            f.write('4. **Sections** - Handle layout sections (scripts, styles) appropriately\n')
            f.write('5. **Partial views** - Ensure component imports and props are correct\n')
            f.write('6. **Model properties** - Verify all prop types and usages\n')
            f.write('7. **HTML helpers** - Review converted form inputs and bindings\n')
            f.write('8. **Loops** - Check converted @foreach statements work correctly\n')
            f.write('9. **Conditionals** - Verify @if/@else conversions\n')
            f.write('10. **Route generation** - Update links to use proper routing\n\n')
            f.write('## Files Converted\n\n')
            
            for file_path in files:
                relative = file_path.relative_to(self.input_path)
                f.write(f'- {relative}\n')
            
            f.write('\n## Next Steps\n\n')
            f.write('1. Review all converted components for TODOs\n')
            f.write('2. Add proper prop types (PropTypes or TypeScript)\n')
            f.write('3. Implement state management if needed\n')
            f.write('4. Add API integration for data fetching\n')
            f.write('5. Test components individually\n')
            f.write('6. Add styling (CSS modules, styled-components, etc.)\n')
        
        print(f"\n✓ Conversion report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert ASP.NET Razor views to React JSX components'
    )
    parser.add_argument(
        'input',
        help='Path to Razor file or directory containing Razor views'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='./converted',
        help='Output directory for JSX files (default: ./converted)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return 1
    
    converter = RazorToJSXConverter(input_path, args.output)
    
    try:
        if input_path.is_file():
            # Convert single file
            component = converter.convert_file(input_path)
            output_file = Path(args.output) / input_path.with_suffix('.jsx').name
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(component, encoding='utf-8')
            print(f"\n✓ Component saved to: {output_file}")
        else:
            # Convert directory
            converter.convert_directory()
        
        print("\n✓ Conversion completed!")
        print("\nIMPORTANT: Review all generated files and address TODO comments.")
        print("The conversion is semi-automated and requires manual refinement.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
