if [ "$ENV"  = "localdev" ]
then

  source "/app/bin/activate"
  cd /app
  python manage.py migrate
  python manage.py initialize_db

else

  # set nginx proxy read timeout
  sed 's/\(^[ ]*server {\)/  proxy_read_timeout 300s;\n\n\1/' /etc/nginx/nginx.conf > /tmp/nginx.tmp
  cat /tmp/nginx.tmp > /etc/nginx/nginx.conf


fi
