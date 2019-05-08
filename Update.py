import mysql.connector
from pyfingerprint.pyfingerprint import PyFingerprint


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

mycursor = mydb.cursor()
try:
    print('Waiting for finger...')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    result = f.searchTemplate()
 
    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print('No match found!')
        exit(0)
    else:
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))

    ## OPTIONAL stuff
    ##

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
    
    sql = "SELECT pub_points FROM record WHERE pub_id ='%s'"%characterics
    mycursor.execute(sql)
    myresult = mycursor.fetchone()
    x=int(myresult[0])
    x=x+1;
    print(x)
    sql = "UPDATE record SET pub_points = %s WHERE pub_id = %s"
    val=(str(x),characterics)
    mycursor.execute(sql,val)
    mydb.commit()
   

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)

