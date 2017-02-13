# coding: utf-8

from manage import app

if __name__ == '__main__':
    app.debug = True
    app.run(host="120.24.4.254", port=7777)
