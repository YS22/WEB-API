from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('ID', String, primary_key=True, nullable=False),
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
    Column('location', String),
    Column('state', String),
)

registrations = Table('registrations', pre_meta,
    Column('user_ID', Integer),
    Column('group_id', Integer),
)

registrations = Table('registrations', post_meta,
    Column('user_id', Integer),
    Column('group_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['ID'].drop()
    post_meta.tables['user'].columns['id'].create()
    pre_meta.tables['registrations'].columns['user_ID'].drop()
    post_meta.tables['registrations'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['ID'].create()
    post_meta.tables['user'].columns['id'].drop()
    pre_meta.tables['registrations'].columns['user_ID'].create()
    post_meta.tables['registrations'].columns['user_id'].drop()
