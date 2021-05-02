void readbytes(int nbytes, char *buff);
void writeBytes(int nbytes, char *buff);

#define PLUG 1 //requerimento
#define STATUS 2
#define SET 3

int outputPinsArray[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, -1}; //2 ->13
char buff[250] = {0};
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i = 0; outputPinsArray[i] > 0 ; i++) {
    pinMode(outputPinsArray[i], OUTPUT);
  }
}

void loop() {
    char numBytes = 0 ;
    int i=0, j=2;
    
    readbytes(1,&numBytes);
    readbytes(numBytes,buff);
    switch(buff[0]){
        case PLUG:
          for( i = 0; outputPinsArray[i] > 0 ; i++){
             buff[i+2]=outputPinsArray[i];
            }
          i+=2;
          Serial.write((char) i); // cast
          buff[1]=1; // vetor de uma unica dimensao
          writeBytes(i,buff);
          break;
        case STATUS:
          j=2;
          for( i = 0; outputPinsArray[i] > 0 ; i++){
             buff[j]=outputPinsArray[i];
             j++;
             buff[j]=digitalRead(outputPinsArray[i]);
             j++;
            }
          Serial.write((char) j); // cast
          buff[1]=2; // vetor de duas dimensoes
          writeBytes(j,buff);
          break;
        case SET:
          digitalWrite(buff[1],buff[2]); // posicao 1 gpio, posicao 2 status
          break;
     }
}

void writeBytes(int nbytes, char *buff) {
  for (int i = 0; i < nbytes; i++) {
    Serial.write(buff[i]);
  }
}

void readbytes(int nbytes, char *buff) {
  if (nbytes < 0) return;
  while (Serial.available() < nbytes);
  for (int i = 0; i < nbytes; i++) {
    buff[i] = Serial.read();
  }
}
