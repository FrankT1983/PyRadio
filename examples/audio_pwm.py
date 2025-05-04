import RPi.GPIO as GPIO
import time

# Pin configuration
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

# Create PWM instances with a frequency of 1000 Hz
pwm1 = GPIO.PWM(18, 1000)
pwm2 = GPIO.PWM(13, 1000)

# Start PWM with a duty cycle of 50% (medium volume)
pwm1.start(20)
pwm2.start(20)

try:
    while True:
        # Gradually increase the volume
        for duty_cycle in range(0, 101, 5):
            pwm1.ChangeDutyCycle(duty_cycle)
            pwm2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)
        
        # Gradually decrease the volume
        for duty_cycle in range(100, -1, -5):
            pwm1.ChangeDutyCycle(duty_cycle)
            pwm2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)

except KeyboardInterrupt:
    # Stop PWM and clean up GPIO pins
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
