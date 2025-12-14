#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

String msg = "";

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);

  lcd.setCursor(0, 0);
  lcd.print("Animal Monitor");
  lcd.setCursor(0, 1);
  lcd.print("System Ready...");
  delay(2000);
  lcd.clear();
}

void loop() {

  // Check if any message is coming
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      msg.trim();
      handleMessage(msg);
      msg = ""; 
    } 
    else {
      msg += c;
    }
  }
}

void handleMessage(String m) {

  lcd.clear();

  if (m == "NONE") {
    lcd.setCursor(0, 0);
    lcd.print("No Animal");
    lcd.setCursor(0, 1);
    lcd.print("Detected");
    return;
  }

  // If any animal detected (general case)
  lcd.setCursor(0, 0);
  lcd.print("Animal Detected");
  lcd.setCursor(0, 1);
  lcd.print("Species: ");
  lcd.print(m);
}