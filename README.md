

# weewx-uradmon

**Update: 14 Feb 2022**

Output of uRADMonitor units is C&deg;, cpm, Pa, ppm, ug/m^3, volts
Add conversions for cpm to micro_sievert
Add Conversions for Pa to hPa, mbar, inHG, mmHg
Fix missing, b0rked en.conf entries

No release ... yet. Awaiting feedback!
Use the [master](https://github.com/glennmckechnie/weewx-uradmon/archive/refs/heads/master.zip) from the github repo.

Removed [[uradmon_mysql]] from install.py

If it is, required then add it manually...
```
[Databases]
    [[uradmon_mysql]]
        database_name = uradmon2
        database_type = MySQL
```


**Update: 05 Feb 2022**

Add languages to skin - currently available from master branch only - and it is a Work In Progress!

This version is tentatively released as [v0.2.7](https://github.com/glennmckechnie/weewx-uradmon/releases).
In truth the master will be the most uptodate.

Contributions welcomed!!
See [issue #5](https://github.com/glennmckechnie/weewx-uradmon/issues/5) for a rundown on what is required

**Update: Feb 2022**

It has been reworked to include (if I've done it correctly) the A, D and Industrial units. It will detect which type based on the 'type' id returned from a json query. Currently it recognizes an A3 (type 8), an A (types 5 & 1), an Industrial (type 14) and a D model (type 6). Any other types will fall through to a syslog ERROR message with their corresponding json output. With that output we should be able to incorporate that hardware version, hopefully without any issues.

This version is not backwards compatable with the 1.5 series as it uses a different database schema. It was a case of the user hand editing the uradmon.py script to select the appropriate schema, or just having a one size fits all database with all the known fields present. I chose that later method. That's not to say that the code/database can't be tweaked to accomadate the original method but there is no reason to upgrade an existing installation to this version of the software. Nothing will be gained by it as this version is about incorporating other models.
The database is now named 'uradmon2'. Just in case and because data is precious!

Now, I don't own these extra units. If something breaks I'll need quality debug information to fix it. I will definitely need the json output from your unit. That should be available in your syslog as if it runs without finding a suitable hook, it will politely print the output there.

index.html.tmpl will need modifying if you are using anything other than an A or A3 model. Not every field contains data and therefore needs to be individually checked. The latest A3 units no longer have cpm, or volts in their output - a huge change from the original.
skin.conf will also need adjusting for the extra database fields that become available with the Industrial and D models.
The weewx documentation should cover everything you need to know about configuring the skin.conf and index.html.tmpls. It should be your first port of call to learn about tweaking weewx.

If you have a problem you can't solve. Raise it as an issue on github or contact me directly. Github issues are best as it won't get lost plus everyone will know about it.

If you fix a problem, no matter how small, then also let me known so that I can update it here.



**Update: Jun 2020**

This version has been rolled up and released as [v0.1.5](https://github.com/glennmckechnie/weewx-uradmon/releases) and is the last in its line. It is was written for, and is best suited to the A3 units.

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
