#!/cvmfs/sft.cern.ch/lcg/releases/LCG_87/Python/2.7.10/x86_64-slc6-gcc49-opt/bin/python
#./sendAllJobs.py -n 500 -e 10000 -q 1nd -f process_list.txt

import os, time, subprocess, datetime
import socket
import getpass
#__________________________________________________________
def write(towrite):
    outfile = open('/afs/cern.ch/work/h/helsens/public/FCCDicts/sendJobs.log', 'a')
    towrite=towrite+'\n'
    outfile.write(towrite)

#__________________________________________________________
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}


#__________________________________________________________
def getNjobs(cmd,nbtrials):
    cmdStatus=0
    for i in range(nbtrials):         
        outputCMD = getCommandOutput(cmd)
	stderr=outputCMD["stderr"].split('\n')
	for line in stderr :
	    if line=="" or line=="No unfinished job found":
                cmdStatus=1
                break
            else:
                write('++++++++++++ERROR while trying the command ===%s==='%cmd)
                write('Trial : %i/%i'%(i,nbtrials))
                write('will retry in 10 seconds')

                time.sleep(10)
                break

        njobs=int(outputCMD["stdout"])

        if cmdStatus==1:
            return njobs

        
        if i==nbtrials-1:
            write('failed trying the command ===%s=== after: %i trials, will exit'%(s,nbtrials))
            return 0


#__________________________________________________________
def can_send(trials=10, period=60, threshold=0):
    cmd="bjobs -u selvaggi | grep 'PEND\|RUN' | wc -l"
    while True:
        njobs=getNjobs(cmd,nbtrials)
	if njobs > threshold:
	    write('cannot submit yet, since {} jobs are running or pending. Sleep for {} seconds'.format(njobs, period))
	else:
            write('can submit, since only {} jobs are running or pending.'.format(njobs))
            return True
        time.sleep(period)

#__________________________________________________________
def getdatetime():    
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    return st

#__________________________________________________________
if __name__=="__main__":
    
    write('=================================================================')
    write('================START the execution of the script================')
    write('=================================================================')
    write('TIME  %s'%getdatetime())

    write('hostname  %s'%socket.gethostname())
    write('username  %s'%getpass.getuser())
    write('localdir  %s'%os.getcwd())

    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option ('-n', '--njobs',  help='number of jobs per process',
                       dest='njobs',
                       default='')

    parser.add_option ('-e', '--events',  help='number of events per job',
                       dest='events',
                       default='')

    parser.add_option ('-q', '--queue',  help='queue',
                       dest='queue',
                       default='')

    parser.add_option ('-f', '--file',  help='file containing flat list of processes',
                       dest='file',
                       default='')

    (options, args) = parser.parse_args()
    njobs  = options.njobs
    events = options.events
    pfile  = options.file
    queue  = options.queue
    
    nbtrials=10
    sleep=60
    threshold=500

    write('input parameters: njobs=%s  events=%s  queue=%s  file=%s'%(njobs, events, queue, pfile))
    write('job parameters: sleep=%i  nbtrials=%i  threshold=%i'%(sleep, nbtrials,threshold))

    process_list = []
    
    with open(pfile) as f:
        process_list = f.read().splitlines()    

        for p in process_list:
            if p=='': continue
            cmd = 'python /afs/cern.ch/work/s/selvaggi/private/EventProducer/bin/sendJobs.py -n {} -e {} -q {} -p {}'.format(njobs, events, queue, p)
            write('')
            write('----------------------------------------------------------------------')
            write('Process: {}'.format(p))
            write('')
                
            if can_send(nbtrials, sleep, threshold):
                write('')
                write('TIME  %s'%getdatetime())
                write('Start submission for process: {}'.format(p))
                write('command:  %s'%cmd)
                my_env = os.environ
                p=subprocess.Popen(cmd, shell=True)
                p.communicate()

            write('TIME  %s'%getdatetime())
        write('=================================================================')
        write('=================END the execution of the script=================')
        write('=================================================================')
