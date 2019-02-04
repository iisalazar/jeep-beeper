import RPi.GPIO as GPIO
import MFRC522
import signal
import sys

# a library for converting data to hex
import struct

class BaseReader(object):

    def __init__(self):

        self.MFReader = MFRC522.MFRC522()
        self.key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        signal.signal(signal.SIGINT, self.end_read)
        self.authenticated = False

    # A method to clean-up GPIO
    # once reading is finished
    def end_read(self):
        "Ending reading..."
        "Cleaning GPIO"
        self.MFReader.MFRC522_StopCrypto1()
        GPIO.cleanup()

    # A method for scanning a card
    def scan_card(self):
        print("Scanning for a card...")
        (status, TagType) = self.MFReader.MFRC522_Request(self.MFReader.PICC_REQIDL)
        if status == self.MFReader.MI_OK:
            print("Card detected")
            return True
        return None


    # A method for getting the UID of a card
    # Returns UID if grabbed else None
    def get_uid(self):
        (status, uid) = self.MFReader.MFRC522_Anticoll()
        if status == self.MFReader.MI_OK:
            print("Grabbed UID of card")
            self.uid = uid
            return {"uid": uid}
        return None

    # A method to authenticate
    # NOTE: must be called first before
    # Calling the methods below


    # TODO: Change this method to a decorator

    def authenticate(self):
        print("Authenticating")
        if not self.authenticated:
            self.MFReader.MFRC522_SelectTag(self.uid)
            status = self.MFReader.MFRC522_Auth(self.MFReader.PICC_AUTHENT1A, 8, self.key, self.uid)
            if status == self.MFReader.MI_OK:
                print("Authenticated")
                self.authenticated = True
                return
        return "Error! Already authenticated"
    '''
    def authenticate(self, func):
        print("Authenticating...")
        def auth_or_raise(*args, **kwargs):
            self.MFReader.MFRC522_SelectTag(self.uid)
        status = self.MFReader.MFRC522_Auth(self.MFReader.PICC_AUTHENTI1A, 8, self.key, self.uid)
            if not status == self.MFReader.MI_OK:
                print("Errors occured")
                raise Exception("Authentication error")
            print("Authenticated")
            return func(*args, **kwargs)
        # IF no errors occur, 
        # Proceed with function
        return auth_or_raise
    '''
    # A method to get a sector block
    # Takes in a number ranging 1 to 20

    def read_sector(self, sector):
        if not self.authenticated:
            self.authenticate()
        try:
            block = self.MFReader.MFRC522_Read(sector)
            return {
                "sector" : sector,
                "block" : block
                }
        except:
            return None


    def write_sector(self, sector, amount):
        if not self.authenticated:
            self.authenticate()
        try:
            d = self.data_to_hexBits(amount)
            print("Writing data {} to sector {}".format(d, sector))
            self.MFReader.MFRC522_Write(sector, d)
            block = self.read_sector(sector)['block']
            return {"block": block}
        except:
            return None

    def clear_sector(self, sector):
        if not self.authenticated:
            self.authenticate()
        try:
            data = []
            for i in range(0, 16):
                data.append(0x00)
            print("Clearing data for sector {}".format(sector))
            self.MFReader.MFRC522_Write(sector, data)
            block = self.read_sector(sector)['block']
            return {"block": block}
        except:
            return None

    # Sorry for the name
    # This function is called to get the desired data to write in the sector
    # Returns a list 
    def data_to_hexBits(self, amount):
        try:
            if self.check_for_negative(amount):
                new_data = self.data_to_list(amount)
                return new_data
        except:
            print("Error in parsing data")

    # This method is called to sanitize input against negative values
    def check_for_negative(self, amount):
        if not amount > 0:
            raise Exception("Amount should not be in negative value")
        return True

    # Convert the given amount to a list of numbers...
    # Example: 257 will be converted to [0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,2]
    def data_to_list(self, amount):
        extra = amount % 255
        counts = amount / 255
        new_data = []
        for i in range(counts):
            new_data.append(255)
        new_data.append(extra)

        range_ = len(new_data)
        for i in range(0, 16 - range_):
            new_data.insert(0, 0)

        return new_data
'''
        Data Representation
        each block is either 0 or 255
        Meaning, a block is either 0 or 1
        and we can compute 
          1      1      1    1      1    1      1    1      1    1      1    1      1    1      1    1 = 2^16 = 65536      
        [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,]
'''
    

if __name__ == '__main__':
    reader = BaseReader()
    signal.signal(signal.SIGINT, reader.end_read)
    while not reader.scan_card():
        reader.scan_card()
    uid = reader.get_uid()
    print(uid)
    block = reader.write_sector(sector=8, amount=257)
    print(block)
    '''
    data = reader.write_sector(sector=8, data=257)
    print(data)
    '''
    '''
    while not reader.get_uid():
        reader.get_uid()
    '''