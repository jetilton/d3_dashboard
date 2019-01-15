from app import app, db
from app.models import User, Cbt, Paths
from app.forms import PathsForm
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Cbt': Cbt, 'Paths': Paths, 'pf':PathsForm}
