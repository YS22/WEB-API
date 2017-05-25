from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
role = Table('role', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('position', String),
    Column('name', String),
    Column('tel', String),
    Column('user_id', Integer),
)

group = Table('group', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('groupname', String),
)

group = Table('group', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('createTime', DateTime),
    Column('tag', String),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String),
    Column('gender', String),
    Column('avatarUrl', String),
    Column('tel', String(length=11)),
    Column('location', String),
    Column('state', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['role'].drop()
    pre_meta.tables['group'].columns['groupname'].drop()
    post_meta.tables['group'].columns['createTime'].create()
    post_meta.tables['group'].columns['name'].create()
    post_meta.tables['group'].columns['tag'].create()
    post_meta.tables['user'].columns['avatarUrl'].create()
    post_meta.tables['user'].columns['gender'].create()
    post_meta.tables['user'].columns['location'].create()
    post_meta.tables['user'].columns['state'].create()
    post_meta.tables['user'].columns['tel'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['role'].create()
    pre_meta.tables['group'].columns['groupname'].create()
    post_meta.tables['group'].columns['createTime'].drop()
    post_meta.tables['group'].columns['name'].drop()
    post_meta.tables['group'].columns['tag'].drop()
    post_meta.tables['user'].columns['avatarUrl'].drop()
    post_meta.tables['user'].columns['gender'].drop()
    post_meta.tables['user'].columns['location'].drop()
    post_meta.tables['user'].columns['state'].drop()
    post_meta.tables['user'].columns['tel'].drop()
