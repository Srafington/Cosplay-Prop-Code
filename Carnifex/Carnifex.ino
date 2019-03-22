#include <Adafruit_NeoPixel.h>

#define TRIGGER 3
#define NEO 4
#define IMPACT 5
#define FIRE 11
#define OVERHEAT 12
#define RELOAD 13

//See the "Neopixel Uberguide" on the Adafruit Learning system to understand
//how to use these WS2812 controlled LEDs
Adafruit_NeoPixel lights = Adafruit_NeoPixel(3, NEO, NEO_GRB + NEO_KHZ800);

int shotsFired = 0;
const uint32_t SIDES = lights.Color(28, 255, 236),
               HOT_SIDE = lights.Color(255, 0, 0),
               BARREL = lights.Color(83, 255, 15),
               OFF = lights.Color(0, 0, 0);
void setup()
{
  //Init inputs where the input sensor will pull the line to ground
  pinMode(TRIGGER, INPUT);
  digitalWrite(TRIGGER, HIGH);
  pinMode(IMPACT, INPUT);
  digitalWrite(IMPACT, HIGH);

  //Init outputs to sound board which need to be pulled low to trigger
  pinMode(FIRE, OUTPUT);
  digitalWrite(FIRE, HIGH);
  pinMode(OVERHEAT, OUTPUT);
  digitalWrite(OVERHEAT, HIGH);
  pinMode(RELOAD, OUTPUT);
  digitalWrite(RELOAD, HIGH);

  //Init the neopixels
  lights.begin();
  lights.setPixelColor(0, SIDES);
  lights.setPixelColor(1, OFF);
  lights.setPixelColor(2, SIDES);
  lights.show();
}

void loop()
{
  if (digitalRead(TRIGGER) == HIGH)
  {
    if (shotsFired < 5)
    {
      digitalWrite(FIRE, LOW);
      delay(300);
      lights.setPixelColor(1, BARREL);
      lights.show();
      delay(200);
      digitalWrite(FIRE, HIGH);
      lights.setPixelColor(1, OFF);
      lights.show();
      delay(1000);
      shotsFired++;
    }
    else
    {
      digitalWrite(OVERHEAT, LOW);
      delay(200);
      digitalWrite(OVERHEAT, HIGH);
      delay(2600);
    }
  }
  else if ((digitalRead(IMPACT) == LOW) && (shotsFired > 0))
  {
    shotsFired = 0;
    digitalWrite(RELOAD, LOW);
    delay(100);
    digitalWrite(RELOAD, HIGH);
    delay(900);
  }
  if (shotsFired < 5)
  {
    lights.setPixelColor(0, SIDES);
    lights.setPixelColor(2, SIDES);
    lights.show();
  }
  else
  {
    lights.setPixelColor(0, HOT_SIDE);
    lights.setPixelColor(2, HOT_SIDE);
    lights.show();
  }
}
