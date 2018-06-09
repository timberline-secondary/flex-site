## Hackerspace test environment installation (instructions for students)
This guide assumes you are running Linux.  If not, then you can use the [Windows subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) if you have Windows 10.  Another option is [Git Bash](https://git-for-windows.github.io/)

#### Preparation
1. Install Python 3: `sudo apt install python3`
1. Install Git: `sudo apt install git`. 
1. Pick/create a location for the project, e.g: `~/Developer`

#### Fork the repository
1. Create a Github account.
2. Go to https://github.com/timberline-secondary/flex-site
3. Click the "Fork" button on the top right corner. 
4. This will allow you to have your own copy of the project on your GitHub account.

#### Clone the repository
1. In your terminal, move to the parent directory of the project: `cd ~/Developer`
2. Go to your forked repository on github.
3. Click "Clone or download" and copy the url.
4. In the terminal: `git clone yoururlhere`
3. This will download the project into ~/Developer/flex-site/

#### Python Virtual Environment
1. If on Windows, use the [Linux Bash Shell in Windows 10](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/).  If using the Bash Shell in Windows 10, you can follow all the Linux instructions below.
1. Install the Python package manager, pip: `sudo apt install python3-pip`
3. Install [virtualenv](https://virtualenv.pypa.io/en/stable/userguide/) using pip3: `pip3 install virtualenv`
1. If you are asked to upgrade pip: `pip3 install --upgrade pip`
2. Move in to the directory of the project: `cd ~/Developer/flex-site` 
2. Create a virtual environment within your project: `virtualenv .`
3. Activate your virtual environment: Linux: `source bin/activate`
4. You should now see "(hackerspace)" appear before your prompt.
5. Later (don't do it now), when you are finished you can leave the environment by typing: `deactivate`

#### Installing required python packages
1. `pip install -r requirements.txt` (now that we're in our Python3 virtual environment we can just use pip instead of pip3, since our environment will default to python3 for everything)

#### Creating the SQLite database (Easy Option)
1. A basic database to get started.  You can move to a more advanced PostgreSQL database later if you like, or try now (see next section)
`./src/manage.py migrate`  This will create your database and create tables for all the thrid-party apps/requirements
2. Now prepare tables for all of the flex-site models: `./src/manage.py makemigrations profiles events excuses` (you might get an error later on if I forget to keep this list of apps updated =)
2. Create the tables in your database: `./src/manage.py migrate`
2. Populate the database with some default data: `./src/manage.py loaddata src/initial_data`
3. Create a superuser in the database (i.e.teacher/administrator account): `./src/manage.py createsuperuser`

#### Creating the PostgreSQL database (Advanced Option)
1. You can follow [these instructions](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-16-04) if you are on Linux (won't work on Windows).  Use the Python3 options.

#### Running the server
1. `./src/manage.py runserver`
2. Segmentation Fault?  try running it again...
3. In your browser go to [127.0.0.1:8000](http://127.0.0.1:8000) to see if it worked!
4. Log in as the superuser to see what a teacher/admin sees
5. Sign up to create a student account.
6. Stop running server (or any bash script in progress) with `Ctrl + C`

#### Setting up PyCharm IDE
1. Install some version of [PyCharmIDE](https://www.jetbrains.com/pycharm/download/#section=linux)
1. File > Open, then choose the ~/Developer/flex-site directory
1. Run > Edit Configurations
1. it "+" and choose Django Server
1. Defaults should be good, but "Run Browser" option is handy, tick it if you want to auto open a browser when you run the server.
1. Turn on Django support.  Click "Fix" button at bottom
1. Tick "Enable Django Support
1. Set Django project root to: ~/Developer/flex-site/src
1. Set Settings to: `flex-site/settings` (this is relative to the root above)
1. OK, Apply, Close.
1. Hit the green play button to test.  Try logging in with the superuser account you created earlier.

#### Committing changes

1. Move into your cloned directory. `cd ~/Developer/hackerspace`
2. Add the upstream remote: `git remote add upstream git@github.com:timberline-secondary/hackerspace.git`
3. Pull in changes from the upstream master: `git fetch upstream`
4. Merge the changes: `git merge upstream/master`
5. Create a new branch: `git checkout -b yourbranchname`
6. Make your changes and them commit: `git commit -am "yourchangeshere"`
7. Push your branch to your fork of the project: `git push origin yourbranchname`
8. Go to your fork of the repository. 
9. Select your recently pushed branch and create a pull request.
10. Complete pull request.





## Server set up. Ubuntu 16.04

1. `apt-get update && apt-get upgrade`
2. (perl locales error? https://www.thomas-krenn.com/en/wiki/Perl_warning_Setting_locale_failed_in_Debian)
3. `adduser username --force-badname --ingroup sudo`
4. add [public key authentication](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04)
6. set up basic firewall (ufw) and allow OpenSSH, turn on rate limiting `ufw limit ssh/tcp`, install fail2ban
7. disable password authentication and root login `/etc/ssh/sshd_config`
8. time: set timezone `sudo dpkg-reconfigure tzdata` and install ntp.

## Nginx Postrgres uWSGI Python/Django stack

1. Install stack: [this for postgresql](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04), and [this for the rest of the stack](http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html).
2. Remove Apache2 from port 80 (if using)
3. ...permissions of socket...

## Additional Security
1. Add SSL, 
2. redirect to https in mysite_nginx.conf, server 80 block (`return 301 https://$server_name$request_uri;`), 
3. Add [forward secuirty](https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html#Forward_Secrecy_&_Diffie_Hellman_Ephemeral_Parameters)
4. [Automatic security updates]( https://help.ubuntu.com/community/AutomaticSecurityUpdates)

## Other
1. Django DEBUG = False
