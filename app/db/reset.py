# reset_db.py (temporary script)
from session import Base, engine

# ⚠️ WARNING: this deletes all old data
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Database reset successfully")