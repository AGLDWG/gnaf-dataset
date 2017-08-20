import logging
import _config
from flask import Flask
from controller import pages, model_classes
app = Flask(__name__)

app.register_blueprint(pages.pages)
app.register_blueprint(model_classes.model_classes)


# run the Flask app
if __name__ == '__main__':
    logging.basicConfig(filename=_config.LOGFILE,
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

    app.run(debug=_config.DEBUG)
