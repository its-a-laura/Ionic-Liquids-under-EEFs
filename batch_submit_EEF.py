# -*- coding: utf-8 -*-
"""

This code creates an sbatch script to run a collection of jobs on the VUW Raapoi HPC.
The code will copy jobs from the users home directory to their scratch directory, run
the jobs, and copy the results back.

The jobs to submit should all consist of the same base file name, followed by a job id,
such as those produced by generate_EEF_com.py. Code is currently setup to sumbit jobs
produced by generate_EEF_com.py, but can be aadapted for other job collections by changing
the job_ids.

Code has been adapted from Dsubmit.py written by Patricia Hunt:
    https://sagacioushours.org.uk/wiki/index.php?title=Talk:Mod:Hunt_Research_Group/Dsubmit

To run this script:
    python batch_submit_EEF.py base_job_name
    

Please note no file extensions    

"""


import sys
import os
import subprocess
dir=os.getcwd()


# EDIT THESE TO SPECIFY THE JOB PARAMETERS
CPUS_PER_TASK = "32"
MEM = "64G"
PARTITION = "quicktest"
TIME = "02:00:00"
USER = "username"
FOLDER = "/foldername" # leave as empty string if jobs are not in a subfolder


# EDIT THESE TO SELECT JOBS TO SUBMIT
FIELD_DIRECTIONS = ["x"]
FIELD_STRENGTHS = [5]
FIELD_SIGNS = [1]

# create a list of all job ids
job_ids = []
for direction in FIELD_DIRECTIONS:
    for strength in FIELD_STRENGTHS:
        for sign in FIELD_SIGNS:
            job_ids.append(direction+str(sign * strength))

# specify the home and scratch directories
home_dir = '/nfs/home/'+USER+FOLDER+'/'
scratch_dir = '/nfs/scratch/'+USER+FOLDER+'/'

# grab the base job name
bjob=str(sys.argv[1])
s='base job expression: '
print('{0:}{1:}'.format(s,bjob))
#
n=0
s='jobs to run: '

# for each job, generate and submit an sbatch file
print('{0:}'.format(s))
for job_id in job_ids :
    
    
    job=bjob+"_"+job_id
    jobname = job_id+"_"+bjob
    com=job+".com"
    log=job+".log"
    chk=job+".chk"
    err=job+".err"
    jobcom=home_dir+job+".com"
    joblog=home_dir+job+".log"
    jobchk=home_dir+job+".chk"
    joberr=home_dir+job+".err"
    
    # open files
    f=open("rung16.sh","w")

    # create submit script
    s0='#!/bin/bash'
    s1='#SBATCH --job-name=' #jobname
    s2='#SBATCH --cpus-per-task=' + CPUS_PER_TASK
    s3='#SBATCH --mem=' + MEM
    s4='#SBATCH --partition=' + PARTITION
    s5='#SBATCH --time=' + TIME
    f.write('{0:}\n{1:}{2:}\n{3:}\n{4:}\n{5:}\n{6:}\n'.format(s0,s1,jobname,s2,s3,s4,s5))

    s0='#SBATCH -o '+scratch_dir #log
    s1='#SBATCH -e '+scratch_dir #err
    f.write('{0:}{1:}\n{2:}{3:}\n\n'.format(s0,log,s1,err))

    s0='cp ' #jobcom 
    f.write('{0:}{1:} {2:}{3:}\n\n'.format(s0,jobcom,scratch_dir,com))

    s0='test -r ' #chk 
    s1=("if [ $? -eq 0 ] \n"
     "then \n")
    s2='cp '  #jobchk
    s3='fi'
    f.write('{0:}{1:}\n{2:}{3:}{4:} {5:}{6:}\n{7:}\n\n'.format(s0,chk,s1,s2,jobchk,scratch_dir,chk,s3))

    s0='cd '
    s1='module --quiet purge'
    s2='module load gaussian/g16'
    s3='g16 '  #com 
    f.write('{0:}{1:}\n{2:}\n{3:}\n{4:}{5:}\n\n'.format(s0,scratch_dir,s1,s2,s3,com))

    s0='test -r ' #log
    s1=("if [ $? -eq 0 ] \n"
     "then \n")
    s2='  cp ' #log
    s3=' '  #joblog
    s4='fi'
    f.write('{0:}{1:}\n{2:}{3:}{4:}{5:}{6:}{7:}\n{8:}\n\n'.format(s0,log,s1,s2,scratch_dir,log,s3,joblog,s4))

    s0='test -r ' #chk 
    s1=("if [ $? -eq 0 ] \n"
     "then \n")
    s2='  cp ' #chk
    s3=' '  #jobchk
    s4='fi'
    f.write('{0:}{1:}\n{2:}{3:}{4:}{5:}{6:}{7:}\n{8:}\n\n'.format(s0,chk,s1,s2,scratch_dir,chk,s3,jobchk,s4))

    # close files
    f.close()

    s0='now submiting via: sbatch rung16.sh'
    print('{0:} {1:}'.format(s0,job))
    os.system('sbatch rung16.sh')
    n=n+1

print("{} jobs submitted".format(n))
#end
sys.exit()
