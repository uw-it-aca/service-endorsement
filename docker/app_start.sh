if [ "$ENV"  = "localdev" ]
then

  source "/app/bin/activate"
  cd /app
  python manage.py migrate
  python manage.py initialize_db

else

  # adjust timeouts to account for slow downstream response
  DOWNSTREAM_TIMEOUT=300

  export GUNICORN_CMD_ARGS="--timeout $DOWNSTREAM_TIMEOUT"

  sed 's/\(^[ ]*server {\)/  proxy_read_timeout '$DOWNSTREAM_TIMEOUT's;\n\n\1/' /etc/nginx/nginx.conf > /tmp/nginx.tmp
  cat /tmp/nginx.tmp > /etc/nginx/nginx.conf

fi
