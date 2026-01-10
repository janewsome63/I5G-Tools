# I5G-Tools

1.) The procedure to calibrate an axis into iRacing is as follows:
    A.) In iRacing, select the control you want to bind and select "Use rotary knob (analog or digital)".
    B.) In the I5G-Tools app, press the "Calibrate" button in the appropriate tab so it now says "<-Calibrating->" and sweeps back and forth.
    C.) In iRacing, hit "Next" and complete.
    D.) In the I5G-Tools app, press the "<-Calibrating->" button so it goes back to saying "Calibrate".

2.) A button, axis, or dpad input may be bound to as many functions as you want. The most obvious example would be binding the switch button for front bar and rear bar to the same button so you can switch the front and rear bars at the same time.

3.) The app will save your binds, axis thresholds, timers, increment mode per tab, and switch mode per tab. This app also supports saving and loading between several settings files, but for the time being you will have to copy and paste the settings.ini file and rename it. The only name requirement is that it ends in ".ini". The folder can be found in C:/Users/YourNameHere/AppData/Local/I5G Tools/

4.) The Pedal Axis in the Clutch and Throttle is intended to be your clutch and throttle pedals, respectively. Technically, the app will let you bind these to a button or dpad, but it won't work unless it's bound to an axis (a pedal, a trigger on a controller, etc.)

5.) The High Axis Threshold and Low Axis Threshold specify how far an axis needs to be moved in order for it to count as an input. The Low Axis Threshold can be set to any number between 1 and High Axis Threshold -1 and the High Axis Threshold can be set to any number between Low Axis Threshold +1 and 99. This affects any axis input that is bound, except for anything bound to Pedal Axis.

6.) Currently there is no deadzone applied to either end of a Pedal Axis. For example, if you wanted a 5% deadzone on the low side of your throttle pedal (or clutch pedal) because your throttle sometimes goes up from 0% to 3% by itself, there is currently no way to do that. If you have this problem, complain to Chris and he'll add it in.

7.) Continuous Mode Loop Timer only affects Continuous mode and is the amount of time (in milliseconds) between WJ increments when the input is held
Similarly, Continuous Mode Initial Loop Timer is the amount of time (in milliseconds) between the initial input and the first time the WJ increments when the input is held. Setting this to be longer than Loop Timer gives you time to release the input if you only wanted to adjust the value by 1 (or the set increment value)

8.) The value in the Switch box shown is always the secondary value. Normally this is helpful to show you what the other value you will be switching to is, but this is annoying/confusing when in Toggle Mode because if you are already at the secondary value, it will just show you what you're already at, instead of the primary value that it will next switch to.

9.) If you try to load a settings profile (either on startup or after the app has loaded) and a controller that is bound to an input is not detected, a window will pop up warning you this is the case. You can choose to proceed by pressing OK, but it will unbind everything associated with that controller and you must rebind everything on that controller when the controller is reconnected. If you don't want to deal with this, you can hit Cancel and the program will either close (if this is during startup) or revert to the last loaded settings file to give you time to plug in the controller before trying again.

10.) There can be a different range in iRacing for WJ, FARB, RARB, Fuel maps, etc., per car. For example, in the IR-18, FARB and RARB go between 1 and 6. In the IL-15, they go between 1 and 5. The Porsche 963 GTP FARB goes between 1-13 and the RARB goes between 1-16 in the rear. The I5G-Tools app automatically detects the car when the sim loads in and adjusts limits - although this only works for the IR-18, IL-15, and some GTP cars for now. In the Display tab, the WJ, FARB, RARB, and Fuel Map labels will turn red if the car detected does not have limits recorded - for example the IL-15 does not have WJ or Fuel Maps - or if the car detected has not been entered into the list or if not loaded into the sim. The red color denotes that the limits are leftover from whenever they were last set, which may be from another car or the defaults (the IR-18 limits). For convenience, the current limits for each axis are listed out in the top right.

11.) Trying to edit values in the boxes by typing can be very annoying. This isn't getting improved unless there's a lot of complaining and an actual reason why this should be improved besides it's somewhat annoying.

12.) Axis Samples can be set between 2 and 10. Right now it's set to 2 and honestly probably never needs to be set higher. There may be weird behavior that occurs if this is set higher because higher values haven't been tested in any detail
