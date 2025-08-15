def generate_markdown(profile_data: dict) -> str:
    writing_style_section = _get_writing_style_section(profile_data)
    md = f"""# {profile_data.get('name')}'s profile

## Personality
{profile_data.get('personality')}

## Writing style
{writing_style_section}

## Code style
{profile_data.get('code_style')}

## Interests
{chr(10).join(f'- {t}' for t in profile_data.get('topics', []))}
"""
    return md

def _get_writing_style_section(profile_data: dict) -> str:
    writing_style_section = ""
    writing_style = profile_data.get('writing_style', '')
    
    if isinstance(writing_style, dict):
        if writing_style:
            writing_style_section = "\n".join([
                f"### {platform.title()}\n{analysis}" 
                for platform, analysis in writing_style.items()
            ])
        else:
            writing_style_section = "No writing style analysis available."
    else:
        writing_style_section = writing_style or "No writing style analysis available."
    return writing_style_section
    
