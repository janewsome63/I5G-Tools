# I5G-Tools

1.) Continuous Mode Loop Timer only affects Continuous mode and is the amount of time (in milliseconds) between WJ increments when the input is held
Similarly, Continuous Mode Initial Loop Timer is the amount of time (in milliseconds) between the initial input and the first time the WJ increments when the input is held. Setting this to be longer than Loop Timer gives you time to release the input if you only wanted to adjust the value by 1 (or the set increment value)

2.) A button, axis, or dpad input may be bound to as many functions as you want. The most obvious example would be binding the switch button for front bar and rear bar to the same button so you can switch the front and rear bars at the same time.

3.) The app will save your binds, axis thresholds, timers, increment mode per tab, and switch mode per tab. This app also supports saving and loading between several settings files, but for the time being you will have to copy and paste the settings.ini file and rename it. The only name requirement is that it ends in ".ini". The folder can be found in C:/Users/YourNameHere/AppData/Local/I5G Tools/

4.) The Pedal Axis in the Clutch and Throttle is intended to be your clutch and throttle pedals, respectively. Technically, the app will let you bind these to a button or dpad, but it won't work unless it's bound to an axis (a pedal, a trigger on a controller, etc.)

5.) The High Axis Threshold and Low Axis Threshold specify how far an axis needs to be moved in order for it to count as an input. The Low Axis Threshold can be set to any number between 1 and High Axis Threshold -1 and the High Axis Threshold can be set to any number between Low Axis Threshold +1 and 99. This affects any axis input that is bound, except for anything bound to Pedal Axis.

6.) Currently there is no deadzone applied to either end of a Pedal Axis. For example, if you wanted a 5% deadzone on the low side of your throttle pedal (or clutch pedal) because your throttle sometimes goes up from 0% to 3% by itself, there is currently no way to do that. If you have this problem, complain to Chris and he'll add it in.

7.) Axis Samples can be set between 2 and 10. Right now it's set to 2 and honestly probably never needs to be set higher. There may be weird behavior that occurs if this is set higher because higher values haven't been tested in any detail