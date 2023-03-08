# SolarEdge-Battery-Optimiser
Optimises overnight battery charging based on the Solcast for the following day

***CODE NOT YET WORKING - CODE IS STILL IN DEVELOPMENT ISSUES STILL BEING RESOLVED***

As above, the purpose of this code is to charge the SolarEdge Battery Store overnight (00:30 to 04:30) when electricity is cheaper on the UK Octopus GO tariff, based on the Solcast for the following day.  As the 'window of intervention only lasts for four hours, the code calls for Solcast data and battery energy levels every 15 minutes during that time and adjusts the battery charge rate to match energy at the end of the period with the forecast energy usage (custom equation) and available solar energy, allowing for a user-defined buffer.

There are XX essential elemnts to the code:
  1) Forecast likely energy usage.  This is done using a bespoke equation based on previous electricity usage without solar panels.  It generates two values:
     a) The Maximum Daily usage, which varies by time of year (less in the summer, more in the winter), and
     b) Likely (average) cumulative usage throught the day, matching likely higher and lower usage rates
  2) Get solar PV forecast data from Solcast and convert it into data comparable with the likely energy usage
  3) Get the battery energy from the SolarEdge inverter via the SolarEdge TCP Modbus
  4) Calculate the battery charging rate to ensure the necessary battery energy to exceed the buffer until the next charging period (00:30 tomorrow)
  5) Change the SolarEdge inverter Energy Manager settings to either charge, not discharge, or maximize self-consuption.  THIS HAS NOT YET BEEN TESTED

At the moment, sections 1-5 have been tested in the current version of the code.  However, there is an issue when calling for TCP Modbus data after the first iteration.  I am not sure why this is.  Perhaps I need to close the TCP socket (shutdown & close), or perhaps there is another wayy to call the data without causing this issue - currently unclear why this error occurs

The code probably looks very basic because:
  a) it is!
  b) I'm totally new to Python
  c) I haven't written code of any kind (other than Excel formulae) for over 20 years
  
  Any thoughts/suggestions to improve the 'elegance', efficiency and usability of the code very much appreciated.
