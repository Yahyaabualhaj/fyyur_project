"""empty message

Revision ID: a50dd682f84f
Revises: 1856999c3ee4
Create Date: 2020-07-25 16:41:48.878146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a50dd682f84f'
down_revision = '1856999c3ee4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('ArtistGenres_artist_id_fkey', 'ArtistGenres', type_='foreignkey')
    op.create_foreign_key(None, 'ArtistGenres', 'Artist', ['artist_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('VenueGenres_venue_id_fkey', 'VenueGenres', type_='foreignkey')
    op.create_foreign_key(None, 'VenueGenres', 'Venue', ['venue_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('show_artist_artist_id_fkey', 'show_artist', type_='foreignkey')
    op.drop_constraint('show_artist_venue_id_fkey', 'show_artist', type_='foreignkey')
    op.create_foreign_key(None, 'show_artist', 'Venue', ['venue_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'show_artist', 'Artist', ['artist_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'show_artist', type_='foreignkey')
    op.drop_constraint(None, 'show_artist', type_='foreignkey')
    op.create_foreign_key('show_artist_venue_id_fkey', 'show_artist', 'Venue', ['venue_id'], ['id'])
    op.create_foreign_key('show_artist_artist_id_fkey', 'show_artist', 'Artist', ['artist_id'], ['id'])
    op.drop_constraint(None, 'VenueGenres', type_='foreignkey')
    op.create_foreign_key('VenueGenres_venue_id_fkey', 'VenueGenres', 'Venue', ['venue_id'], ['id'])
    op.drop_constraint(None, 'ArtistGenres', type_='foreignkey')
    op.create_foreign_key('ArtistGenres_artist_id_fkey', 'ArtistGenres', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###
