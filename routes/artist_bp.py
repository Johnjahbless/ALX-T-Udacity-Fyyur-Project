from flask import Blueprint

# Import functions from controllers
from controllers.artist import artists, search_artists, show_artist, create_artist_form, create_artist_submission, delete_artist, edit_artist, edit_artist_submission


artist_bp = Blueprint('artist_bp', __name__)

# Define appropriate routes
artist_bp.route('/', methods=['GET']) (artists)
artist_bp.route('/search', methods=['POST']) (search_artists)
artist_bp.route('/<int:artist_id>', methods=['GET']) (show_artist)
artist_bp.route('/create', methods=['GET']) (create_artist_form)
artist_bp.route('/create', methods=['POST']) (create_artist_submission)
artist_bp.route('/<artist_id>', methods=['DELETE']) (delete_artist)
artist_bp.route('/<int:artist_id>/edit', methods=['GET']) (edit_artist)
artist_bp.route('/<int:artist_id>/edit', methods=['POST']) (edit_artist_submission)
