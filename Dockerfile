FROM python:3.9-buster

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app
COPY pyproject.toml start-server.sh /opt/app/
COPY . /opt/app
WORKDIR /opt/app
RUN pip install poetry 
RUN poetry install \
    && poetry run python manage.py migrate
RUN chown -R www-data:www-data /opt/app

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["./start-server.sh"]
