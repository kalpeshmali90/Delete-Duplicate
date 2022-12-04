import os
import time
import urllib.request
from sys import *
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import  datetime
import schedule

def is_connected():
    try:
        urllib.request.urlopen("http://www.google.com/")
        return True
    except:
        return False


def checksum(dir_name):
    is_dir=os.path.isdir(dir_name)
    data={}
    if is_dir==True:

        for folder_name,sub_folder,file_name in os.walk(dir_name):
            for file in file_name:
                hasher = hashlib.md5()
                file_path=os.path.join(folder_name,file)
                a_file=open(file_path,mode="rb")
                file_content=a_file.read()
                hasher.update(file_content)
                hex_digest=hasher.hexdigest()
                a_file.close()

                if hex_digest  in data:
                    data[hex_digest].append(file_path)
                else:
                    data[hex_digest]=[file_path]
    return data

def delete_duplicate(dir_name):
    separator="-"*90

    t = str(datetime.datetime.now())
    t2 = t.replace(":", ".")  #To name a log file with timestamp
    current_time = t2.replace(" ", "_")

    duplic= checksum(dir_name)
    results = list(filter(lambda x: len(x) > 1, duplic.values()))
    if len(results) > 0:

        log_file = open(os.path.join(dir_name, f'deleted_file_{current_time}.log'), 'a')
        log_file.write(f"duplicate files recorded at {t} are:\n")
        log_file.write(f"{separator}\n")
        for each in results:

            log_file.write(f"{each[0]}\n")

            is_abs=os.path.isabs(each[0])
            if is_abs==False:
                is_abs=os.path.abspath(each[0])
            os.remove(path=is_abs)
        log_file.write("\n")
        log_file.close()

    else:
        print('No duplicates found.')
    return current_time

def send_mail(dir_name,to_mail_id):
    return_value=delete_duplicate(dir_name)
    t1 = return_value.replace(".", ":")
    t2 = t1.replace("_", " ") #to reconvert the time to original format

    fromaddr = "pythonexercise900@gmail.com"
    toaddr = to_mail_id

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Log file"

    # string to store the body of the mail
    body = f"Hi This mail contains log file of deleted duplicate files created at {t2}"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent

    filename = f"deleted_file_{return_value}.log"
    abs_path=os.path.abspath(dir_name)
    total_path = os.path.join(abs_path, filename)
    attachment = open(total_path, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication

    s.login(fromaddr, os.environ.get("password"))

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()
    print("mail sent succesfully")

def main():

    if argv[1] == "--h" or argv[1]=="--H":
        print("this program will accept dir name and mail id."
              "dir name: all duplicate files will be deleted inside of that dir name"
              "mail id: deleted files names will be stored in log file which will be sent to an email "
              "sample input in terminal: python delete_dupli.py Dir_name  to_mail_add@gmail.com" )
        exit()

    if len(argv) < 2:
        print("insuffient arguments. use --h for help")
        exit()

    if is_connected()==True:
        schedule.every(1).hour.do(send_mail(argv[1],argv[2]))
    while True:
        schedule.run_pending()
        time.sleep(2)



if __name__ == "__main__":
    main()
