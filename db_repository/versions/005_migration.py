from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('id', String, primary_key=True, nullable=False),
    Column('nickname', String),
    Column('gender', String),
    Column('avatarUrl', String),
    Column('tel', String),
    Column('location', String),
    Column('state', String),
)

user = Table('user', post_meta,
    Column('id', String, primary_key=True, nullable=False),
    Column('nickname', String),
    Column('gender', String),
    Column('avatarUrl', String),
    Column('tel', String(length=11)),
    Column('latitude', String),
    Column('longitude', String),
    Column('state', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['location'].drop()
    post_meta.tables['user'].columns['latitude'].create()
    post_meta.tables['user'].columns['longitude'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['location'].create()
    post_meta.tables['user'].columns['latitude'].drop()
    post_meta.tables['user'].columns['longitude'].drop()
