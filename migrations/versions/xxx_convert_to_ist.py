"""Convert timestamps to IST

Revision ID: xxx
Revises: ff07d8515622
Create Date: 2024-xx-xx xx:xx:xx.xxx

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def upgrade():
    # Get database connection
    connection = op.get_bind()
    
    # Update cigarettes table
    connection.execute("""
        UPDATE cigarettes 
        SET smoked_at = smoked_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata'
        WHERE smoked_at IS NOT NULL
    """)
    
    # Update users table
    connection.execute("""
        UPDATE users 
        SET created_at = created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata'
        WHERE created_at IS NOT NULL
    """)

def downgrade():
    # Convert back to UTC if needed
    connection = op.get_bind()
    
    connection.execute("""
        UPDATE cigarettes 
        SET smoked_at = smoked_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
        WHERE smoked_at IS NOT NULL
    """)
    
    connection.execute("""
        UPDATE users 
        SET created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
        WHERE created_at IS NOT NULL
    """) 