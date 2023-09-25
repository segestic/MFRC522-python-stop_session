# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import RPi.GPIO as GPIO
import time
  
class SimpleMFRC522:

  READER = None
  
  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  BLOCK_ADDRS = [8, 9, 10]
  
  def __init__(self):
    self.running = True
    self.READER = MFRC522()
  
  def read(self):
      id, text = self.read_no_block()
      while not id:
          id, text = self.read_no_block()
      return id, text

  
#read it takes a parameter - time in seconds
  def read_id(self, time_in_seconds):
      id = self.read_id_no_block(time_in_seconds)
      while not id:
          id = self.read_id_no_block(time_in_seconds)
      return id

  def read_id_no_block(self, time_in_seconds):
      start_time = time.time()
      while time.time() - start_time <= time_in_seconds:
          (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
          if status != self.READER.MI_OK:
              continue
          (status, uid) = self.READER.MFRC522_Anticoll()
          if status != self.READER.MI_OK:
              continue
          return self.uid_to_num(uid)
      return None
    
  # def read_id_no_block(self):
  #     (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
  #     if status != self.READER.MI_OK:
  #         return None
  #     (status, uid) = self.READER.MFRC522_Anticoll()
  #     if status != self.READER.MI_OK:
  #         return None
  #     return self.uid_to_num(uid)
  
  def read_no_block(self):
      while self.running:
          (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
          if status != self.READER.MI_OK:
              return None, None
          (status, uid) = self.READER.MFRC522_Anticoll()
          if status != self.READER.MI_OK:
              return None, None
          print ('UID before conversion to demcimal is ', uid)
          id = self.uid_to_num(uid)
          self.READER.MFRC522_SelectTag(uid)
          status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
          data = []
          text_read = ''
          if status == self.READER.MI_OK:
              for block_num in self.BLOCK_ADDRS:
                  block = self.READER.MFRC522_Read(block_num) 
                  if block:
                  		data += block
              if data:
                   text_read = ''.join(chr(i) for i in data)
          self.READER.MFRC522_StopCrypto1()
          return id, text_read
    
  def write(self, text):
      id, text_in = self.write_no_block(text)
      while not id:
          id, text_in = self.write_no_block(text)
      return id, text_in

  def write_no_block(self, text):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
      self.READER.MFRC522_Read(11)
      if status == self.READER.MI_OK:
          data = bytearray()
          data.extend(bytearray(text.ljust(len(self.BLOCK_ADDRS) * 16).encode('ascii')))
          i = 0
          for block_num in self.BLOCK_ADDRS:
            self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
            i += 1
      self.READER.MFRC522_StopCrypto1()
      return id, text[0:(len(self.BLOCK_ADDRS) * 16)]

  def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n
  
  #stop session added. to current stop a reading session without card scanning...
  def stop_session(self):
      self.running = False  # Set the flag to stop the RFID session
      self.READER.MFRC522_StopCrypto1()
      return True


