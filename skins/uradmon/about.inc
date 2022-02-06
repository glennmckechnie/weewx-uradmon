## about module for standard skin
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo

<div id='about_widget' class="widget">
  <div class="widget_title">
    <a class="widget_control_left"
      onclick="toggle_widget('about')">&diams;&nbsp;$gettext("About this weather station")</a>
        &nbsp;
    <a class="widget_control"
      onclick="toggle_widget('about')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>
    <tr>
      <td class="label">$gettext("Hardware")</td>
      <td class="data">$station.hardware</td>
    </tr>
    <tr>
      <td class="label">$gettext("Latitude")</td>
      <td class="data">$station.latitude[0]&deg; $station.latitude[1]' $station.latitude[2]</td>
    </tr>
    <tr>
      <td class="label">$gettext("Longitude")</td>
      <td class="data">$station.longitude[0]&deg; $station.longitude[1]' $station.longitude[2]</td>
    </tr>
    <tr>
      <td class="label">$gettext("Altitude")</td>
      <td class="data">$station.altitude</td>
    </tr>
    <tr>
      <td class="label">$gettext("Server uptime")</td>
      <td class="data">$station.os_uptime</td>
    </tr>
    <tr>
      <td class="label">$gettext("weeWX uptime")</td>
      <td class="data">$station.uptime</td>
    </tr>
    <tr>
      <td class="label">$gettext("weeWX version")</td>
      <td class="data">$station.version</td>
    </tr>
  </table>
  </div>

</div>
