from database.db import Base
from database.db import engine

from database.models import (
    User,
    WithdrawRequest,
    PackageOrder,
    Campaign,
    CampaignParticipant,
    CampaignComment
)

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")