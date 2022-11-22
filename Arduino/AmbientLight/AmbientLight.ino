#include <FastLED.h>
FASTLED_USING_NAMESPACE

#define DATA_PIN    3
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
#define NUM_LEDS    100
#define BRIGHTNESS  100
CRGB leds[NUM_LEDS];

#define SERIAL_BAUD_RATE 9600

#define VALUES_PER_LED 4

#define BUFFER_SIZE VALUES_PER_LED
byte buff[BUFFER_SIZE];


void setup() {
  Serial.begin(SERIAL_BAUD_RATE);

  FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  // FastLED.setMaxRefreshRate(0, false);  // turn OFF the refresh rate constraint
}

void loop() {
  // int brightness = analogRead(pot_pin);
  // map potentiometer value to 0-255
  // FastLED.setBrightness(brightness);

  if (Serial.available())
  {
    Serial.readBytes(buff, BUFFER_SIZE);

    leds[int(buff[0])].r = int(buff[1]);
    leds[int(buff[0])].g = int(buff[2]);
    leds[int(buff[0])].b = int(buff[3]);

    FastLED.show();
  }
}
