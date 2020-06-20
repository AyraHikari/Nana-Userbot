# We're using Alpine stable
FROM python:3.7-alpine

#
# We have to uncomment Community repo for some packages
#
# RUN sed -e 's;^#http\(.*\)/v3.9/community;http\1/v3.9/community;g' -i /etc/apk/repositories

# Installing requirements
RUN apk add --no-cache --update \
    bash \
    build-base \
    bzip2-dev \
    curl \
    figlet \
    gcc \
    git \
    sudo \
    util-linux \
    libffi-dev \
    libpq \
    libwebp-dev \
    libxml2 \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    musl \
    neofetch \
    openssl-dev \
    php-pgsql \
    postgresql \
    postgresql-client \
    postgresql-dev \
    py-lxml \
    py-pillow \
    py-pip \
    py-requests \
    py-sqlalchemy \
    py-tz \
    py3-aiohttp \
    openssl \
    pv \
    jq \
    wget \
    python3 \
    python3-dev \
    readline-dev \
    sqlite \
    sqlite-dev \
    sudo

# Installing psycopg2 dependencies
RUN apk add --no-cache --update gcc python3-dev

# Installing postgresql
RUN apk add --no-cache --update postgresql postgresql-client postgresql-dev

# Installing pillow dependencies
RUN apk add --no-cache --update jpeg-dev zlib-dev

# Installing chromium
RUN apk add --no-cache --update chromium chromium-chromedriver

# Installing libpq-dev before py-psycopg2
# RUN apk add --no-cache --update libpq-dev

# RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/main py-psycopg2

RUN pip3 install --upgrade pip setuptools

# Copy Python Requirements to /app

RUN git clone https://github.com/AyraHikari/Nana-Userbot nana
WORKDIR nana

ENV PATH="/home/userbot/bin:$PATH"

#
# Install requirements
#
RUN sudo pip3 install -r requirements.txt
CMD ["python3","-m","nana"]
