# I5G-Tools

1.) Continuous Mode Loop Timer only affects Continuous mode and is the amount of time (in milliseconds) between WJ increments when the input is held
Similarly, Continuous Mode Initial Loop Timer is the amount of time (in milliseconds) between the initial input and the first time the WJ increments when the input is held. Setting this to be longer than Loop Timer gives you time to release the input if you only wanted to adjust the value by 1 (or the set increment value)

2.) Axis Samples can be set between 2 and 10. Right now it's set to 2 and honestly probably never needs to be set higher. There may be weird behavior that occurs if this is set higher because higher values haven't been tested in any detail
