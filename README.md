# I5G-Tools

1.) Continuous Mode Loop Timer only affects Continuous mode and is the amount of time (in milliseconds) between WJ increments when the input is held
Similarly, Continuous Mode Initial Loop Timer is the amount of time (in milliseconds) between the initial input and the first time the WJ increments when the input is held. Setting this to be longer than Loop Timer gives you time to release the input if you only wanted to adjust the value by 1 (or the set increment value)

2.) A button, axis, or dpad input may be bound to as many functions as you want. The most obvious example would be binding the switch button for front bar and rear bar to the same button so you can switch the front and rear bars at the same time.

3.) The app will save your binds, axis thresholds, timers, increment mode per tab, and switch mode per tab. This app also supports saving and loading between several settings files, but for the time being you will have to copy and paste the settings.ini file and rename it. The only name requirement is that it ends in ".ini". The folder can be found in C:/Users/YourNameHere/AppData/Local/I5G Tools/

4.) The Pedal Axis in the Clutch and Throttle is intended to be your clutch and throttle pedals, respectively. Technically, the app will let you bind these to a button or dpad, but it won't work unless it's bound to an axis (a pedal, a trigger on a controller, etc.)

5.) The High Axis Threshold and Low Axis Threshold specify how far an axis needs to be moved in order for it to count as an input. The Low Axis Threshold can be set to any number between 1 and High Axis Threshold -1 and the High Axis Threshold can be set to any number between Low Axis Threshold +1 and 99. This affects any axis input that is bound, except for anything bound to Pedal Axis.

6.) Currently there is no deadzone applied to either end of a Pedal Axis. For example, if you wanted a 5% deadzone on the low side of your throttle pedal (or clutch pedal) because your throttle sometimes goes up from 0% to 3% by itself, there is currently no way to do that. If you have this problem, complain to Chris and he'll add it in.

7.) The value in the Switch box shown is always the secondary value. Normally this is helpful to show you what the other value you will be switching to is, but this is annoying/confusing when in Toggle Mode because if you are already at the secondary value, it will just show you what you're already at, instead of the primary value that it will next switch to.

8.) If you try to load a settings profile (either on startup or after the app has loaded) and a controller that is bound to an input is not detected, a window will pop up warning you this is the case. You can choose to proceed by pressing OK, but it will unbind everything associated with that controller and you must rebind everything on that controller when the controller is reconnected. If you don't want to deal with this, you can hit Cancel and the program will either close (if this is during startup) or revert to the last loaded settings file to give you time to plug in the controller before trying again.

9.) The Front and Rear Bars are coded for values 1 through 6 for the IR-18. However, the IL-15 only has 1 through 5, so if you use the app, the numbers won't exactly line up correct and you'll have to press increase 2 times to go from 3 to 4 (or somewhere around there). There are future plans to automatically detect the car and adjust the range accordingly. There are probably other cars that may have a similar issue, or also with Fuel Maps. Complain to Chris and/or Alexis if you run into this problem.

10.) Trying to edit values in the boxes by typing can be very annoying. This isn't getting improved unless there's a lot of complaining and an actual reason why this should be improved besides it's somewhat annoying.

11.) Axis Samples can be set between 2 and 10. Right now it's set to 2 and honestly probably never needs to be set higher. There may be weird behavior that occurs if this is set higher because higher values haven't been tested in any detail