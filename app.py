import logging
import _config
from flask import Flask
from controller import pages, classes
import os

app = Flask(__name__, template_folder=_config.TEMPLATES_DIR, static_folder=_config.STATIC_DIR)

app.register_blueprint(pages.pages)
app.register_blueprint(classes.classes)


# run the Flask app
if __name__ == '__main__':
    logging.basicConfig(filename=_config.LOGFILE,
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

    app.run(debug=_config.DEBUG, threaded=True)
