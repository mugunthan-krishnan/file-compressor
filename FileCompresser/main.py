import os
import sys
from flask import Flask, render_template

def create_app(config_filename=''):
    app = Flask(__name__)

    with app.app_context():
        from views.home import home
        app.register_blueprint(home)
        from views.compression import compress
        app.register_blueprint(compress)
        from views.decompression import decompress
        app.register_blueprint(decompress)
        return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))