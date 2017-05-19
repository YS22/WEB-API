#!flask/bin/python
from app import app
if __name__ == "__main__":
    app.run(host='0.0.0.1',port=8082,debug=True)