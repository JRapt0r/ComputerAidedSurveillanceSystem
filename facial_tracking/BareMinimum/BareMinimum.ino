#include <Servo.h>

//Up down servo
Servo tiltServo;

//Left right servo
Servo panServo;

int pan, tilt;

bool moveRight, moveLeft, moveUp, moveDown = false;
void SetMovement(String data){
    if(data.indexOf("left") > -1){
      moveLeft = true;
    }else if(data.indexOf("right") > -1){
      moveRight = true;
    }

    if(data.indexOf("up") > -1){
      moveUp = true;
    }else if(data.indexOf("down") > -1){
      moveDown = true;
    }
}

void ResetMove(){
  moveLeft = false;
  moveRight = false;
  moveUp = false;
  moveDown = false;
}

void MoveServos(){
  if(moveRight){
    panServo.write(panServo.read() + 5);
  }else if(moveLeft){
    panServo.write(panServo.read() - 5);
  }

  if(moveUp){
    tiltServo.write(tiltServo.read() + 5);
  }else if(moveDown){
    tiltServo.write(tiltServo.read() - 5);
  }
}

void setup() {
  //For debugging
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  Serial.setTimeout(50);

  //Attach our tilt servo to 7
  tiltServo.attach(7);

  //Attach our pan servo to 6
  panServo.attach(6);

  panServo.write(90);
  tiltServo.write(90);
}

void loop() {
  if(Serial.available() > 0){
    String data = Serial.readString();
    SetMovement(data);
    MoveServos();
    ResetMove();
  }
}
