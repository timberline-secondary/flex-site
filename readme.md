
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
