

# weewx-uradmon

**Update: Jun 2020**

This version has been rolled up and released as [v0.1.5](https://github.com/glennmckechnie/weewx-uradmon/releases)

Fix the utf-8 breakage (micros and cubes), add weewx4 logging.

This runs under python 2.7 ; it will also run under python3 as is required for weewx4.

The main change is that this weewx extension (SLE) has now been updated to capture, archive, and display the noise parameter. If your model does not capture noise, the skin will adapt by ignoring that field.

To do this the old database requires an extra field. This doesn't matter if you're doing a brand new install as it will obviously be created along with everything else. If you are upgrading though, you'll need to dump (if you want to restore your old data) and then rename (delete) your old database as uradmon will not use it in its current form.

Thanks go to evilbunny2008 and lizdodd for this enhancement.

**Description**

This extension provides a Service, and a Report skin that integrates with [weewx](http://weewx.com) (weather station software).

The Service captures and stores the output from a [uradmonitor](https://www.uradmonitor.com) into a local database at the exisiting archive interval (as set in weewx.conf).
By default it captures the data from an A3 unit but it should also capture most other modules. Sqlite is the default database, mysql is also an option.
The Report will generate a seperate html page in the style of the Seasons skin. It will be located at weewx/uradmon/index.html with daily, weekly, monthly and yearly graphs as is done with the main weewx/ pages and your weather station.

***Instructions:***



1. Download the skin to your weewx machine.

    The latest working code can be found by using the following command...

    <pre>wget -O weewx-uradmon.zip https://github.com/glennmckechnie/weewx-uradmon/archive/master.zip</pre>

    This version will have the most recent updates.

    (Alternatively, it is packaged as a release under https://github.com/glennmckechnie/weewx-uradmon/releases
    This gives a fixed (in time) version. You will need to adjust the following instructions by using the filename you downloaded.)

2. Change to that directory and run the wee_extension installer

   <pre>sudo wee_extension --install weewx-uradmon.zip</pre>

   (or if using a release version, substitute the filename weewx-uradmon.zip with the downloaded file name (eg: v0.1.4.zip))

3. You will need to edit the main weewx.conf file and under the [Uradmon] section add the IP address of your unit.

   <pre>
    # Options for extension 'uradmon'
    [UradMon]
        #urad_debug = True
        data_binding = uradmon_binding
        uradmon_address = 192.168.0.235
   </pre>

   It will appear as above. Change the _192.168.0.235_ to point to your unit, using its __IP__ or __Qualified name.__

   Next, edit the uradmon/skin.conf and in the top setion there is the __unit_id__ that needs changing. Replace what is there with yours.

   <pre>
   [Uradmonitor]
           # id of your uradmonitor device, aka unit.
           # This is the unique number allocated by the uradmonitor site and
           # can be found on your dashboard page, once you are logged in.
           unit_id = 82000079
   </pre>



4. Restart weewx

   <pre>
   sudo /etc/init.d/weewx stop

   sudo /etc/init.d/weewx start
   </pre>


5. Problems?
   Hopefully none but if there are then look at your logs - syslog and apache2/error.log. If you view them in a terminal window then you will see what's happening, as it occurs.

   (I find multitail -f /var/log/syslog /var/log/apache2/error.log works for me {adjust to suit your install} -- apt-get install multi-tail if needed)

6.To uninstall

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
That user can now be assigned the appropriate permissions to operate the needed database.
You may need to create the user depending how you have previously setup weewx setup (the default is sqlite only, ie:-  no mysql).

<pre>
mysql -uroot -p
Enter password:

 [...]
 MariaDB [(none)]> CREATE USER 'weewx'@'localhost' IDENTIFIED BY 'weewx';
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
