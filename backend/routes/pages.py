from flask import Blueprint, send_from_directory, current_app
import os

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/admin')
@pages_bp.route('/admin/')
@pages_bp.route('/admin.html')
def admin_page():
    # BASE_DIR is in database.py but we can't import it easily if circular, 
    # but we can deduce it or import from current_app config if we set it.
    # Simpler: dedup logic.
    # We know backend/routes/pages.py is depth 2 from backend root.
    # But let's just use relative paths from the backend dir.
    # The app is run from backend/app.py usually.
    # root_path is backend/.
    # One level up is project root.
    # Page dir is project_root/Page.
    
    # Let's rely on relative path from where app is run (backend dir).
    page_dir = os.path.abspath(os.path.join(os.getcwd(), '../Page'))
    # Fallback if run from elsewhere
    if not os.path.exists(page_dir):
         # try relative to this file
         current_dir = os.path.dirname(os.path.abspath(__file__))
         page_dir = os.path.abspath(os.path.join(current_dir, '../../Page'))
         
    return send_from_directory(page_dir, 'admin.html')


# Serve the Page/ static files so frontend can call same-origin APIs
@pages_bp.route('/', defaults={'path': 'index.html'})
@pages_bp.route('/<path:path>')
def serve_page(path):
    page_dir = os.path.abspath(os.path.join(os.getcwd(), '../Page'))
    if not os.path.exists(page_dir):
         current_dir = os.path.dirname(os.path.abspath(__file__))
         page_dir = os.path.abspath(os.path.join(current_dir, '../../Page'))

    target = os.path.join(page_dir, path)
    if os.path.exists(target) and os.path.isfile(target):
        return send_from_directory(page_dir, path)
    # fallback to index
    if path == 'index.html' or not path:
         return send_from_directory(page_dir, 'index.html')
         
    # if not found return 404 or index? 
    # Usually SPA returns index, but this is simple static serving.
    return send_from_directory(page_dir, 'index.html')
