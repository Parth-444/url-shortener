class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:12345@localhost:5432/url_shortener"
    SQLALCHEMY_TRACK_MODIFICATIONS = False