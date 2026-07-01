from database.db import SessionLocal
from database.models import User


def get_or_create_user(telegram_user):

    db = SessionLocal()

    try:

        user = db.query(User).filter(
            User.telegram_id == telegram_user.id
        ).first()

        if not user:

            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name
            )

            db.add(user)
            db.commit()

            # تحديث الكائن بعد الحفظ
            db.refresh(user)

        return user

    finally:
        db.close()