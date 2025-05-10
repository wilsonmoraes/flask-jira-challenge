FLASK_ENV=development
FLASK_APP=api_service.app:create_app
SECRET_KEY=Dyn4m1cAsS3tKey
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db
RESTPLUS_MASK_SWAGGER=False
CACHE_TYPE=RedisCache
CACHE_REDIS_URL=redis://localhost:6379/0