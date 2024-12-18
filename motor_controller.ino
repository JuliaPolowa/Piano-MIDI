#include <Servo.h>
#include "machine_instructions.h"

// Constants Definitions
#define STEPS_PER_ROTATION 200
#define STEPS_PER_KEY 118
#define NUM_WHITE_KEYS 52

// Assign pins
#define LEFT_DIR_PIN 33
#define LEFT_STEP_PIN 31
#define RIGHT_DIR_PIN 43
#define RIGHT_STEP_PIN 41

#define LEFT_LIMIT_PIN 23
#define RIGHT_LIMIT_PIN 25

const int left_servo_pins[5] = {12, 11, 10, 9, 8};
const int right_servo_pins[5] = {3, 4, 5, 6, 7};

// Servo Objects
Servo left_fingers[5];
Servo right_fingers[5];

// Servo Positions
const int SERVO_MIN_ANGLE = 90;   // Unpressed
const int SERVO_MAX_ANGLE = 110;  // Pressed

// Hand Positions
int left_current_key = 0;
int right_current_key = 0;

// Function Prototypes
void move_hand(int which_hand, int to_key);
void press_finger(int which_hand, int finger);
void unpress_finger(int which_hand, int finger);
void reset_left_hand();
void reset_right_hand();
bool is_left_limit_triggered();
bool is_right_limit_triggered();

bool is_left_limit_triggered() {
    if(digitalRead(LEFT_LIMIT_PIN) == LOW) {
        delay(50);
        return (digitalRead(LEFT_LIMIT_PIN) == LOW);
    }
    return false;
}

bool is_right_limit_triggered() {
    if(digitalRead(RIGHT_LIMIT_PIN) == LOW) {
        delay(50);
        return (digitalRead(RIGHT_LIMIT_PIN) == LOW);
    }
    return false;
}

void press_finger(int which_hand, int finger) {
    if(finger < 1 || finger > 5) {
        Serial.println("Invalid Finger Number");
        return;
    }
    
    if(which_hand == 0) { 
        left_fingers[finger - 1].write(SERVO_MAX_ANGLE);
        Serial.print("Pressed Left Finger ");
        Serial.println(finger);
    } else { 
        right_fingers[finger - 1].write(SERVO_MAX_ANGLE);
        Serial.print("Pressed Right Finger ");
        Serial.println(finger);
    }
}


void unpress_finger(int which_hand, int finger) {
    if(finger < 1 || finger > 5) {
        Serial.println("Invalid Finger Number");
        return;
    }
    
    if(which_hand == 0) { 
        left_fingers[finger - 1].write(SERVO_MIN_ANGLE);
        Serial.print("Unpressed Left Finger ");
        Serial.println(finger);
    } else { 
        right_fingers[finger - 1].write(SERVO_MIN_ANGLE);
        Serial.print("Unpressed Right Finger ");
        Serial.println(finger);
    }
}

void reset_left_hand() {
    Serial.println("Resetting Left Hand to Key 1");
    digitalWrite(LEFT_DIR_PIN, LOW);    
    
    while(!is_left_limit_triggered()) { 
        digitalWrite(LEFT_STEP_PIN, HIGH);
        delayMiliseconds(5); 
        digitalWrite(LEFT_STEP_PIN, LOW);
        delayMiliseconds(5);
    }
    
    left_current_key = 1;
    
    Serial.println("Left Hand reset to Key 1");
}


void reset_right_hand() {
    Serial.println("Resetting Right Hand to Last Key");    
    
    digitalWrite(RIGHT_DIR_PIN, HIGH);
    
    while(!is_right_limit_triggered()) { 
        digitalWrite(RIGHT_STEP_PIN, HIGH);
        delayMiliseconds(5); 
        digitalWrite(RIGHT_STEP_PIN, LOW);
        delayMiliseconds(5);
    }
    
    right_current_key = NUM_WHITE_KEYS - 4;
    Serial.println("Right Hand reset to Last Key");
}


void move_hand(int which_hand, int to_key) {
    int steps_needed = STEPS_PER_KEY * (to_key - ((which_hand == 0) ? left_current_key : right_current_key));
    bool clockwise;
    
    if(which_hand == 0) { 
        clockwise = steps_needed > 0;
    } else { 
        clockwise = steps_needed < 0; 
    }
    
    int steps = abs(steps_needed);
    
    if(which_hand == 0) {
        digitalWrite(LEFT_DIR_PIN, clockwise ? HIGH : LOW);
        
        for(int i = 0; i < steps; i++) {
            digitalWrite(LEFT_STEP_PIN, HIGH);
            delayMicroseconds(800); 
            digitalWrite(LEFT_STEP_PIN, LOW);
            delayMicroseconds(800);
            
            if(is_left_limit_triggered()) { 
                Serial.println("Left Hand limit switch triggered during movement");
                reset_left_hand();
                break; 
            }
        }
        
        left_current_key = to_key;
        Serial.print("Moved Left Hand to Key ");
        Serial.println(to_key);
    } else {   
        digitalWrite(RIGHT_DIR_PIN, clockwise ? HIGH : LOW);
        
        for(int i = 0; i < steps; i++) {
            digitalWrite(RIGHT_STEP_PIN, HIGH);
            delayMicroseconds(800); 
            digitalWrite(RIGHT_STEP_PIN, LOW);
            delayMicroseconds(800);
            
            if(is_right_limit_triggered()) { 
                Serial.println("Right Hand limit switch triggered during movement");
                reset_right_hand();
                break; 
            }
        }
        
        right_current_key = to_key;
        Serial.print("Moved Right Hand to Key ");
        Serial.println(to_key);
    }
}

void setup() {
    Serial.begin(9600);
    
    pinMode(LEFT_STEP_PIN, OUTPUT);
    pinMode(LEFT_DIR_PIN, OUTPUT);
    pinMode(RIGHT_STEP_PIN, OUTPUT);
    pinMode(RIGHT_DIR_PIN, OUTPUT);
    
    pinMode(LEFT_LIMIT_PIN, INPUT_PULLUP);
    pinMode(RIGHT_LIMIT_PIN, INPUT_PULLUP);
    
    for(int i = 0; i < 5; i++) {
        left_fingers[i].attach(left_servo_pins[i]);
        right_fingers[i].attach(right_servo_pins[i]);
        left_fingers[i].write(SERVO_MIN_ANGLE);   
        right_fingers[i].write(SERVO_MIN_ANGLE);  
    }
    
    for(int i = 0; i < numCommands; i++) {
        Command cmd = commands[i];
        switch(cmd.type) {
            case CMD_WAIT:
                Serial.print("Waiting for ");
                Serial.print(cmd.param);
                Serial.println(" ms");
                delay(cmd.param);
                break;
                
            case CMD_MOVE_HAND:
                move_hand(cmd.which_hand, cmd.param);
                break;
                
            case CMD_PRESS_FINGER:
                press_finger(cmd.which_hand, cmd.param);
                break;
                
            case CMD_UNPRESS_FINGER:
                unpress_finger(cmd.which_hand, cmd.param);
                break;
                
            default:
                Serial.println("Unknown Command");
                break;
        }
    }
}