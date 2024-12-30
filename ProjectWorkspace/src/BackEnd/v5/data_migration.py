# data_migration.py

from app import db, create_app
from app.models import User
import json

app = create_app()
with app.app_context():
    users = User.query.all()
    for user in users:
        if user.favorite_places:
            try:
                json.loads(user.favorite_places)
            except json.JSONDecodeError:
                # Convert comma-separated string to JSON array
                places = [place.strip() for place in user.favorite_places.split(',')]
                user.favorite_places = json.dumps(places)
                db.session.add(user)
    db.session.commit()
    print("Data migration completed.")
