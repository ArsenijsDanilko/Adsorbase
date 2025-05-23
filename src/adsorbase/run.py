from .app import app

def launch():
    app.run(debug=True)

if __name__ == '__main__':
    launch()
