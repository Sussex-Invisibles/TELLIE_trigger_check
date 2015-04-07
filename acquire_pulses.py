#!/usr/bin/env python
#########################
# acquire_pulses.py 
#
# Script to fire tellie (master mode), and read 
# both trig_out and light pulse at scope. 
#########################
try:
    from pyvisa.vpp43 import visa_library, visa_exceptions
    visa_library.load_library("/Library/Frameworks/Visa.framework/VISA") # Mac specific??
    import visa
except ImportError:
    print "No VISA/pyVISA software installed, cannot use VisaUSB"
import os
import time
import sys
import core.serial_command as serial_command
import common.comms_flags as comms_flags
import scopes
import scope_connections
import readPklWaveFile
import utils

if __name__=="__main__":
    script_time = time.time()

    # Save file
    fname = str(sys.argv[1])
    #print fname

    # No. Events
    no_events = 10001

    # TELLIE settings
    channel = 8
    box_no = 1
    logical_channel = (box_no-1)*8 + channel
    IPW = 7800
    height = 16383
    delay = 1 # ms -> 1 kHz
    fibre_delay = 0
    trigger_delay = 0
    pulse_number = 1

    # Set up serial connection
    sc = serial_command.SerialCommand("/dev/tty.usbserial-FTE3C0PG")
    sc.select_channel(logical_channel)
    sc.set_pulse_width(IPW)
    sc.set_pulse_height(height)
    sc.set_pulse_number(pulse_number)
    sc.set_pulse_delay(delay)
    sc.set_fibre_delay(fibre_delay)
    sc.set_trigger_delay(trigger_delay)

    # Set-up scope
    usb_conn = scope_connections.VisaUSB()
    tek_scope = scopes.Tektronix3000(usb_conn)
    tek_scope.unlock()
    tek_scope.set_single_acquisition() # Single signal acquisition mode
    trigger = 1 # Volts
    tek_scope.set_edge_trigger(trigger, 1, False) # Rising edge trigger 
    time.sleep(0.1)
    tek_scope.set_data_mode(4725, 5049)
    time.sleep(0.1)
    tek_scope.lock() # Re acquires the preamble  

    # Set-up results file
    results = utils.PickleFile(fname, 2)
    results.set_meta_data("timeform_1", tek_scope.get_timeform(1))
    results.set_meta_data("timeform_2", tek_scope.get_timeform(2))
    print tek_scope._get_preamble
    #results.set_meta_dict(tek_scope._get_preamble(1))       

    # Fire and save data
    time.sleep(0.1)
    loop_time = time.time()
    for i in range(no_events):
        if i==0: # Often first pulse doesn't fire correctly
            tek_scope.acquire(True) # Wait for triggered acquisition
            sc.fire()
            time.sleep(0.1)
            sc.fire()
            time.sleep(0.1)
        sc.fire()
        #time.sleep(0.1)
        tek_scope.acquire_time_check()
        try:
            results.add_data(tek_scope.get_waveform(1), 1)
            results.add_data(tek_scope.get_waveform(2), 2)
        except Exception, e:
            print "Scope died, acquisition lost..."
            print e
        if i % 100 == 0:
            print "%i events saved, this loop took: %i s" % (i, (time.time() - loop_time))
            loop_time = time.time() 
            sc.read_pin(logical_channel)
            sc.fire()
            time.sleep(0.1)
            sc.fire()
            time.sleep(0.1)
    sc.read_pin(logical_channel)
    tek_scope.unlock()
    results.save()
    results.close()
    print "########################################"
    print "%i response and trigger out signals saved to: %s" % (i, fname)
    print "Script took : %1.2f mins"%( (time.time() - script_time)/60 )
