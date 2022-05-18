from Cep2Model import Cep2Model
from Cep2WebClient import Cep2WebClient, Cep2WebDeviceEvent
from Cep2Zigbee2mqttClient import (Cep2Zigbee2mqttClient,
                                   Cep2Zigbee2mqttMessage, Cep2Zigbee2mqttMessageType)
import time
import http.client
import heucod
import json

class Cep2Controller:
    HTTP_HOST = "http://192.168.86.134:8085"
    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883
    timer = time.time()
    Kitchen_Light_State = 1 # Used to keep track of whether the kitchen light is on.

    stove_state = False
    time_sm = 0 # small timer, to keep track of if the user has been in the kitchen for 20 seconds.
    global_timer = 0 # Variable to keep track of how long no movement has been detected in the kitchen while the stove is on.
    idchain = 0 # Used to seperate the data in the database.
    Number_Of_Rooms = 1 # The number of rooms excluding the kitchen that have sensors.
    UserRoomState = 0
    temp = 0
    
    

    """ The controller is responsible for managing events received from zigbee2mqtt and handle them.
    By handle them it can be process, store and communicate with other parts of the system. In this
    case, the class listens for zigbee2mqtt events, processes them (turn on another Zigbee device)
    and send an event to a remote HTTP server.
    """

    def __init__(self, devices_model: Cep2Model) -> None:
        """ Class initializer. The actuator and monitor devices are loaded (filtered) only when the
        class is instantiated. If the database changes, this is not reflected.

        Args:
            devices_model (Cep2Model): the model that represents the data of this application
        """
        self.__devices_model = devices_model
        self.__z2m_client = Cep2Zigbee2mqttClient(host=self.MQTT_BROKER_HOST,
                                                  port=self.MQTT_BROKER_PORT,
                                                  on_message_clbk=self.__zigbee2mqtt_event_received)
        
        

        

    def start(self) -> None:
        """ Start listening for zigbee2mqtt events.
        """
        self.__z2m_client.connect()
        print(f"Zigbee2Mqtt is {self.__z2m_client.check_health()}")

    def stop(self) -> None:
        """ Stop listening for zigbee2mqtt events.
        """
        self.__z2m_client.disconnect()
        
    def TimerStart(self) -> None:
        """Updates the timer variable to the present time """
        self.timer = time.time()
        
    def TurnOffAllLights(self) -> None:
        i = 0 # Variable used to shift through all rooms.
        new_state = "OFF"
        while i <= self.Number_Of_Rooms: # Shift through the number of rooms in the house
            self.__z2m_client.change_state("Light_Room_"+str(i), new_state)
            i +=1
        self.LightOff(0)
        
    def StoveOn(self) -> bool: # Simply returns a boolean indicating if the stove is on or off
        return self.stove_state

    def LightOn(self, room_number) -> None:
        new_state = "ON"
        if room_number == 0:
            self.Kitchen_Light_State = 1
            self.__z2m_client.change_state("Kitchen_Light", new_state)
            #if self.UserRoomState == 0: # Used for testing purposes
            #    self.__z2m_client.change_color("Kitchen_Light",{"r":2,"g":5,"b":2})
        else:
            self.__z2m_client.change_state("Light_Room_"+str(room_number), new_state)
        
    def LightOff(self, room_number) -> None:
        new_state = "OFF"
        if room_number == 0: # If the room number is 0 indicating it is the kitchen, turn off the kitchen led
            self.Kitchen_Light_State = 0
            self.__z2m_client.change_state("Kitchen_Light", new_state)
        else: # Otherwise turn off the led in the room indicated by the room number
            self.__z2m_client.change_state("Light_Room_"+str(room_number), new_state)
    
    def StoveOff(self) -> None:
        self.stove_state = False # set the stove state to False, to indicate that the stove is off
        self.__z2m_client.change_state("Kitchen_Plug", "OFF") # Turn off the kitchen plug
        self.SendEvent("Stove Was Turned Off By Controller") # Send an event indicating this to the web API 
    
    
    def logic(self) -> None:
        if self.stove_state == False: # If the stove is off return
            return
        
        if self.temp != 0: # This is a failsafe used to handle the delay that sometimes comes with sending an event using HTTP
            self.TimerStart()
            self.temp = 0
            
        self.time_sm = time.time() - self.timer # The first timer
        self.global_timer = self.time_sm - 20 # The global timer
        """
        Used for testing purposes
        if round(self.global_timer) % 5 == 0 and self.global_timer >=0:
            print("User has left the kitchen for " + str(round(self.global_timer)) + " seconds.")
        """
        
        if self.time_sm > 20:
            if  self.global_timer < 1:
                self.SendEvent("User Has Left The Kitchen")
        """
        This part is for testing purposes
            if self.global_timer > 300 and self.Kitchen_Light_State != 1:
                self.LightOn(0)
            
        if self.global_timer < 300 and self.Kitchen_Light_State != 0:
            self.TurnOffAllLights()
        """    
        if self.global_timer > 1200: # If 20 minutes pass with no event recieved from the kitchen sensor with occupancy == true do the following
            self.TurnOffAllLights() # Turn off all alerting lights.
            self.LightOn(0) # Turn on the kitchen LED light.
            self.__z2m_client.change_color("Kitchen_Light",{"r":2,"g":0,"b":0}) # Make the light red to signify that the user left the stove on for more than 20 minutes.
            self.SendEvent("User Has Not Returned After 20 Minutes") # Send an event to the web API
            self.StoveOff() # Turn off the stove
        return
        
    def SendEvent(self, event) -> None:
            """
            This is for testing purposes
            print("Event("+event+") was sent to the database.")
            """
            # This is the code used to send a json package to the web API to store in the database.
            conn = http.client.HTTPConnection('kitchenguard.ddns.net')
            event_kitchen_occupancy = heucod.HeucodEvent()
            event_kitchen_occupancy.Timestamp = time.time()+7200
            event_kitchen_occupancy.Event = event
            event_kitchen_occupancy.IdChain = self.idchain
            data = event_kitchen_occupancy.to_json()              
            conn.request('POST', '/a.php', data)
           """
            This is for testing purposes
            r1 = conn.getresponse() 
            print(r1.status, r1.reason)
            while chunk := r1.read(200):
                print(repr(chunk))
           """
    def __zigbee2mqtt_event_received(self, message: Cep2Zigbee2mqttMessage) -> None:
        """ 
        Process an event received from zigbee2mqtt. This function given as callback to
        Cep2Zigbee2mqttClient, which is then called when a message from zigbee2mqtt is received.

        Args:
            message (Cep2Zigbee2mqttMessage): an object with the message received from zigbee2mqtt
        """
        # If message is None (it wasn't parsed), then don't do anything.
        if not message:
            return
        # This prints what event is recieved in the controllers terminal.
        #print(f"zigbee2mqtt event received on topic {message.topic}: {message.data}: {message.event}")
        
        # If the message is not a device event, then don't do anything.
        if message.type_ != Cep2Zigbee2mqttMessageType.DEVICE_EVENT:
            return
        
        # Parse the topic to retreive the device ID. If the topic only has one level, don't do anything.
        tokens = message.topic.split("/")
        if len(tokens) <= 1:
            return
        
        # Retrieve the device ID from the topic.
        device_id = tokens[1]

        device = self.__devices_model.find(device_id)
        
        if device:
            try:
                #This checks if the event recieved includes the variable power, as in is the event from the plug.
                power = message.event["power"]
                state = message.event["state"]
                #If the device is not the kitchen plug then ignore the event. We only use that one plug.
                if device_id != "Kitchen_Plug":
                    pass
            except KeyError:
                pass
            else:
                #If the plug is powering something as in the stove is on, check if it was off previously, if it was do the following.
                if power>0 and state == "ON":
                    if self.stove_state == False :
                        self.stove_state = True
                        self.TimerStart()
                        self.idchain += 1
                        self.SendEvent("Stove Turned On")
                else: # Otherwise if the stove is off
                    if self.stove_state == True: #check if it previously was on, if it was do the following.
                        self.SendEvent("Stove Was Manually Turned Off")
                        if self.global_timer < 1200:
                            self.LightOff(0)
                    self.stove_state = False 
            try:
                # Check if the event includes the variable occupancy, as in is it from a sensor.
                occupancy = message.event["occupancy"]
            except KeyError:
                pass
            else:
                # If there is movement
                if occupancy and self.stove_state:
                    #If it is from the kitchen
                    if device_id == "Kitchen_Sensor":
                        if self.time_sm > 20 and self.temp == 0:
                            self.temp = 1 # Used to handle HTTP delay
                            self.SendEvent("User Returned To The Kitchen")
                        self.TimerStart() # Resets the timer
                        self.UserRoomState = 0 # Used to indicate that the user is in the kitchen
                        #self.__z2m_client.change_color("Kitchen_Light",{"r":2,"g":5,"b":2}) # Used for testing purposes

                    elif device_id != "Kitchen_Sensor": # If not from the kitchen
                        if self.global_timer > 300: # and 5 minutes have passed
                            i = 1 # used to keep track of the rooms
                            while i <= self.Number_Of_Rooms: # Check which room the movement occured in
                                if "Sensor_Room_"+str(i) == device_id and self.UserRoomState == 0:
                                    #self.LightOn(i)
                                    #When the user enters another room the kitchen light will change colour. This is because we only have one light.
                                    #self.TurnOffAllLights()
                                    self.UserRoomState = 1
                                    self.LightOn(0)
                                    self.__z2m_client.change_color("Kitchen_Light",{"r":i+2 ,"g":i,"b":i+1})
                                    self.SendEvent("User is in Room "+str(i))
                                i+=1
                
