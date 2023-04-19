#include "Motori.h"

Motori::Motori(int d1, int d2, int d3, int d4)
{
    this->d1=d1;
    this->d2=d2;
    this->d3=d3;
    this->d4=d4;

    pinMode(d1, OUTPUT);
    pinMode(d2, OUTPUT);
    pinMode(d3, OUTPUT);
    pinMode(d4, OUTPUT);

}


void Motori::avanti()
{
    digitalWrite(d1, HIGH);
    digitalWrite(d2, LOW);
    analogWrite(d3, 127);
    analogWrite(d4, 0);
}
    
void Motori::indietro()
{
    digitalWrite(d1, LOW);
    digitalWrite(d2, HIGH);
    analogWrite(d3, 0);
    analogWrite(d4, 127);
}
    
void Motori::destra()
{
    digitalWrite(d1, LOW);
    digitalWrite(d2, HIGH);
    analogWrite(d3, 127);
    analogWrite(d4, 0);

}

void Motori::sinistra()
{

    digitalWrite(d1, HIGH);
    digitalWrite(d2, LOW);
    analogWrite(d3, 0);
    analogWrite(d4, 127);

}
 
void Motori::fermo()
{
    digitalWrite(d1, LOW);
    digitalWrite(d2, LOW);
    analogWrite(d3, 0);
    analogWrite(d4, 0);
}
