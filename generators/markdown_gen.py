def generate_markdown(profile_data: dict) -> str:
    md = f"""# {profile_data.get('name')}'s profile

## Personality
{profile_data.get('personality')}

## Writing style
{profile_data.get('writing_style')}

## Code style
{profile_data.get('code_style')}

## Interests
- {chr(10).join(profile_data.get('topics', []))}
"""
    return md
