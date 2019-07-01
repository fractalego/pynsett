from pynsett.server import pynsett_app

if __name__ == '__main__':
    pynsett_app.run(debug=True, port=4001, host='0.0.0.0')