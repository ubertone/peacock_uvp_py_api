# peacock_uvp_py_api

Modbus API written in Python for measurement control of Ubertone's Peacock UVP, 
the OEM acoustic profiler dedicated to environmental monitoring and industrial 
applications.



sorry for the remaining French comments, we will work on it soon.

On windows/cygwin 750000 BAUD is not allowed by the operating system

# test

run test with :

```
python3 ./tests/test_modbus.py
python3 ./tests/test_apf04_driver_basic.py
python3 ./tests/test_apf04_driver.py
```

or start a specific test with :

```
python test_apf04_driver.py TestApf04Handler.test_settings
```
