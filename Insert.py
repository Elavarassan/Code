import time
import mysql.connector
from pyfingerprint.pyfingerprint import PyFingerprint


## Enrolls new finger
##

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    mydb = mysql.connector.connect(
         host="*****",
         user="*****",
         passwd="*****",
         database="****"
         )

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

mycursor = mydb.cursor()
## Tries to enroll new finger
try:
    print('Waiting for finger...')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        exit(0)

    print('Remove finger...')
    time.sleep(2)

    print('Waiting for same finger again...')

    ## Wait that finger is read again
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    ## Compares the charbuffers
    if ( f.compareCharacteristics() == 0 ):
        raise Exception('Fingers do not match')

    ## Creates a template
    f.createTemplate()

    ## Saves template at new position number
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))

     ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, 0x01)
    # Downloads the characteristics of template loaded in charbuffer 1
    characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')  
    characterics=characterics.translate(None,',')
    characterics=characterics.translate(None,'[')
    characterics=characterics.translate(None,']')
    characterics=characterics.translate(None,'0')
    characterics=characterics.translate(None,' ')
    print(characterics)
    
    sql = "INSERT INTO record (pub_id, pub_name,pub_points) VALUES (%s, %s,%s)"
    name = raw_input("Enter your name : ")
    points= raw_input("Enter your points : ")
    val = (characterics, name,points)
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)