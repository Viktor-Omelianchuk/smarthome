=========
SMARTHOME
=========

Django smart home control server with a web interface for configuration and manual control that will periodically poll sensors and automatically respond in case of certain situations using the smart home controller API

Having entered https://smarthome.webpython.graders.eldf.ru/ and registered, you will receive a unique key (KEY) that you will need to use when working with the controller API. Using the same key, you can get an image from the “virtual camera” of a smart home, which will clearly show which devices are working or why a particular sensor has triggered, and manually control the devices. API documentation can be viewed on the same site.

Devices connected to the controller are available for recording (usually true - enable / open, false - disable / close, but there are options). Both sensors and devices are readable. Devices, when reading from them, act as sensors and return their state, which may differ from the one written.

Implement automatically polling the controller in the background every 5 seconds (django celery) and reacting to some events.

 Automatically poll the controller in the background every second and react to some events.

 If there is a water leak (leak_detector = true), close the cold (cold_water = false) and hot (hot_water = false) water and send a letter at the time of detection.

 If cold water (cold_water) is closed, immediately turn off the boiler (boiler) and the washing machine (washing_machine) and under no circumstances turn them on until the cold water is opened again.

 If hot water has a temperature (boiler_temperature) less than hot_water_target_temperature - 10%, you need to turn on the boiler (boiler), and wait until it reaches the temperature hot_water_target_temperature + 10%, after which, in order to save energy, the boiler must be turned off

 If the curtains are partially open (curtains == “slightly_open”), then they are manually controlled - this means their state cannot be changed automatically under any circumstances.

 If the street (outdoor_light) is darker than 50, open the curtains (curtains), but only if the lamp in the bedroom (bedroom_light) is not lit. If the street (outdoor_light) is lighter than 50, or the light in the bedroom (bedroom_light) is on, close the curtains. Except when they are manually operated

 If smoke is detected (smoke_detector), immediately turn off the following appliances [air_conditioner, bedroom_light, bathroom_light, boiler, washing_machine], and under no circumstances turn them on until the smoke disappears.

 If the temperature in the bedroom (bedroom_temperature) has risen above bedroom_target_temperature + 10% - turn on the air conditioner (air_conditioner), and wait until the temperature drops below bedroom_target_temperature - 10%, then turn off the air conditioner.

Installation
-------------------
On Unix, Linux, BSD, macOS, and Cygwin::

  $ git clone https://github.com/Viktor-Omelianchuk/smarthome.git

Create and activate isolated Python environments
-------------------------------------------------
::

    $ cd smarthome
    $ virtualenv env
    $ source env/bin/activate

Install requirements
--------------------------------------
::

    $ pip install -r requirements.txt


Run Redis
--------------------------------------
::

    $ docker run --name some-redis -p 6379:6379 redis
    
    
Run Celery
--------------------------------------
::

    $ celery -A coursera_house worker  -B -l info
    
Run local development server
--------------------------------------
::

    $ python manage.py runserver
 
