# create_majors.py
'''TO USE:
python manage.py shell

from create_majors import create_majors
create_majors()

'''

from registration.models import Major

def create_majors():
    majors = [
        {"name": "Computer Science", "description": "Study of computers and computational systems."},
        {"name": "Mathematics", "description": "Study of numbers, quantities, and shapes."},
        {"name": "English", "description": "Study of literature, writing, and language."},
        {"name": "Physics", "description": "Study of matter, energy, and the fundamental forces of nature."},
        {"name": "Biology", "description": "Study of living organisms and their interactions."},
        {"name": "Chemistry", "description": "Study of substances, their properties, and reactions."},
        {"name": "History", "description": "Study of past events, societies, and civilizations."},
        {"name": "Psychology", "description": "Study of the human mind and behavior."},
        {"name": "Economics", "description": "Study of production, distribution, and consumption of goods and services."},
        {"name": "Art", "description": "Study of creative expression through visual, auditory, or performance mediums."},
    ]
    

    for major_data in majors:
        major, created = Major.objects.get_or_create(
            name=major_data["name"],
            defaults={"description": major_data["description"]}
        )
        if created:
            print(f"Created major: {major.name}")
        else:
            print(f"Major already exists: {major.name}")

# Call the function
create_majors()