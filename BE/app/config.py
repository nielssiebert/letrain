class Config:
    BASE_PATH = '/letrain'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///letrain.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENABLE_AUTH = False  # Toggle authentication