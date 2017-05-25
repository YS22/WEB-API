from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
inspect = Table('inspect', post_meta,
    Column('groupid', String, primary_key=True, nullable=False),
    Column('createrid', String),
    Column('userid', String),
    Column('time', DateTime),
    Column('user_id', Integer),
)

group = Table('group', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('createrId', String),
    Column('createTime', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['inspect'].create()
    post_meta.tables['group'].columns['createrId'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['inspect'].drop()
    post_meta.tables['group'].columns['createrId'].drop()
