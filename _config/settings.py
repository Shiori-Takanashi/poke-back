import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# セキュリティの観点から、重要に管理せよ！
SECRET_KEY = 'django-insecure-t0ai@w7w#pr+9(br56@_!qq2#t9o63g%%(3s_dz$d)2=&diovw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# --------------------
# 「機能する」アプリの総覧
# --------------------

# 重要：アプリを導入しても、ここに追加しないと機能しない！
# 重要: アプリ名は、慎重に変更すること！アプリ名を適当に決めるな！
# 注意：startappしたり、pip installして、油断しないこと。
# 注意：rest_frameworkが抜けやすい。
# 理由：登録しなければ、migrationやadminが読み込まれないから。
# 失敗：ここに登録せずに、エラーを頻発。嫌でもsettingを確認する習慣。
# 失敗：自作したアプリ名のタイポに気づかなかった。

# 注意：自作アプリについて

    # app_name.apps.app_nameの変化形である。
    # app_nameは、ハイフンを含めない！
    # アンダーバーの省略、キャメルケースの使用、Configの追加が必要。

    # 'example_aplication'（アプリ名）であるとき、
    # 'ExampleAplicationConfig'を登録せよ。

    # アプリ名をcopilotに変更させて、app.pyを誤ったことあり。
    # アプリ名の変更は、慎重に行うこと。（大事だから2回言う）


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 自作アプリ
    'ep_registry.apps.EpRegistryConfig',
    'fetch_pokemon.apps.FetchPokemonConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '_config.wsgi.application'

# データベース変更 （2025/06/08）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pokeback',
        'USER': 'shiori',
        'PASSWORD': 'Obear0311',
        'HOST': 'localhost',
        'PORT': '5432',        # PostgreSQLのデフォルトポート
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
