
# Server set up. Ubuntu 16.04

1. `apt-get update && apt-get upgrade`
2. (perl locales error? https://www.thomas-krenn.com/en/wiki/Perl_warning_Setting_locale_failed_in_Debian)
3. `adduser 90158 --force-badname --ingroup sudo`
4. add [public key authentication](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04)
5. disable password auth
6. set up basic firewall (ufw) and allow OpenSSH, turn on rate limiting `ufw limit ssh/tcp`
7. disable root login
8. time: set timezone `sudo dpkg-reconfigure tzdata` and install ntp.
