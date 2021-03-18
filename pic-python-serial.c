unsigned int temp_res;
char error,dato,lectura;
short serial_connection = 0;           //Serial_connection = false
short tshort;
void main() {
  ADCON1 = 0B00001110;           // Voltaje de referencia para la conversión A/D es VCC
                                 // PA0 se define como entrada analógica
  
  TRISA  = 0xFF;              // PORTA is input
  TRISB  = 0x00;                 // PORTB is output
  ADC_Init();
  error=Soft_UART_Init(&PORTC, 7, 6, 9600, 0); // Configura el puerto serial
  PORTB = 0B11110000;
     while(1){
     dato=Soft_UART_Read(&error);
     temp_res = ADC_Read(0);
     lectura = temp_res/4;
     PORTB = lectura;
     if(dato == 105 && serial_connection ==0)
     {
     Soft_UART_Write('S');
     Soft_UART_Write('t');
     Soft_UART_Write('a');
     Soft_UART_Write('r');
     Soft_UART_Write('t');
     Soft_UART_Write('i');
     Soft_UART_Write('n');
     Soft_UART_Write('g');
     Soft_UART_Write('\n');
     serial_connection = 1;
     }
     else if(dato == 97 && serial_connection == 1)
     {
     Soft_UART_Write(lectura);
     }

     }

} 