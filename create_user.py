from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():

    user = User.query.filter_by(username="admin").first()

    if user:

        user.password = generate_password_hash("admin123")

        db.session.commit()

        print("Admin password updated successfully!")

    else:

        user = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="Admin"
        )

        db.session.add(user)
        db.session.commit()

        print("Admin user created successfully!")