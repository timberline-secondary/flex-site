
# Server set up. Ubuntu 16.04

1. `apt-get update && apt-get upgrade`
2. (perl locales error? https://www.thomas-krenn.com/en/wiki/Perl_warning_Setting_locale_failed_in_Debian)
3. `adduser username --force-badname --ingroup sudo`
4. add [public key authentication](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04)
5. disable password auth
6. set up basic firewall (ufw) and allow OpenSSH, turn on rate limiting `ufw limit ssh/tcp`, install fail2ban
7. disable root login `/etc/ssh/sshd_config`
8. time: set timezone `sudo dpkg-reconfigure tzdata` and install ntp.

# Nginx Postrgres uWSGI Python/Django stack

1. Install stack: [this for postgresql](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04), and [this for the rest of the stack](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-16-04).
2. If nginx fails due to apache running on port 80, switch to port 8080 `/etc/apache2/ports.conf` (firewall update?) and reinstall nginx
3. uWGSI files: `/etc/systemd/system/uwsgi.service`, `/etc/uwsgi/sites/`, `/etc/nginx/sites-available/flex-site`
