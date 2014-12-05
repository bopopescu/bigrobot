The REST services are implemented using the Python Flask module. Be sure to
install Flask on the system which runs the service.

  % pip install flask

By convention, we advertise the services in the YAML config.

  % cat bigrobot/configs/rest_services.yaml
  ...
  send_mail:
    url: http://qa-rest.qa.bigswitch.com:5000/
  ...

