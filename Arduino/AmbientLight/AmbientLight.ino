#include <FastLED.h>
FASTLED_USING_NAMESPACE

#define DATA_PIN    3
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
#define NUM_LEDS    100
#define BRIGHTNESS  255
CRGB leds[NUM_LEDS];

#define SERIAL_BAUD_RATE 115200

#define VALUES_PER_LED 4
#define LED_PER_SHOW 3

#define BUFFER_SIZE VALUES_PER_LED*LED_PER_SHOW
byte buff[BUFFER_SIZE];

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);

  FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.setMaxRefreshRate(0, false);  // turn OFF the refresh rate constraint
}

void loop() {
  if (Serial.available())
  {
    Serial.readBytes(buff, BUFFER_SIZE);

    for(int i=0; i<BUFFER_SIZE; i+=VALUES_PER_LED)
    {
      leds[int(buff[i])].r = int(buff[i+1]);
      leds[int(buff[i])].g = int(buff[i+2]);
      leds[int(buff[i])].b = int(buff[i+3]);
    }
    FastLED.show();
  }
}
