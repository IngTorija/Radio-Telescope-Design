import wx
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np                                                              #Importar librería de cálculos matemáticos
import serial                                                                   #Importar librería para comunicación serial
import time                                                                     #Importar librería para


class TopPanel(wx.Panel):                                                       #TopPanel hereda los métodos de wx.Panel
    def __init__(self,parent):                                                  #Método constructor: inicializa atributos, se ejecuta al crear el objeto
        wx.Panel.__init__(self,parent = parent)                                 #Método constructor de la clase padre (wx.Panel)(preguntar a alguien)
        self.figure = Figure()                                                  #Crea el objeto Figura (solo dentro de la clase)
        self.axes = self.figure.add_subplot(111)                                #Crea los ejes coordenados de la figura dentro de la ventana en la fila 1, columna 1, subplot 1 =  Add_subplot(111)
        self.canvas = FigureCanvas(self,-1,self.figure)                         #FigureCanvas contiene figure (de matplotlib) y crea una figura de WXpython
        self.sizer = wx.BoxSizer(wx.VERTICAL)                                   #Crea un sizer que acopla la figura al tamaño de la ventana
        self.sizer.Add(self.canvas,1,wx.EXPAND)                                 #Agrega Canvas al sizer
        self.SetSizer(self.sizer)                                               #utiliza el Sizer para acoplar la figura Canvas al tamaño de la ventana
        self.axes.set_xlabel('Tiempo(s)-->')
        self.axes.set_ylabel('Amplitud(V)-->')

    def draw(self,x,y,time_unit):                                                         #Método para dibujar el gráfico
        self.axes.clear()                                                       #Límpia los ejes coordenados
        self.axes.plot(x,y,'r')                                                 #grafica 'x' vs 'y'
        self.axes.set_ylabel('Amplitud(V)-->')
        if time_unit =="min":
            self.axes.set_xlabel('Tiempo (seg)--->')
        elif time_unit == "hrs":
            self.axes.set_xlabel('Tiempo (min)--->')
        else:
            self.axes.set_xlabel('Tiempo (seg)--->')
        self.canvas.draw()                                                      #Redibuja la figura canvas

    def changeAxes(self,min,max):                                               #Método para cambiar el rango de Y
        self.axes.set_ylim(float(min),float(max))                               #Estable los límites de Y
        self.canvas.draw()                                                      #Redibuja la figuraCanvas

class ButtomPanel(wx.Panel):                                                    #ButtonPanel hereda los métodos de wx.Panel
    def __init__(self,parent,top):                                              #Método constructor: inicializa atributos, se ejecuta al crear el objeto e incluye top dentro de sus parámetros
        wx.Panel.__init__(self,parent = parent)                                 #Método constructor de la clase padre (wx.Panel)(preguntar a alguien)
        self.graph = top                                                        #crea el objeto graph que es una referencia al objeto top
        self.togglebuttonStart = wx.ToggleButton(self,
        id=-1,label = "¡Monitorear!", pos = (325,60))                                #Crea un botón de conmutación
        self.togglebuttonStart.Bind(wx.EVT_TOGGLEBUTTON, self.OnStartClick)     #Lee el evento del botón de conmutación y nos manda al método OnStartClick
        wx.StaticText(self,-1, "Tiempo de visualización", pos = (170,10))       #caja de texto estático
        self.cb3 = wx.CheckBox(self, -1, label = "Minutos",pos = (170,55))      #Caja para checar A3
        self.cb4 = wx.CheckBox(self, -1, label = "Horas",pos = (170,70))        #Caja para checar A4
        self.Bind(wx.EVT_CHECKBOX, self.OnChecked)                              #Lee el evento de todas las cajas para checar y nos manda al método OnChecked
        self.textboxSampleTime = wx.TextCtrl(self, -1,"30",                     #Entrada de texto
        pos = (170,30), size =(50,-1))
        self.image=wx.StaticBitmap(self,-1, wx.Bitmap("antena.png")
        ,pos = (450,0),size=(170,170))
        self.textboxPortCOM = wx.TextCtrl(self, -1,"COM3",                      #Entrada de texto para puerto COM
        pos = (325,30), size =(50,-1))
        self.label_portCOM = wx.StaticText(self, -1, "Introducir puerto COM",
        pos = (325,10), size = (150,-1))
        self.textboxWarning = wx.StaticText(self,-1," ",
        pos = (170,110))
        wx.StaticText(self, -1, "Valor mínimo de Y", pos =(10,10))                  #Caja de texto
        self.textboxMinYAxis = wx.TextCtrl(self, -1, "0", pos = (10,30))        #Entrada de texto para configurar valor mínimo de Y
        wx.StaticText(self, -1, "Valor máximo de Y", pos =(10,60))              #Caja de texto
        self.textboxMaxYAxis = wx.TextCtrl(self, -1, "255", pos = (10,80))      #Entrada de texto para configurar valor máximo de Y
        self.buttonRange = wx.Button(self,-1,"Establecer eje Y",pos = (10,105)) #Botón para enviar valores mínimos y máximos
        self.buttonRange.Bind(wx.EVT_BUTTON, self.SetButtonRange)               #Lee evento del botón de valores min y max del eje Y
        self.timer = wx.Timer(self)                                             #Se crea el objeto timer, temporizador para controlar la velocidad de adquisición de datos
        self.Bind(wx.EVT_TIMER, self.TimeInterval, self.timer)                  #
        self.serial_connection = False                                          # se crea variable para saber el estado de la conexión serial
        self.x = np.array([])                                                   #Arreglo del eje x vacío
        self.y = np.array([])                                                   #Arreglo del eje y vacío
        self.x_counter =0                                                       #Contador para el eje x
        self.time_unit = "null"
        
    def SetButtonRange(self,event):                                             # Método para establecer rango de Y
        min = self.textboxMinYAxis.GetValue()                                   #Obtiene valores mínimo de Y
        max = self.textboxMaxYAxis.GetValue()                                   #Obtiene valores máximo de Y
        self.graph.changeAxes(min,max)                                          #Llama al método changeAxes que está en la clase TopPanel


    def OnChecked(self,event):                                                  #Método para obtener la casilla que está presionada
        minut = self.cb3.GetValue()
        hrs = self.cb4.GetValue()
        val = self.togglebuttonStart.GetValue()
        if val == False:  
            if hrs ==False and minut ==True:
                self.cb4.SetValue(False)
                self.time_unit = "min"
            elif hrs == True and minut ==False:
                self.cb3.SetValue(False)
                self.time_unit = "hrs"
            elif hrs ==False and minut ==False:
                self.cb3.SetValue(False)
                self.cb4.SetValue(False)
                self.time_unit = "null"
            elif hrs == True and miut == True:
                self.cb3.SetValue(False)
                self.cb4.SetValue(False)
                self.time_unit = "null"
            else:
                self.cb3.SetValue(False)
                self.cb4.SetValue(False)
                self.time_unit = "null"
        else:
            self.textboxWarning.SetLabel("Monitoreando...")
            

    def TimeInterval(self,event):                                               #Método para definir la velocidad de muestreo de los datos
        if self.time_unit == "null": 
            
            if self.x_counter<130:
                self.serial_device.write("a".encode())                                   #Se envía el caracter al dispositivo serial
                tmp = self.serial_device.read()                                        #Se lee el dato que regresa el dispositivo
                self.y = np.append(self.y,int.from_bytes(tmp,"big") )                                     #Se agrega el valor al eje coordenado y
                self.x = np.append(self.x,float(self.x_counter*0.8))                               #Se agrega el valor de x_counter al eje coordenado x
                self.x_counter +=1                                                      #Se aumenta el valor de x_counter                
                self.textboxWarning.SetLabel("Recibiendo datos...")
                self.graph.draw(self.x,self.y,self.time_unit)
            else:    
                self.serial_device.write("a".encode())                                   #Se envía el caracter al dispositivo serial
                tmp = self.serial_device.read()                                        #Se lee el dato que regresa el dispositivo
                self.y = np.delete(self.y,0)                                            #Se remueve el 1° valor al eje coordenado y
                self.x = np.delete(self.x,0)                                            #Se remueve el 1°valor de x_counter al eje coordenado x
                self.y = np.append(self.y,int.from_bytes(tmp,"big"))                                     #Se agrega el valor al eje coordenado y
                self.x = np.append(self.x,self.x_counter)                               #Se agrega el valor de x_counter al eje coordenado x
                self.x_counter +=1                                                      #Se aumenta el valor de x_counter                
                self.textboxWarning.SetLabel("Recibiendo datos...")
                self.graph.draw(self.x,self.y,self.time_unit)                                          #Se llama al método draw con los argumentos: x_counter y serial_device.readline()
                                                
        elif self.time_unit == "min":
            if self.x_counter<= 1200:
                self.serial_device.write("a".encode())                                   #Se envía el caracter a al dispositivo serial
                tmp = self.serial_device.read()                                        #Se lee el dato que regresa el dispositivo
                self.y = np.append(self.y,int.from_bytes(tmp,"big"))                                     #Se agrega el valor al eje coordenado y
                self.x = np.append(self.x,float(self.x_counter*self.muestreo/1000))                               #Se agrega el valor de x_counter al eje coordenado x
                self.x_counter +=1                                                      #Se aumenta el valor de x_counter                
                self.graph.draw(self.x,self.y,self.time_unit)                                          #Se llama al método draw con los argumentos: x_counter y serial_device.readline()
                self.textboxWarning.SetLabel("Monitoreo en proceso...")
            else:
                self.timer.Stop()
                self.textboxWarning.SetLabel("Monitoreo Finalizado")
                self.togglebuttonStart.SetValue(False)
                self.togglebuttonStart.SetLabel("¡Monitorear!")

        elif self.time_unit == "hrs":
            if self.x_counter<= 3600:
                self.serial_device.write("a".encode())                                   #Se envía el caracter a al dispositivo serial
                tmp = self.serial_device.read()                                        #Se lee el dato que regresa el dispositivo
                self.y = np.append(self.y,int.from_bytes(tmp,"big"))                                     #Se agrega el valor al eje coordenado y
                self.x = np.append(self.x,float(self.x_counter*self.muestreo/1000))                               #Se agrega el valor de x_counter al eje coordenado x
                self.x_counter +=1                                                      #Se aumenta el valor de x_counter                
                self.graph.draw(self.x,self.y,self.time_unit)                                          #Se llama al método draw con los argumentos: x_counter y serial_device.readline()
                self.textboxWarning.SetLabel("Monitoreo en proceso...")
            else:
                self.timer.Stop()
                self.textboxWarning.SetLabel("Monitoreo Finalizado")
                self.togglebuttonStart.SetValue(False)
                self.togglebuttonStart.SetLabel("¡Monitorear!")


    def OnStartClick(self,event):                                               #Método para iniciar la comunicacione entre dispositivo y la GUI
        self.text_tiempo=self.textboxSampleTime.GetValue()
        self.text_puerto=self.textboxPortCOM.GetValue()
        self.btn_min = self.cb3.GetValue()
        self.btn_hras = self.cb4.GetValue()
        self.test = (self.btn_min | self.btn_hras)
        
        if self.test:
            if int(self.text_tiempo) < 1 & int(self.text_tiempo) >60:
                self.textboxWarning.SetLabel("Error en rango de tiempo")
                self.togglebuttonStart.SetLabel("¡Monitorear!")                          #Conmuta el label del botón a "¡Monitorear!"
                self.togglebuttonStart.SetValue(False)
                self.timer.Stop()

        val = self.togglebuttonStart.GetValue()                                 #Obtenemos el estado del botón de conmutación
        
        if val ==True:                                                        #Condición si es verdadadero
            self.togglebuttonStart.SetLabel("Detener")                          #Conmuta el label de botón a "Detener"
            self.x = []                                                             #Arreglo del eje x vacío
            self.y = []
            self.x_counter = 0    
            if self.time_unit == "null":    
                self.muestreo= 1
                self.timer.Start(self.muestreo)                                 #Toma datos cada milisegundo
                self.serial_connection = False
            
            elif self.time_unit == "min":
                self.muestreo = 50*int(self.textboxSampleTime.GetValue())-7
                self.timer.Start(self.muestreo)
                self.serial_connection = False
            
            elif self.time_unit == "hrs":
                self.muestreo=1000*int(self.textboxSampleTime.GetValue())
                self.timer.Start(self.muestreo)
                self.serial_connection = False
            
            else:
                self.muestreo = 1
                self.timer.Start(self.muestreo)
        else:
            self.togglebuttonStart.SetLabel("¡Monitorear!")                          #Conmuta el label del botón a "¡Monitorear!"
            self.togglebuttonStart.SetValue(False)
            self.timer.Stop()
        
        if self.serial_connection == False:
            try:
                self.portCOM = self.textboxPortCOM.GetValue()                   #Se obtiene el valor del puerto COM
                self.serial_device = serial.Serial(self.portCOM,9600,timeout=2,)
                time.sleep(2)
                self.data = b"i"                                                # pasar la cadena "i" a tipo byte
                self.serial_device.write(self.data)                                #Envía el caracter "i" para iniciar comunicación
                res = self.serial_device.readline()                                #Lee el dato enviado por el dispositivo serial
                if res ==b"Starting\n":                                       #Si el dispositivo envía "Starting\n" se inicia comunicación sino se marca error
                    self.textboxWarning.SetLabel("El dispositivo está listo...")
                    self.serial_connection = True
            except serial.serialutil.SerialException:
                self.textboxWarning.SetLabel("Problema conectando dispositivo...")

class Main(wx.Frame):                                                           #Clase principal, hereda sus atributos de wx.Frame
    def __init__(self):                                                         #Método constructor se ejecuta al crear el objeto
        wx.Frame.__init__(self, parent = None,                                  #Método constructor de la clase padre (wx.Frame)(preguntar a alguien)
        title = "FCE-BUAP/RadioTelescopio", size = (650,700))
        splitter = wx.SplitterWindow(self)                                      #Crea un objeto con dos ventanas
        top = TopPanel(splitter)                                                #Ventana de arriba (gráfica)
        buttom = ButtomPanel(splitter,top)                                      #Ventana de abajo (botones) hace referencia al objeto top
        splitter.SplitHorizontally(top,buttom)                                  #agrupa las ventanas horizontalmente
        splitter.SetMinimumPaneSize(500)                                        #tamaño mínimo de la ventana de arriba
        #top.draw(0,0)                                                           #llama al método draw (dibujar la gráfica)
        icono = wx.Icon("astronave.png")
        self.SetIcon(icono)


if __name__ == "__main__":
    app = wx.App()                                                              #Arranca la interfaz gráfica
    frame = Main()                                                              #Crea el objeto frame de tipo Main
    frame.Show()                                                                #Muestra el frame Main
    app.MainLoop()                                                              #Ejecuta la interfaz gráfica
