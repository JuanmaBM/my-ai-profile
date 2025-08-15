def generate_markdown(profile_data: dict) -> str:
    writing_style_section = _get_writing_style_section(profile_data)
    important_notes_section = _get_important_notes_section(profile_data)
    md = f"""# {profile_data.get('name')}'s profile

{important_notes_section}

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
    
def _get_important_notes_section(profile_data: dict) -> str:
    important_notes_section = ""
    important_notes = profile_data.get('important_notes', '')
    if important_notes:
        important_notes_section = f"""
## Important Notes
Use this section for critical restrictions, annotations, or clarifications about the user that must be considered at all times when interpreting or applying the profile.
These notes override general preferences if there is any conflict.

{important_notes}
"""
    return important_notes_section