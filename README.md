# easy_cms  
Easily install, configure, control [cms](http://cms-dev.github.io/)(Contest Management System v1.3rc0) on remote Ubuntu 16.04 machines.  

## Preparation  
Install python requirements from **requirements**.  
Configure **settings.py** and **passwords.py** in **config** folder.  

## Installation of cms  
Run script with **-i** flag and specify indexes of ip addreses written in **settings.py** numbered from zero.  
Example: **python3 ./easy_cms 0 1 2 3 -i**  

## Updating configs  
Run script with **-u** flag and specify indexes of ip addreses written in **settings.py** numbered from zero.  
Example: **python3 ./easy_cms 0 1 2 3 -u**  

## Start AdminWebServer  
Run script with **--start_admin** flag.  
Example: **python3 ./easy_cms --start_admin**  

## Import task from Polygon  
Run script with **-ti %task_link%** flag and specify link to task.  
Example: **python3 ./easy_cms --task_import https://<i></i>polygon.codeforces.com/p85dIBF/mmirzayanov/a-plus-b**  

## Update task from Polygon  
Run script with **-tu %task_link%** flag and specify link to task.  
Example: **python3 ./easy_cms --task_update https://<i></i>polygon.codeforces.com/p85dIBF/mmirzayanov/a-plus-b**  

## Starting contest  
Run script with **-s %contest_id%** flag and specify indexes of ip addreses written in **settings.py** numbered from zero.  
Example: **python3 ./easy_cms 0 1 2 3 -s 1**  

## Stop cms  
Run script with **--stop** flag and specify indexes of ip addreses written in **settings.py** numbered from zero.  
Example: **python3 ./easy_cms 0 1 2 3 --stop**  

## ...  
You can combine commands.  
Example: **python3 ./easy_cms 0 1 2 3 -i --start_admin**  
Commands operations executed in this order:  
**Installation**  
**Updating configs**  
**Starting AdminWebServer**  
**Stopping cms**  
**Importing tasks**  
**Updating tasks**  
**Starting cms**  

## First steps on Amazon Web Servers
 *  Launch Ubuntu 16.04 EC2 Instances (one of the best choices is t2.medium with ~20GB SSD).
 *  Open 80 port for main instance and allow all traffic to local (usually 172.31.0.0/16, change it in **settings.py** if it's different).
    ![inbound rules](https://user-images.githubusercontent.com/17214986/56339576-9c025080-61d0-11e9-9de6-40b1f65c95e3.png)
 *  Add ip addresses list to **settings.py** and specify number of workers (remember that first ip in list will be used as main web server). Change passwords in **passwords.py**. Change path to your pemfile in **settings.py**.
 *  Run **python3 ./easy_cms 0 1 2 -i --start_admin** to install CMS and run AdminWebServer.
 *  Configure contest.
     *  Log in to AWS.
     *  Add contest.
     *  Configure start time and languages.
     *  Add tasks.
         * Run **python3 ./easy_cms --task_import https://<i></i>polygon.codeforces.com/p85dIBF/mmirzayanov/a-plus-b** to import task from polygon.
         *  Do not forget to configure scoring type for every task.
     *  Add users.
 *  Run **python3 ./easy_cms 0 1 2 -s 1** to start contest for users.
