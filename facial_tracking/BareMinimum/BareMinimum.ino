#include <Servo.h>

Servo tiltServo; // Up-down servo
Servo panServo; // Left-right servo

int pan, tilt, movementDegree;
bool moveRight, moveLeft, moveUp, moveDown = false;

void setMovement(String data)
{
    if (data.indexOf("left") > -1) {
        moveLeft = true;
    }
    else if (data.indexOf("right") > -1) {
        moveRight = true;
    }

    if (data.indexOf("up") > -1) {
        moveUp = true;
    }
    else if (data.indexOf("down") > -1) {
        moveDown = true;
    }

    if (data.indexOf("high") > -1) {
        movementDegree = 7;
    }
    else if (data.indexOf("med") > -1) {
        movementDegree = 4;
    }
    else {
        movementDegree = 2;
    }
}

void resetMove()
{
    moveLeft = false;
    moveRight = false;
    moveUp = false;
    moveDown = false;
}

void moveServos()
{
    if (moveRight) {
        panServo.write(panServo.read() + movementDegree);
    }
    else if (moveLeft) {
        panServo.write(panServo.read() - movementDegree);
    }

    if (moveUp) {
        tiltServo.write(tiltServo.read() - movementDegree);
    }
    else if (moveDown) {
        tiltServo.write(tiltServo.read() + movementDegree);
    }
}

void setup()
{
    // For debugging
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(115200);
    Serial.setTimeout(50);

    panServo.attach(6); // Attach pan servo to pin 6
    tiltServo.attach(7); // Attach tilt servo to pin 7

    panServo.write(90);
    tiltServo.write(90);
}

void loop()
{
    if (Serial.available() > 0) {
        String data = Serial.readString();
        setMovement(data);
        moveServos();
        resetMove();
    }
}