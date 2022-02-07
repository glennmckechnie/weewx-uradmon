## forecast module for standard skin
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
##
## Australian Index Forecast panel
## Included in index.html.tmpl
##
## Depending of your location and XML file in skin.conf
## you will need to adjust this file in a few places
## From Responsive skin with all credits to Darryn Cape


#import dateutil.parser

#errorCatcher Echo

<div id='uradmon_widget' class="widget">
  <div class="widget_title">
   <a class="widget_control_left"
      onclick="toggle_widget('uradmon')">&diams;&nbsp;$gettext("Air Quality (uRADMonitor)")</a>
    &nbsp;
    <a class="widget_control"
      onclick="toggle_widget('uradmon')">&diams;</a>
  </div>
  <div class="widget_contents">
   <div id="uradmon_details">
   <p>
   $gettext("Environmental stats as provided by an")<br>
   <a href="$unit_link" target="_blank">$unit_model</a> $gettext("unit from uRADMonitor").
   </p><p class="footnote">
   <i>
   $gettext("Gamma radiation, formaldehyde, CO2"),<br>
   $gettext("tVOC Air quality + temperature"),<br>
   $gettext("barometric pressure, air humidity"),<br>
   $gettext("noise &amp; laser scattering sensor for")<br>
   $gettext("PM2.5 particulate matter").
   </i></p>
   <table>
   <tr><td colspan='2'><i>$gettext("Local Environmental Stats")</i></td></tr>
   <tr>
    <td>
    &nbsp;<img src="images/urad-favicon.ico" width="16" height="16" alt="">
    </td>
    <td>
    $gettext("Local") - <a href="index.html" target="_blank"> $unit_model $gettext("uRADMonitor")</a>
   </tr>

   <tr><td colspan='2'><i>$gettext("Stats from uRADMonitor site")</i></td></tr>
   <tr>
   <td>
   &nbsp;<img src="images/urad-favicon.ico" width="16" height="16" alt="">
   </td>
    <td>
     <a href="https://www.uradmonitor.com/?open=$unit_id" target="_blank">$gettext("uRAD Dashboard")</a>
    </td>
   </tr>

   <tr>
   <td>
   &nbsp;<img src="images/urad-favicon.ico" width="16" height="16" alt="">
   </td>
    <td>
     <a href="https://uradmonitor.com/tools/dashboard-04/?open=$unit_id" target="_blank">$gettext("uRAD Graphs")</a>
    </td>
   </tr>

   </table>
   </div>
  </div>
</div>

