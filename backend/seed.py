from app import SessionLocal, password_hash, text

with SessionLocal() as db:
    existing = db.execute(
        text("SELECT id FROM users WHERE username='admin'")
    ).first()

    if not existing:
        db.execute(
            text(
                "INSERT INTO users(username,password_hash,display_name,role) "
                "VALUES ('admin', :password_hash, 'Cloud Lab Administrator', 'admin')"
            ),
            {"password_hash": password_hash.hash("ChangeMe123!")},
        )
        db.commit()
        print("Seeded admin user.")
    else:
        print("Admin user already exists.")
