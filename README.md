# GarageDoorOpener
TFLuna Raspi ensure that the garage door opens.

The first panel of my garage door bows out slightly.  Because of this.  When the garage door opens, it hits the header of the garage door opening.  Causing the garage door opener to stop.  I have to cycle the door several times to get it to open fully.  

Using the raspi and this TF Luna distance measure.  I hope to measure the opening of the garage door and when it stops, the pi will cycle to door until it opens fully.

Sudo code:
  * detect opening of the door
  * if not fully open
  * is the door still opening?
  * if door has stopped before fully open
  * cycle the door button
  * push once and the door starts to close
  * push again to stop the closing operation
  * push again to start the opening operation
  * go back to step 2



  