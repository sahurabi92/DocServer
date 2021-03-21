from apps import create_app
"""start the server"""
app, db = create_app()
app.app_context().push()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
