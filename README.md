

# weewx-uradmon


**Description**

This is a skin that integrates with [weewx](http://weewx.com) (weather station software) and provides

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

