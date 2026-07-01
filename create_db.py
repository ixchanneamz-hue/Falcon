from database.db import engine
from database.db import Base

import database.models

Base.metadata.create_all(bind=engine)

print("Tables created successfully ✅")
