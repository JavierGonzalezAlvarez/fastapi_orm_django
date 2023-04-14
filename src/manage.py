def init_django():
    import django
    from django.conf import settings
    
    if settings.configured:
        return

    settings.configure(
        INSTALLED_APPS=[            
            'db',  
            #'corsheaders',          
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'ecommerce',
                'USER': 'test',
                'PASSWORD': '2525_ap',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            },
        },

        MIDDLEWARE = [
        #'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        
        ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '127.0.0.1:8000', '[::1]', '0.0.0.0'],

        LANGUAGE_CODE = 'es-us',

        TIME_ZONE = 'Europe/Madrid',

    )
    django.setup()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    init_django()
    execute_from_command_line()