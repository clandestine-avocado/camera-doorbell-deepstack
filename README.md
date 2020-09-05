# doorbell

Purpose:
Allow for doorbell press to:
- capture still image
- record short video
- sound a buzzer so user gets audible feedback
- send images over MQTT to Home Assistant Node-Red
- Get push notifications (via Telegram?)

Without button press, allow for object (person only) detection:
- Tensorflow ([Tensorflow HA Integration](https://www.home-assistant.io/integrations/tensorflow/) | [Install Page](https://www.tensorflow.org/install/)) 
- Tensorflow Lite
- DOODS ([DOODS HA Integration](https://www.home-assistant.io/integrations/doods/) | [DOODS in GIT](https://github.com/snowzach/doods))
- Other software?




# Equipment:
- [Rasperry Pi 3A](https://www.microcenter.com/product/514076/3_Model_A_Board?storeID=081)
- [Pi NoIR camera module](https://www.amazon.com/gp/product/B07W5T3J5T/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)
- [Momentary button switch w/ LED backlight](https://www.aliexpress.com/item/32956631402.html?spm=a2g0s.9042311.0.0.73504c4dbyl6RU)
- [5V Piezo Buzzer (PASSIVE)](https://www.aliexpress.com/item/32974555488.html?spm=a2g0s.9042311.0.0.73504c4dbyl6RU)
- [5V Piezo Buzzer (ACTIVE)](https://www.amazon.com/gp/product/B07GL4MBLM/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
