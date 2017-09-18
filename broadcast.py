import time,socket,threading,hashlib,logging,pickle
import Queue
"""
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-6s) %(message)s',)
"""
class Senderthread(threading.Thread):
   def __init__(self,address,parameters):
       threading.Thread.__init__(self,name="senderthread")
       self._stop = threading.Event()
       self.params = parameters
       self.address = address
       self.count = 0
   def stop(self):
       self._stop.set() #sets internal flag to True
   def stopped(self):
        return self._stop.isSet() #returns true if flag is True
   def run(self):
       #address = ("",8000)
       s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
       
       #s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
       while True:
           try:
               data = pickle.dumps(self.params)
               checksum = self.packet_validation(data)
               msg = (data,checksum)
               pickled_msg = pickle.dumps(msg)               
           except pickle.UnpicklingError, e:
               print "pickling erorr...."
               logging.debug("pickling error")

           if self._stop.isSet():
               break    
           
           else: 
               s.sendto(pickled_msg,self.address)
               #sends message to the reciever thread
               self.count+=1        
               logging.debug("message sent")
               time.sleep(1)
           
                
       s.close()
       print "socket is closed"
   def packet_validation(self,data):
       """
       This function returns a string of binary data
       """
       m = hashlib.md5()
       m.update(data)
       return m.hexdigest()

class ReceiverThread(threading.Thread):
   def __init__(self,address,queue):
       threading.Thread.__init__(self,name="receieverthread")
       self.address = address
       self.queue = queue
       self.count = 0
       self._stop = threading.Event()
   def stop(self):
       self._stop.set()
   def stopped(self):
       return self._stop.isSet()
   def run(self):
       sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
       sock.settimeout(10)
       sock.bind(self.address)
       while True:
             try:
                 """
                 if self._stop.isSet():
                   print "terminating receiver thread.."
                   break
                 """

                 raw_msg,address = sock.recvfrom(4096)
                 #print "recieved from: adresss is {} and data is {}".format(address,data)
                 #logging.debug("recieved data is {}".format(data))
                 msg = pickle.loads(raw_msg)
              
                  
                 if self.checksum_verify(msg):
                      data = pickle.loads(msg[0])
                      
                      self.queue.put((data,address))
                      #logging.info("received msg-> %s from ip adress:%s",msg[0],address[0])
                      self.count+=1
                   
                 else:
                     logging.warning("recieved wrong data something went wrong")
                 if self._stop.isSet():
                   print "terminating receiver thread.."
                   break
 
             except socket.timeout:
                 print "socket connection has timed out"
                 break
             except socket.error as e:
                 print e
                 break
             except pickle.UnpicklingError:
                 logging.debug("could not unpickle data")
       sock.close()
   def checksum_verify(self,data):
       if type(data) is tuple:
           #get MD5 of received messgae across network
           m = hashlib.md5()
           m.update(data[0])
           recieved_checksum = m.hexdigest()
           #get MD5 of sent data across network
           sent_checksum = data[1]
           if recieved_checksum == sent_checksum:
              return True
           else: 
              return False
       else:
            return None

class Task_handler(threading.Thread):
   def __init__(self,q):
       threading.Thread.__init__(self)
       self.daemon = True
       self.msg_queue = q
       self.count = 0
   def run(self):
       while True:
           try:
              (message,address) = self.msg_queue.get()
              #print "received message from task handler"
              #print message
             
              print message.lat
              print message.lon
              print message.alt
              print message.heading
              
              print "****************"
              self.count+=1
              self.msg_queue.task_done()
           except Queue.Empty:
              print ("all messages processed")


if __name__=="__main__":
   logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-6s) %(message)s',)  
   thread1 = Senderthread(("",8001),"sampledata")
   thread1.start()
   print threading.enumerate()
   for i in range(3):
      print "broadcasting"
      time.sleep(2)

   print thread1.stopped()
   thread1.stop()
   print thread1.stopped()
   print thread1.count
