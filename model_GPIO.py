
class ModelGPIO:
    BCM = OUT = IN = HIGH = LOW = None
    def setmode(self, *args): print("ModelGPIO: setmode")
    def setup(self, *args): print("ModelGPIO: setup", args)
    def PWM(self, *args): 
        print("ModelGPIO: create PWM", args) 
        class FakePWM:
            def start(self, duty): print("FakePWM: start", duty)
            def ChangeDutyCycle(self, duty): print("FakePWM: duty =  ", duty)
            def stop(self): print("FakePWM: stop")
        return FakePWM()
    def output(self, *args): print("ModelGPIO: output", args)
    def cleanup(self): print("ModelGPIO: cleanup")
   
GPIO = ModelGPIO()