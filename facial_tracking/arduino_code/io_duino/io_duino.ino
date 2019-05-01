/*Expecations:
    LCD running on pins 12, 11, 5, 4, 3, and 2
    LED on pin 6
    Button on pin 7
    Connections between two arduino 0 and 1 pins
    Shared ground between both
*/

//Include the liquid crystal library
#include <LiquidCrystal.h>

//Set up the LCD
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

//Pins for other IO
const int buttonPin = 7;
const int ledPin = 6;

//Stores the time of the last button press
unsigned long lastButtonPress = 0;

//Half a second delay for button presses
unsigned long debounceDelay = 500;

//Tracking if the lcd has changed
String lastSerial;

boolean lcdChanged = false;
boolean lcd_on = false;

void setup()
{
    //Start the lcd
    lcd.begin(16, 2);

    //Print the default message of 0 faces
    lcd.print("Press button to");
    lcd.setCursor(0, 1);
    lcd.print("track faces");
    //Set the pinmode for buttons and LED
    pinMode(ledPin, OUTPUT);
    pinMode(buttonPin, INPUT);

    //Start a serial Connections
    Serial.begin(115200);
}

void loop()
{
    //Stores the reading from the button
    int buttonReading = digitalRead(buttonPin);

    //If the button is pressed
    //And we have waited long enough since the last press
    if (buttonReading == HIGH && (millis() - lastButtonPress) > debounceDelay) {
        //Send serial information to our python program
        Serial.println("toggleTracking");

        //Set the last buttonPress time
        lastButtonPress = millis();
    }

    //If we recieved serial data
    if (Serial.available() > 0) {
        digitalWrite(LED_BUILTIN, LOW);
        String data = Serial.readString();
        //Determine if our data is related to detected faces or LED
        if (data.indexOf("toggleLED") > -1) {
          digitalWrite(ledPin, HIGH);
        }
        else if (data.indexOf("faceData") > -1) {
            data = data.substring(9,17);
            data.trim(); // Trims whitespace characters
            lcd.clear();
            lcd.print(data);
        }
    }
}
