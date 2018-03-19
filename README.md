

# weewx-uradmon


**Description**

This is a skin that integrates with [weewx](http://weewx.com) (weather station software) and provides the capture and storage of the output from an A3 [uradmonitor](https://www.uradmonitor.com).


***Instructions:***

1. Download the skin to your weewx machine.

    <pre>wget -O weewx-uradmon.zip https://github.com/glennmckechnie/weewx-uradmon/archive/master.zip</pre>

2. Change to that directory and run the wee_extension installer

   <pre>sudo wee_extension --install weewx-uradmon.zip</pre>

3. Restart weewx

   <pre>
   sudo /etc/init.d/weewx stop

   sudo /etc/init.d/weewx start
   </pre>


4. Problems?
   Hopefully none but if there are then look at your logs - syslog and apache2/error.log. If you view them in a terminal window then you will see what's happening, as it occurs.

   (I find multitail -f /var/log/syslog /var/log/apache2/error.log works for me {adjust to suit your install} -- apt-get install multi-tail if needed)

5.To uninstall

   <pre>sudo wee_extension --uninstall uradmon</pre>

   and then restart weewx

   <pre>
   sudo /etc/init.d/weewx stop

   sudo /etc/init.d/weewx start
   </pre>

***Database options***

In its default configuration, this skin will write to an sqlite database.

To change that to a mysql database then you need a suitable database user and to make a minor alteration to the uradmon entry in weewx.conf.

For the database, the following example assumes it will be named uradmon, and that the database user will be the weewx default user.
eg:- The following extract shows your user...

<pre>
[DatabaseTypes]
    [...]
    [[MySQL]]
        [...]
        user = weewx
</pre>
That user can now be assigned the appropriate permissions to operate the needed database, and you may need to create the user depending how you have previously setup weewx setup (the default is no mysql).

<pre>
mysql -uroot -p
Enter password:

 [...]
 MariaDB [(none)]>CREATE USER 'weewx'@'localhost' IDENTIFIED BY 'weewx';
 MariaDB [(none)]> GRANT select, update, create, delete, insert ON uradmon.* to weewx@localhost;
Query OK, 0 rows affected (0.01 sec)

MariaDB [(none)]> quit;
Bye
</pre>

With the above step done you'll then need to change one of the uradmon entries that was installed by the uradmon extension into weewx.conf...

Replace the old entry __database = uradmon_sqlite__  with your new one  __database = uradmon_mysql__ 
eg:-

<pre>
[DataBindings]
    [[uradmon_binding]]
        [...]
        database = uradmon_mysql

</pre>
Save weewx.conf and then restart weewx as per the installation instructions above, then watch your logs for any errors.
It should work seemlessly, but it always pays to check!
