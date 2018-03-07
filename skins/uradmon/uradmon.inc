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
      onclick="toggle_widget('uradmon')">&diams;&nbsp;Air Quality (uRADMonitor)</a>
    &nbsp;
    <a class="widget_control"
      onclick="toggle_widget('uradmon')">&diams;</a>
  </div>
  <div class="widget_contents">
   <div id="uradmon_details">
   <p>
   Environmental stats as provided by<br>
   an <a href="$unit_link" target="_blank">$unit_model</a> from uRADMonitor.
   </p><p class="footnote">
   <i>"Gamma radiation, formaldehyde, CO2,<br>
   tVOC Air quality +temperature,<br>
   barometric pressure, air humidity,<br>
   and a laser scattering sensor for<br>
   PM2.5 particulate matter.
   </i></p>
   <table>
   <tr><td  colspan='2'><i>Local Environmental Stats</i></td></tr>
   <tr>
   <td>
    &nbsp;<img src="images/urad-favicon.ico" width="16" height="16" alt="">
    </td>
    <td>
    Local - <a href="index.html" target="_blank"> uRADMonitor</a>
   </tr>

   <tr><td  colspan='2'><i>Stats from uRADMonitor site</i></td></tr>
   <tr>
   <td>
   &nbsp;<img src="images/urad-favicon.ico" width="16" height="16" alt="">
   </td>
    <td>
     <a href="https://www.uradmonitor.com/?open=$unit_id" target="_blank">uRAD Dashboard</a>
    </td>
   </tr>

   <tr>
   <td>
   &nbsp;<img src="images/urad-favicon.ico" width="16" height="16" alt="">
   </td>
    <td>
     <a href="https://uradmonitor.com/tools/dashboard-04/?open=$unit_id" target="_blank">uRAD Graphs</a>
    </td>
   </tr>

   </table>
   </div>
  </div>
</div>

