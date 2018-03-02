== DTM ==

=== REQUIREMENTS ===

All packages required by DC are installed by that script

create file
hce-dts-install.sh
#!/bin/sh
apt-get install python-pip python-dev subversion
pip install cement
aptitude install python-flask
aptitude install python-flaskext.wtf
pip install sqlalchemy
pip install Flask-SQLAlchemy
apt-get install libffi-dev libxml2-dev  libxslt1-dev
apt-get install php5
apt-get install php5-dev
apt-get install php-pear
apt-get install pkg-config
apt-get install libpgm-dev
apt-get install bc
apt-get install openjdk-7-jdk
pecl install zmq-beta
pip install scrapy
#zmq
wget http://download.zeromq.org/zeromq-4.0.4.tar.gz
tar -xvf zeromq-4.0.4.tar.gz
cd zeromq-4.0.4
./configure && make && make install
cd -
rm -rf zeromq-4.0.4 zeromq-4.0.4*
ldconfig
echo "extension=zmq.so" >> /etc/php5/cli/php.ini
pip install pyzmq --install-option="--zmq=bundled"
#svn
mkdir ~/hce_dts/ && cd ~/hce_dts
svn co svn://192.168.1.201/hce/hce_dts/trunk/


== DC ==

=== REQUIREMENTS ===

All packages required by DC are installed by that script

create file
: dc-requirements-install.sh

  #!/bin/sh
  
  #zmq
  wget http://download.zeromq.org/zeromq-4.0.4.tar.gz
  tar -xvf zeromq-4.0.4.tar.gz
  cd zeromq-4.0.4
  ./configure && make && make install
  cd -
  rm -rf zeromq-4.0.4 zeromq-4.0.4*
  ldconfig
  #for Debian
  pip install pyzmq --install-option="--zmq=4.0.3"
  #for Centos
  pip install pyzmq --install-option="--zmq=bundled" 

  #hce-node
  apt-get install php5
  apt-get install php-pear php5-dev
  apt-get install pkg-config
  pecl install zmq-beta
  echo "extension=zmq.so" >> /etc/php5/cli/php.ini
  
  #for CrawlerTask and ProcessorTask
  apt-get install subversion libffi-dev libxml2-dev libxslt1-dev python-pip mysql-client libmysqlclient-dev python-dev python-mysqldb libicu-dev libjpeg-dev
  pip install pillow

  #specific version of requests for avg resources CrawlerTask 

  # requests ver >= 2.4.3
  pip install requests 
  
  pip install mysql-python cement pyicu scrapy newspaper goose-extractor lepl 
  sudo pip install Ghost.py --pre
  sudo pip install uritools

  #for CrawlerTask tidylib
  sudo apt-get install libtidy-dev
  sudo pip install pytidylib

  # CrawlerTask dependences
  sudo pip install Ghost.py --pre
  sudo pip install python-magic


  chmod +x dc-requirements-install.sh
  ./dc-requirements-install.sh
    
== HCE-NODE ==

=== REQUIREMENTS ===