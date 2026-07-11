import functions as fn
import variables as var

import irsdk
import keyboard
import math

from time import sleep
from win32gui import GetWindowText, GetForegroundWindow

ir = irsdk.IRSDK()

def chat_write(text):
    finished = False
    while GetWindowText(GetForegroundWindow()) == "iRacing.com Simulator" and ir['IsOnTrack'] and not finished:
        # keyboard.send('t')
        ir.chat_command(1)
        sleep(0.05)
        keyboard.write("## " + str(text) + " ##")
        sleep(0.05)
        keyboard.send('enter')
        finished = True
    if not finished:
        ir.chat_command(3)

def check_connection():
    if var.status['ir']['connected'] and not (ir.is_initialized and ir.is_connected):
        ir.shutdown()
        var.status['ir']['connected'] = False
        return False
    elif not var.status['ir']['connected'] and ir.startup() and ir.is_initialized and ir.is_connected:
        #sleep(1.0)
        var.status['ir']['connected'] = True
        return True

def main():
    while True:
        if check_connection():
            print("<-------- iRacing Connected -------->") #temporary, make indicator
            
            # Detect user's driver id and determine if they are a spectator or spotter
            for idx in range(64, -2, -1):
                try:
                    if ir['DriverInfo']['Drivers'][idx]['UserID'] == ir['DriverInfo']['DriverUserID']:
                        if ir['DriverInfo']['Drivers'][idx]['IsSpectator'] == 1:
                            var.status['ir']['spectator'] = True
                        else:
                            var.status['ir']['spectator'] = False
                        var.telemetry['driver']['idx'] = idx
                        var.status['ir']['spotter'] = False
                        break
                    elif idx == -1:
                        var.telemetry['driver']['idx'] = ir['DriverInfo']['DriverCarIdx']
                        var.status['ir']['spotter'] = True
                except IndexError:
                    pass
                
            # Set static variables
            var.telemetry['car']['name'] = ir['DriverInfo']['Drivers'][var.telemetry['driver']['idx']]['CarPath']
            var.telemetry['fuel']['full'] = ir['DriverInfo']['DriverCarFuelMaxLtr'] #check this for less than 100% values
            var.telemetry['fuel']['limit'] = ir['DriverInfo']['DriverCarMaxFuelPct']
            var.telemetry['track']['length'] = float(ir['WeekendInfo']['TrackLength'].split()[0])
        elif check_connection() is False:
            print("<-------- iRacing Disconnected -------->") #temporary, make indicator
            
        init_loop = True
        while ir.is_connected:
            ir.freeze_var_buffer_latest()
            
            # Car
            var.telemetry['car']['garage'] = ir['IsInGarage']
            var.telemetry['car']['pitting'] = ir['PitstopActive']
            var.telemetry['car']['position'] = ir['LapDist']
            var.telemetry['car']['surface'] = ir['PlayerTrackSurface'] # (-1 = not_in_world, 0 = off_track, 1 = in stall, 2 = approaching_pits, 3 = on_track)

            # Driver
            var.telemetry['driver']['driving'] = ir['IsOnTrack']
            var.telemetry['driver']['lap']['completed'] = ir['LapCompleted']
            var.telemetry['driver']['lap']['dist'] = ir['LapDist']
            var.telemetry['driver']['lap']['pct'] = ir['LapDistPct']

            # Engine
            var.telemetry['engine']['oil'] = ir['OilTemp']
            var.telemetry['engine']['water'] = ir['WaterTemp']
            var.telemetry['engine']['temp_total'] = ir['OilTemp'] + ir['WaterTemp']

            # Flags
            var.telemetry['flags']['hex'] = ir['SessionFlags']

            # Fuel
            var.telemetry['fuel']['level'] = ir['FuelLevel']
            var.telemetry['fuel']['pct'] = ir['FuelLevelPct']

            # Tires
            var.telemetry['tires']['temp_total'] = 0.0
            var.telemetry['tires']['wear_total'] = 0.0
            for tire in var.telemetry['tires']:
                if tire != "temp_total" and tire != "wear_total":
                    for info in var.telemetry['tires'][tire]:
                        for section in var.telemetry['tires'][tire][info]:
                            if info == "temp":
                                unit = "C"
                            else:
                                unit = ""
                            var.telemetry['tires'][tire][info][section] = ir[tire.upper() + info + unit + section.upper()]
                            var.telemetry['tires'][info + '_total'] += ir[tire.upper() + info + unit + section.upper()]

            # Session
            var.telemetry['session']['lap']['remaining'] = ir['SessionLapsRemainEx']
            var.telemetry['session']['lap']['time'] = ir['LapLastLapTime']
            var.telemetry['session']['lap']['total'] = ir['SessionLapsTotal']
            var.telemetry['session']['state'] = ir['SessionState']
            var.telemetry['session']['time']['current'] = ir['SessionTime']
            var.telemetry['session']['time']['remaining'] = ir['SessionTimeRemain']
            var.telemetry['session']['time']['total'] = ir['SessionTimeTotal']
            var.telemetry['session']['type'] = ir['SessionInfo']['Sessions'][ir['SessionNum']]['SessionType']

            # Detect unit type
            if ir['DisplayUnits'] == 0:
                var.telemetry['units'] = "imperial"
            elif ir['DisplayUnits'] == 1:
                var.telemetry['units'] = "metric"

            # Update flags
            for item in var.codes['flags']:
                if var.telemetry['flags']['hex'] & var.codes['flags'][item] == var.codes['flags'][item]:
                    var.telemetry['flags']['list'].append(item)

            ir.unfreeze_var_buffer_latest()

            # Log distances for fn.direction (uneeded?)
            var.cache['distances'].append(var.telemetry['driver']['lap']['dist'])
            if len(var.cache['distances']) > 6:
                var.cache['distances'].pop(0)

            # Set cache values
            var.cache['lap']['pct_diff'] = var.telemetry['driver']['lap']['pct'] - var.cache['lap']['pct']
            var.cache['lap']['pct'] = var.telemetry['driver']['lap']['pct']

            if init_loop:
                init_loop = False
                fn.start_thread(triggers)
                fn.start_thread(statuses)

            sleep(var.settings['frequency'])
        sleep(var.settings['frequency'] * 4)
        
def statuses():
    init_loop = True
    while ir.is_connected:
        if init_loop:
            init_loop = False

        sleep(var.settings['frequency'])
        
def triggers():
    diff_prev = 0.0
    pct = 0.0
    pct_prev = pct
    sessiontime_prev = var.telemetry['session']['time']['current']
    ticks_prev = 0.1167
    fuel_prev = 0.0

    # Starting vars
    init_loop = True
    while ir.is_connected:
        # Check if lap has changed
        if var.telemetry['car']['surface'] != -1:
            if var.telemetry['driver']['lap']['completed'] < var.telemetry['driver']['lap']['next'] - 1 or var.telemetry['driver']['lap']['completed'] > var.telemetry['driver']['lap']['next'] + 1:
                var.telemetry['driver']['lap']['next'] = var.telemetry['driver']['lap']['completed'] + 1
            elif var.telemetry['driver']['lap']['completed'] == var.telemetry['driver']['lap']['next']:
                var.telemetry['driver']['lap']['next'] = var.telemetry['driver']['lap']['next'] + 1
                for section in var.triggers['lap']:
                    var.triggers['lap'][section] = True
                print("Lap")

        # Check if driving status changed
        if var.telemetry['driver']['driving'] and not var.cache['driving']:
            var.cache['driving'] = True
            if not init_loop:
                for section in var.triggers['driving']:
                    var.triggers['driving'][section] = True
                print("Driving")
        elif not var.telemetry['driver']['driving'] and var.cache['driving']:
            var.cache['driving'] = False

        # Check for car reset
        if var.cache['engine']['temp_total'] != 154.0 == var.telemetry['engine']['temp_total'] and var.cache['tires']['temp_total'] != var.telemetry['tires']['temp_total']:
            if not init_loop:
                for section in var.triggers['reset']:
                    var.triggers['reset'][section] = True
                print("Car Reset")

        # Check for active reset
        if "Offline Testing" in var.telemetry['session']['type'] and var.cache['lap']['pct_diff'] != diff_prev:
            if var.triggers['lap']['active_reset']:
                pct += 1.0 - math.fabs(var.cache['lap']['pct_diff'])
                var.triggers['lap']['active_reset'] = False
            elif not var.triggers['lap']['active_reset'] and 1.0 > var.cache['lap']['pct_diff'] > 0.5:
                pct += 1.0 - var.cache['lap']['pct_diff']
            else:
                pct += var.cache['lap']['pct_diff']
            pct_diff = pct - pct_prev
            pct_prev = pct
            sessiontime = var.telemetry['session']['time']['current']
            dist = pct_diff * var.telemetry['track']['length'] * 1000
            ticks = (sessiontime - sessiontime_prev)
            sessiontime_prev = sessiontime
            if ticks <= 0.0:
                ticks = ticks_prev
            ticks_prev = ticks
            speed = math.fabs(dist / ticks)
            if not var.triggers['reset']['active_reset']:
                if speed > 117.0 or not var.telemetry['car']['pitting'] and var.cache['fuel']['level_prev'] < var.telemetry['fuel']['level']:
                    for section in var.triggers['active_reset']:
                        var.triggers['active_reset'][section] = True
                    print("Active Reset")
            else:
                var.triggers['reset']['active_reset'] = False
        diff_prev = var.cache['lap']['pct_diff']

        # Set every-time cache values
        var.cache['engine']['oil'] = var.telemetry['engine']['oil']
        var.cache['engine']['water'] = var.telemetry['engine']['water']
        var.cache['engine']['temp_total'] = var.telemetry['engine']['temp_total']
        var.cache['fuel']['level_prev'] = var.telemetry['fuel']['level']
        var.cache['tires']['temp_total'] = var.telemetry['tires']['temp_total']

        if init_loop:
            init_loop = False

        sleep(var.settings['frequency'])