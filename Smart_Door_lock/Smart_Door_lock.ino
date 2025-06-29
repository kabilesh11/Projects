#include <Keypad.h>
#include <EEPROM.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define RelayPin 11             // Pin controlling the relay

#define I2C_ADDR 0x27           // I2C address of the LCD

const byte numRows = 4;         // Number of rows on the keypad
const byte numCols = 4;         // Number of columns on the keypad

char keymap[numRows][numCols] = {
  {'1', '2', '3', 'A'}, 
  {'4', '5', '6', 'B'}, 
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

char code[] = {'6', '6', '0', '1'};  // The default code
char code_buff1[sizeof(code)];  // Buffer for new code
char code_buff2[sizeof(code)];  // Buffer for code confirmation

short a = 0, i = 0, s = 0, j = 0;  // Variables for code handling

byte rowPins[numRows] = {9, 8, 7, 6}; // Row pins for the keypad
byte colPins[numCols] = {5, 4, 3, 2}; // Column pins for the keypad

LiquidCrystal_I2C lcd(I2C_ADDR, 16, 2); // Initialize the LCD with I2C address and size
Keypad myKeypad = Keypad(makeKeymap(keymap), rowPins, colPins, numRows, numCols);

char keypressed; // Declare keypressed as a global variable

void setup() {
  lcd.init();
  lcd.clear();
  lcd.backlight(); // Turn on the backlight
  lcd.home();
  lcd.print("ENTER * KEY");

  pinMode(RelayPin, OUTPUT);
  
  
  // Uncomment this section to store the code in EEPROM on the first upload
  /*
  for (i = 0; i < sizeof(code); i++) {
    EEPROM.put(i, code[i]);
  }
  */
}

void loop() {
  keypressed = myKeypad.getKey(); // Check for keypress

  if (keypressed == '*') { // * to open the relay
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Enter Password");
    GetCode();
    if (a == sizeof(code)) {
      OpenRelay();
    } else {
      lcd.clear();
      lcd.print("Wrong");
    }
    delay(2000);
    lcd.clear();
    lcd.print("ENTER * KEY");
  }

  if (keypressed == '#') { // # to change the code
    ChangeCode();
    lcd.clear();
    lcd.print("ENTER * KEY");
  }
}

void GetCode() {
  i = 0;
  a = 0;
  j = 0;

  while (keypressed != 'A') { // User presses 'A' to confirm the code
    keypressed = myKeypad.getKey();
    if (keypressed != NO_KEY && keypressed != 'A') {
      lcd.setCursor(j, 1);
      lcd.print("*");
      j++;
      if (keypressed == code[i] && i < sizeof(code)) {
        a++;
        i++;
      } else {
        a--;
      }
    }
  }
  keypressed = NO_KEY;
}

void ChangeCode() {
  lcd.clear();
  lcd.print("Changing code");
  delay(1000);
  lcd.clear();
  lcd.print("Enter old code");
  GetCode();

  if (a == sizeof(code)) {
    lcd.clear();
    lcd.print("Changing code");
    GetNewCode1();
    GetNewCode2();
    s = 0;
    for (i = 0; i < sizeof(code); i++) {
      if (code_buff1[i] == code_buff2[i]) {
        s++;
      }
    }
    if (s == sizeof(code)) {
      for (i = 0; i < sizeof(code); i++) {
        code[i] = code_buff2[i];
        EEPROM.put(i, code[i]);
      }
      lcd.clear();
      lcd.print("Code Changed");
      delay(2000);
    } else {
      lcd.clear();
      lcd.print("Codes are not");
      lcd.setCursor(0, 1);
      lcd.print("matching !!");
      delay(2000);
    }
  } else {
    lcd.clear();
    lcd.print("Wrong");
    delay(2000);
  }
}

void GetNewCode1() {
  i = 0;
  j = 0;
  lcd.clear();
  lcd.print("Enter new code");
  lcd.setCursor(0, 1);
  lcd.print("and press A");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("and press A");

  while (keypressed != 'A') {
    keypressed = myKeypad.getKey();
    if (keypressed != NO_KEY && keypressed != 'A') {
      lcd.setCursor(j, 0);
      lcd.print("*");
      code_buff1[i] = keypressed;
      i++;
      j++;
    }
  }
  keypressed = NO_KEY;
}

void GetNewCode2() {
  i = 0;
  j = 0;
  lcd.clear();
  lcd.print("Confirm code");
  lcd.setCursor(0, 1);
  lcd.print("and press A");
  delay(3000);
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("and press A");

  while (keypressed != 'A') {
    keypressed = myKeypad.getKey();
    if (keypressed != NO_KEY && keypressed != 'A') {
      lcd.setCursor(j, 0);
      lcd.print("*");
      code_buff2[i] = keypressed;
      i++;
      j++;
    }
  }
  keypressed = NO_KEY;
}

void OpenRelay() {
  lcd.clear();
  lcd.print("Welcome");
  digitalWrite(RelayPin, LOW);
  delay(10000); // Keep the relay activated for 3 seconds
  digitalWrite(RelayPin, HIGH);
}
