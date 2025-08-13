def generate_markdown(profile_data: dict) -> str:
    md = f"""# Perfil de {profile_data.get('name')}

## Personalidad
{profile_data.get('personality')}

## Estilo de escritura
{profile_data.get('writing_style')}

## Estilo de código
{profile_data.get('code_style')}

## Temas de interés
- {chr(10).join(profile_data.get('topics', []))}
"""
    return md
