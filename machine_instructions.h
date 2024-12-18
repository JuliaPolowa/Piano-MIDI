#ifndef MACHINE_INSTRUCTIONS_H
#define MACHINE_INSTRUCTIONS_H

typedef enum {
    CMD_WAIT,
    CMD_MOVE_HAND,
    CMD_PRESS_FINGER,
    CMD_UNPRESS_FINGER
} CommandType;

typedef struct {
    CommandType type;
    int which_hand;  // 0 for left, 1 for right (ignored for CMD_WAIT)
    int param;       // key number, finger number, or wait duration
} Command;

const Command commands[] = {
    { CMD_MOVE_HAND, 1, 1 },
    { CMD_PRESS_FINGER, 1, 1 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 1, 1 },
    { CMD_PRESS_FINGER, 1, 2 },
    { CMD_WAIT, -1, 200 },
    { CMD_MOVE_HAND, 0, 8 },
    { CMD_PRESS_FINGER, 0, 1 },
    { CMD_UNPRESS_FINGER, 1, 2 },
    { CMD_PRESS_FINGER, 1, 3 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 0, 1 },
    { CMD_PRESS_FINGER, 0, 2 },
    { CMD_UNPRESS_FINGER, 1, 3 },
    { CMD_PRESS_FINGER, 1, 4 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 0, 2 },
    { CMD_PRESS_FINGER, 0, 3 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 0, 3 },
    { CMD_PRESS_FINGER, 0, 4 },
    { CMD_UNPRESS_FINGER, 1, 4 },
    { CMD_WAIT, -1, 400 },
    { CMD_UNPRESS_FINGER, 0, 4 },
    { CMD_PRESS_FINGER, 0, 5 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 0, 5 },
    { CMD_MOVE_HAND, 0, 13 },
    { CMD_PRESS_FINGER, 0, 1 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 0, 1 },
    { CMD_PRESS_FINGER, 0, 2 },
    { CMD_WAIT, -1, 200 },
    { CMD_UNPRESS_FINGER, 0, 2 },
};

const int numCommands = sizeof(commands) / sizeof(commands[0]);

#endif
