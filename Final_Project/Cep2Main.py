from time import sleep
from Cep2Controller import Cep2Controller
from Cep2Model import Cep2Model, Cep2ZigbeeDevice


if __name__ == "__main__":
    # Create a data model and add a list of known Zigbee devices.
    devices_model = Cep2Model()
    devices_model.add([Cep2ZigbeeDevice("Kitchen_Sensor", "pir"),
                       Cep2ZigbeeDevice("Kitchen_Light", "led"),
                       Cep2ZigbeeDevice("Kitchen_Plug", "power plug"),
                       Cep2ZigbeeDevice("Sensor_Room_1", "pir")
                       # The following sensors would be connected, however we only managed to connect 1 additional sensor
                       #Cep2ZigbeeDevice("Sensor_Room_2", "pir") 
                       #Cep2ZigbeeDevice("Sensor_Room_3", "pir")
                       #Cep2ZigbeeDevice("Sensor_Room_4", "pir")
                       #Cep2ZigbeeDevice("Sensor_Room_5", "pir")
                       
                       # The following LEDs would be connected, however we did not manage to add any additional lights
                       #Cep2ZigbeeDevice("Light_Room_1", "led")
                       #Cep2ZigbeeDevice("Light_Room_2", "led")
                       #Cep2ZigbeeDevice("Light_Room_3", "led")
                       #Cep2ZigbeeDevice("Light_Room_4", "led")
                       #Cep2ZigbeeDevice("Light_Room_5", "led")
                      ])

    # Create a controller and give it the data model that was instantiated.
    controller = Cep2Controller(devices_model)
    controller.start()

    print("Waiting for events...")

    while True:
        sleep(1)
        controller.logic()

    controller.stop()
