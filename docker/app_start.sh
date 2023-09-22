if [ "$ENV"  = "localdev" ]
then

  source "/app/bin/activate"
  cd /app
  python manage.py migrate
  python manage.py initialize_db

fi
