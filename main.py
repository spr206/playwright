#Get the RELEASED list
def pull_released():
    pass

#Iterate through the RELEASED list and pass .pdf and .msg files from done\\\mmddyy to otto_sync
def run_otto():
    pass
    #create \\mmddyy, \\mmddyy\\processed, \\mmddyy\\error, \\mmddyy\\mmddyy.log
    #Copy done files to done\\mmddyy
    #iteration
        #get file path
        #invoke otto_sync
        #if:
            #sucessful is returned from otto_sync
            #copy file to done\\mmddyy\\processed
            #logfile
        #elseif:
            #not_sucessful is returned from otto_sync
            #copy file to done\\mmddyy\\error
            #logfile

#Create log and email to fssacct
def email_log():
    pass

def error_check():
    pass
    #iteration
        #check each file in .\\ against those in .\\processed
        #check each file in .\\ against those in .\\error
        #if:
            #there then delete the copy in .\\
        #else
            #logfile