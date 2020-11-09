#created by Manu B
import requests, json, time, datetime as dt, sys, getopt

def api_call(ip_addr, port, command, json_payload, sid):
    url = 'https://' + ip_addr + ':' + port + '/web_api/' + command
    if sid == '':
        request_headers = {'Content-Type' : 'application/json'}
    else:
        request_headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}
    r = requests.post(url,data=json.dumps(json_payload), headers=request_headers, verify= False)
    return r.json()


def login(ip, port, user, password, domainname):
    payload = {'user': user, 'password' : password, 'domain' : domainname}
    response = api_call(ip, port, 'login', payload, '')
    return response["sid"]

def main(argv):

    try:
        opts, args = getopt.getopt(argv,"hi:o:u:p:d:",["mgmtip=","port=","uname=", "pass=","domain="])
    except getopt.GetoptError:
        print ("Incorrect Syntax, Correct Syntax as follows :")
        print ('cp_object_analytics.py -i <Mgmt IP> -o <Port> -u <username> -p <password> -d <domain>')
        sys.exit(2)

    ip=''
    port="443"
    user=''
    passw=''
    domain=''

    for opt, arg in opts:
        if opt == "-h":
            print ('cp_object_analytics.py -i <Mgmt IP> -o <Port> -u <username> -p <password> -d <domain>')
            sys.exit()
        elif opt in ("-i", "--mgmtip"):
            ip = arg

        elif opt in ("-o", "--port"):
            port = arg

        elif opt in ("-u", "--uname"):
            user = arg

        elif opt in ("-p", "--pass"):
            passw = arg

        elif opt in ("-d", "--domain"):
            domain = arg

    if ((user=='') or (passw=='') or (ip=='')): 
        print ("Mandatory Parameter missing!, Correct Syntax as follows :")
        print ('cp_object_analytics.py -i <Mgmt IP> -o <Port> -u <username> -p <password> -d <domain>')
        sys.exit(2)

    try:
        sid = login(ip, port, user, passw, domain)
        print("session id: " + sid)
    except Exception as e:
        print ("ERROR in Login!!!\n")
        print (e.message, e.args)
        sys.exit(2)

    #API can send only max of 500 Objects at a time
    limit=500

    #Current Date time to construct a unique file
    currdt=dt.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')

    try:
        payload = {'limit' : limit }
        show_unused_objects = api_call(ip, port,'show-unused-objects', payload ,sid)
        # print("result: " + json.dumps(show_unused_objects))
        # raise Exception

        print "#############################################################################################"
        print "Analyzing host objects..... It takes time, depends of data base, please sit back and relax..."
        print "#############################################################################################\n"
        
        #Initializing variables
        i=0
        j=show_unused_objects['total']
        t=j

        #Incase of debug uncomment the following line
        # count=1

        #Outer Loop
        while i < j:
            payload = {'limit' : limit, 'offset' : i }
            show_unused_objects = api_call(ip, port,'show-unused-objects', payload ,sid)
        
            #Thats for the last lap, ex : what if only 499 left 
            if t<500:
                limit=t
            
            #Inner Loop
            k=0
            while k < limit:
                objname = show_unused_objects['objects'][k]['name']
                otype = show_unused_objects['objects'][k]['type']
                
                #Incase of debug uncomment the following lines
                # dtype = show_unused_objects['objects'][k]['domain']['domain-type']
                # print ("count = " + str(count))
                # print (dtype)
                # print (objname)
                # print (otype)
                
                # incase if we need to only certain types of objects
                # if otype in ["group", "network", "host", "address-range"]:

                print ("Please consider deleting : " + objname +" : Object Type : "+ otype )            
                Ofile = open("unused_objects_output_" + currdt + ".txt", "a")
                Ofile.write(objname + "\n") 
                Ofile.close()
                k += 1
                # Incase of debug uncomment the following line
                # count += 1
            i=i+500
            t = t-500
        print ("\n\nOutput written to file : unused_objects_output_"+ currdt + ".txt\n")
    except Exception as e:
        print ("ERROR in running Analytics!!!\n")
        print (e.message, e.args)

    try:
        logout_result = api_call(ip, port,"logout", {},sid)    
        print("logout result: " + json.dumps(logout_result))
        
    except Exception as e:
        print ("ERROR in Logout!!!\n")
        print (e.message, e.args)


if __name__ == "__main__":
    main(sys.argv[1:])