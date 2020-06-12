# We're using Alpine stable
FROM alpine:edge

#
# We have to uncomment Community repo for some packages
#
RUN sed -e 's;^#http\(.*\)/v3.9/community;http\1/v3.9/community;g' -i /etc/apk/repositories

# Installing Python
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
    chromium \
    chromium-chromedriver \
    jpeg-dev \
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
    python-dev \
    openssl \
    pv \
    jq \
    wget \
    python3 \
    python3-dev \
    readline-dev \
    sqlite \
    sqlite-dev \
    sudo \
    zlib-dev

RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/main py-psycopg2

RUN pip3 install --upgrade pip setuptools

# Copy Python Requirements to /app

RUN git clone https://github.com/AyraHikari/Nana-TgBot nana
WORKDIR nana

ENV PATH="/home/userbot/bin:$PATH"

#
# Install requirements
#
RUN sudo pip3 install -r requirements.txt
CMD ["python3","-m","nana"]
