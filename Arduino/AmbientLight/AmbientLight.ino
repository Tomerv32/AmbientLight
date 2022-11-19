#include <FastLED.h>
FASTLED_USING_NAMESPACE

#define DATA_PIN    3
#define LED_TYPE    WS2812
#define COLOR_ORDER GRB
#define NUM_LEDS    46
#define BRIGHTNESS  96
CRGB leds[NUM_LEDS];

#define BUFFER_SIZE 12
byte buff[BUFFER_SIZE];

void setup() {
  Serial.begin(250000);

  FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  // FastLED.setMaxRefreshRate(0, false);  // turn OFF the refresh rate constraint

}


void loop() {
  if (Serial.available())
  {
    Serial.readBytes(buff, BUFFER_SIZE);
    for (int i=0; i<BUFFER_SIZE; i=i+4)
    {
      leds[int(buff[i])].r = int(buff[i+1]);
      leds[int(buff[i])].g = int(buff[i+2]);
      leds[int(buff[i])].b = int(buff[i+3]);
    }
    FastLED.show();
    // delay(50);
  }
}
