from sqlalchemy import Column, Integer, BigInteger, String, Float
from database.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    balance = Column(Float, default=0)
    referrals = Column(Integer, default=0)
    referrer_id = Column(BigInteger, nullable=True)


class WithdrawRequest(Base):
    __tablename__ = 'withdraw_requests'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)
    wallet_address = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')


class PackageOrder(Base):
    __tablename__ = 'package_orders'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    package_name = Column(String(100), nullable=False)
    package_price = Column(Float, nullable=False)
    post_link = Column(String(500), nullable=False)
    payment_image = Column(String(500))
    status = Column(String(20), default='pending')


class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    customer_id = Column(BigInteger, nullable=False)
    package_name = Column(String(100), nullable=False)
    post_link = Column(String(500), nullable=False)
    target_count = Column(Integer, nullable=False)
    completed_count = Column(Integer, default=0)
    reward = Column(Float, default=0.005)
    status = Column(String(20), default='active')


class CampaignParticipant(Base):
    __tablename__ = 'campaign_participants'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, nullable=False)
    telegram_id = Column(BigInteger, nullable=False)


class CampaignComment(Base):
    __tablename__ = 'campaign_comments'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    comment = Column(String(1000), nullable=False)
    rating = Column(Integer, default=0)


class ReferralEarning(Base):
    __tablename__ = 'referral_earnings'
    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger, nullable=False, index=True)
    referred_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(Float, default=0)
    status = Column(String(20), default='pending')
    created_at = Column(String(50), nullable=True)
