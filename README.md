# PyFax2Mail
This is a Python implementation to send incoming FAX directly by Mail to a set of recipients of your choice, from the PBX dialplan straight forward.\
\
The implementation is using the mod_python package of freeswitch.\
The debian package of freeswitch is compiled in python 2.7.

The code is written to support Python 2.7 and +3.5 syntax.\
If you update freeswitch and future versions of mod_python is compiled in 3.x the code will still execute without throwing errors.

Requirements:\
You need the tiff tools package

**Installation:**

1st you need to figure out where the PYTHONPATH inside FS points.\
Start the fs_cli console and execute **env system** example:

```
freeswitch@tuxtux> system env
LANGUAGE=de_CH:de
USER=freeswitch
GROUP=freeswitch
JOURNAL_STREAM=9:8618863
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
INVOCATION_ID=49d4df5de8b14ddda8729b7f0a8ba662
LANG=de_CH.UTF-8
PWD=/usr/local/src/fs
DAEMON_OPTS=-nonat
PYTHONPATH=/usr/share/freeswitch/scripts
```
it tells you where the python path points, and there we clone the app.\
Change to "/usr/share/freeswitch/scripts" and clone the app.

On my machine this folder is owned by the user freeswitch.\
In this case we clone the app as the user freeswitch
```
sudo -u freeswitch -g freeswitch git clone https://github.com/thigazi/PyFax2Mail.git fs
sudo -u freeswitch -g freeswitch touch __init__.py
```

Now we need to modify the dialplan to create the pdf file and set 3 variables before calling the app.\
Here is a complete sample for receiving a fax, converting it to pdf and handover the variables to the python app:
```
<action application="set" data="absolute_codec_string=PCMA"/>
<action application="set" data="fax_enable_t38=true"/>
<action application="set" data="fax_enable_t38_request=true"/>
<action application="answer" />
<action application="t38_gateway" data="self"/>
<action application="playback" data="silence_stream://2000"/>
<action application="rxfax" data="/var/spool/spandsp/${uuid}.tiff"/>
<action application="system" data="tiff2pdf -d -p A4 -o /var/spool/spandsp/${uuid}.pdf /var/spool/spandsp/${uuid}.tiff"/>

<action application="set" data="caller=${caller_id_number}"/>
<action application="set" data="pdffile=/var/spool/spandsp/${uuid}.pdf"/>
<action application="set" data="tiffile=/var/spool/spandsp/${uuid}.tiff"/>
<action application="python" data="fs.mailer"/>
```

the last thing to do is to configure the listconfig.xml, which is quiet self explaining :-)
