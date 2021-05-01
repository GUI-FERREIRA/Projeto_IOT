void readbytes(int nbytes, char *buff);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("Ok\n");
}

void loop() {
  char command = 0;
  readbytes(1, &command);
  Serial.write((char)-1);
 
}
void writeBytes(int nbytes, char *buff){
  for (int i = 0; i < nbytes; i++) {
    Serial.read(buff[i]);
  }
}
void readbytes(int nbytes, char *buff) {
  if (nbytes < 0) return;
  while (Serial.available() < nbytes);
  for (int i = 0; i < nbytes; i++) {
    buff[i] = Serial.read();
  }
}
